from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import objects, events, districts

app = FastAPI(
    title="City Geo API",
    description="API для работы с городской инфраструктурой и событиями",
    version="1.0.0"
)

# CORS для работы с frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(objects.router, prefix="/api/objects", tags=["Объекты"])
app.include_router(events.router, prefix="/api/events", tags=["События"])
app.include_router(districts.router, prefix="/api/districts", tags=["Районы"])

@app.get("/")
def read_root():
    return {
        "message": "City Geo API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}