from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class EventBase(BaseModel):
    title: str
    event_type: str
    description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None

class EventCreate(EventBase):
    lat: float
    lon: float
    source: Optional[str] = "manual"
    source_url: Optional[str] = None
    image_url: Optional[str] = None
    price: Optional[str] = None
    venue: Optional[str] = None

class EventResponse(EventBase):
    id: int
    lat: float
    lon: float
    source: Optional[str] = None
    source_url: Optional[str] = None
    image_url: Optional[str] = None
    price: Optional[str] = None
    venue: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class NearbyEventsRequest(BaseModel):
    lat: float
    lon: float
    radius: float  # в метрах
    event_type: Optional[str] = None

class TelegramUserBase(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class TelegramUserCreate(TelegramUserBase):
    chat_id: int

class TelegramUserResponse(TelegramUserBase):
    id: int
    chat_id: int
    is_active: bool
    created_at: datetime
    last_interaction: datetime
    
    class Config:
        from_attributes = True
