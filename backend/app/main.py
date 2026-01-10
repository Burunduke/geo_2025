from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from .routers import events
from .bot import start_bot, stop_bot
from .cities_config import get_all_cities

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown"""
    # Startup
    logger.info("Starting application...")
    
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

app.include_router(events.router, prefix="/api", tags=["События"])

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
    """Check application health"""
    return {
        "status": "healthy",
        "districts": {
            "ready": True,
            "initialized": True
        }
    }

@app.get("/api/cities")
def get_cities():
    """Получить список доступных городов"""
    return {
        "cities": get_all_cities()
    }