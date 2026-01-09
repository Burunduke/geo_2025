from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from .routers import events, districts
from .bot import start_bot, stop_bot
from .cities_config import get_all_cities

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown"""
    # Startup
    logger.info("Starting application...")
    
    # Initialize districts from OSM if needed - now blocking startup
    try:
        from .init_districts import init_districts_from_osm
        logger.info("Starting districts initialization (blocking)...")
        init_districts_from_osm()
        logger.info("Districts initialization completed")
    except Exception as e:
        logger.error(f"Failed to initialize districts: {e}")
    
    try:
        await start_bot()
        logger.info("Telegram bot started")
    except Exception as e:
        logger.error(f"Failed to start Telegram bot: {e}")
        logger.warning("Application will continue without bot functionality")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    try:
        await stop_bot()
        logger.info("Telegram bot stopped")
    except Exception as e:
        logger.error(f"Error stopping Telegram bot: {e}")

app = FastAPI(
    title="City Geo API",
    description="API для работы с городской инфраструктурой и событиями",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router, prefix="/api/events", tags=["События"])
app.include_router(districts.router, prefix="/api/districts", tags=["Районы"])

@app.get("/")
def read_root():
    return {
        "message": "City Geo API",
        "version": "1.0.0",
        "docs": "/docs",
        "telegram_bot": "active"
    }

@app.get("/health")
def health_check():
    """Check application health including districts status"""
    try:
        from .database import SessionLocal
        from .models import District
        from sqlalchemy import func
        import os
        
        # Check if initialization flag file exists
        init_flag_path = '/app/data/districts_initialized'
        districts_initialized = os.path.exists(init_flag_path)
        
        db = SessionLocal()
        try:
            # Check districts count
            total_districts = db.query(District).count()
            valid_districts = db.query(District).filter(
                func.ST_IsValid(District.geom)
            ).count()
            
            # Only mark as ready if both conditions are met:
            # 1. Initialization process completed (flag file exists)
            # 2. We have valid districts in database
            districts_ready = districts_initialized and total_districts > 0 and valid_districts > 0
            
            return {
                "status": "healthy",
                "districts": {
                    "total": total_districts,
                    "valid": valid_districts,
                    "ready": districts_ready,
                    "initialized": districts_initialized
                }
            }
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "districts": {
                "total": 0,
                "valid": 0,
                "ready": False,
                "initialized": False
            }
        }

@app.get("/api/cities")
def get_cities():
    """Получить список доступных городов"""
    return {
        "cities": get_all_cities()
    }