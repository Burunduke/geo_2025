from sqlalchemy import Column, Integer, String, DateTime, Text, BigInteger, ForeignKey, Boolean
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
    source_url = Column(String(500))
    image_url = Column(String(500))
    price = Column(String(100))
    venue = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

class District(Base):
    __tablename__ = "districts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    population = Column(Integer)
    geom = Column(Geometry(geometry_type='POLYGON', srid=4326), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

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
    
    # Relationships
    subscriptions = relationship("UserSubscription", back_populates="user", cascade="all, delete-orphan")

class UserSubscription(Base):
    __tablename__ = "user_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("telegram_users.id", ondelete="CASCADE"), nullable=False)
    district_id = Column(Integer, ForeignKey("districts.id", ondelete="CASCADE"), nullable=False)
    notification_time = Column(String(5), default="09:00")  # HH:MM format
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("TelegramUser", back_populates="subscriptions")
    district = relationship("District")