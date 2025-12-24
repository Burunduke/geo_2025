from sqlalchemy import Column, Integer, String, DateTime, Text
from geoalchemy2 import Geometry
from datetime import datetime
from .database import Base

class Object(Base):
    tablename = "objects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False, index=True)
    address = Column(String(255))
    geom = Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Event(Base):
    tablename = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    event_type = Column(String(50), nullable=False, index=True)
    description = Column(Text)
    geom = Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class District(Base):
    tablename = "districts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    population = Column(Integer)
    geom = Column(Geometry(geometry_type='POLYGON', srid=4326), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)