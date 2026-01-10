from sqlalchemy import Column, Integer, String, DateTime, Text, BigInteger, ForeignKey, Boolean, Time
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from datetime import datetime
from .database import Base

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    event_type = Column(String(50), nullable=False, index=True)
    description = Column(Text)
    geom = Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime)
    source = Column(String(50), default='manual', index=True)  # yandex_afisha, manual, telegram
    source_id = Column(String(100), index=True)  # Уникальный ID из источника
    source_url = Column(String(500))
    image_url = Column(String(500))
    price = Column(String(100))
    venue = Column(String(255))
    city = Column(String(50), nullable=False, index=True)  # Город события
    last_updated = Column(DateTime, default=datetime.utcnow)  # Время последнего обновления
    created_at = Column(DateTime, default=datetime.utcnow)
    is_archived = Column(Boolean, default=False)  # Мягкое удаление

class TelegramUser(Base):
    __tablename__ = "telegram_users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    chat_id = Column(BigInteger, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_interaction = Column(DateTime, default=datetime.utcnow)
    
    # Notification preferences
    notifications_enabled = Column(Boolean, default=False)
    notification_radius = Column(Integer, default=5000)  # Radius in meters
    user_location = Column(Geometry(geometry_type='POINT', srid=4326))
    preferred_city = Column(String(50))
    
    # Event type preferences (JSON string)
    preferred_event_types = Column(Text)  # JSON array as string
    
    # Notification settings
    notify_on_import = Column(Boolean, default=True)
    quiet_hours_start = Column(Time)
    quiet_hours_end = Column(Time)

class NotificationHistory(Base):
    __tablename__ = "notification_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('telegram_users.id', ondelete='CASCADE'), nullable=False)
    event_id = Column(Integer, ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)
    notification_type = Column(String(50), default='new_event')
    
    # Relationships
    user = relationship("TelegramUser")
    event = relationship("Event")