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

class UserSubscriptionBase(BaseModel):
    district_id: int
    notification_time: str = "09:00"

class UserSubscriptionCreate(UserSubscriptionBase):
    user_id: int

class UserSubscriptionResponse(UserSubscriptionBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class SubscriptionWithDistrict(BaseModel):
    id: int
    district_id: int
    district_name: str
    notification_time: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True