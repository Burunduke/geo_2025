from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ObjectBase(BaseModel):
    name: str
    type: str
    address: Optional[str] = None

class ObjectCreate(ObjectBase):
    lat: float
    lon: float

class ObjectResponse(ObjectBase):
    id: int
    lat: float
    lon: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class EventBase(BaseModel):
    title: str
    event_type: str
    description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None

class EventCreate(EventBase):
    lat: float
    lon: float

class EventResponse(EventBase):
    id: int
    lat: float
    lon: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class DistrictResponse(BaseModel):
    id: int
    name: str
    population: Optional[int]
    geometry: dict  # GeoJSON
    
    class Config:
        from_attributes = True

class NearbyObjectsRequest(BaseModel):
    lat: float
    lon: float
    radius: float  # в метрах
    object_type: Optional[str] = None