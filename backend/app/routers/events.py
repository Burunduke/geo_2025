from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from geoalchemy2.functions import ST_Distance, ST_DWithin, ST_AsGeoJSON, ST_MakePoint
from typing import List, Optional
from ..database import get_db
from ..models import Event, Object, District
from ..schemas import EventResponse, EventCreate

router = APIRouter()

# Получить все события
@router.get("/", response_model=List[EventResponse])
def get_events(
    event_type: Optional[str] = None,
    active_only: Optional[bool] = False,
    db: Session = Depends(get_db)
):
    """Получить все события с опциональной фильтрацией по типу"""
    query = db.query(
        Event.id,
        Event.title,
        Event.event_type,
        Event.description,
        func.ST_X(Event.geom).label('lon'),
        func.ST_Y(Event.geom).label('lat'),
        Event.start_time,
        Event.end_time,
        Event.created_at
    )
    
    if event_type:
        query = query.filter(Event.event_type == event_type)
    
    if active_only:
        from datetime import datetime
        query = query.filter(
            Event.start_time <= datetime.utcnow(),
            (Event.end_time >= datetime.utcnow()) | (Event.end_time.is_(None))
        )
    
    events = query.all()
    
    return [
        EventResponse(
            id=evt.id,
            title=evt.title,
            event_type=evt.event_type,
            description=evt.description,
            lat=evt.lat,
            lon=evt.lon,
            start_time=evt.start_time,
            end_time=evt.end_time,
            created_at=evt.created_at
        )
        for evt in events
    ]

# Создать новое событие
@router.post("/", response_model=EventResponse)
def create_event(
    event: EventCreate,
    db: Session = Depends(get_db)
):
    """Создать новое событие"""
    new_event = Event(
        title=event.title,
        event_type=event.event_type,
        description=event.description,
        geom=func.ST_SetSRID(func.ST_MakePoint(event.lon, event.lat), 4326),
        start_time=event.start_time,
        end_time=event.end_time
    )
    
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    
    return EventResponse(
        id=new_event.id,
        title=new_event.title,
        event_type=new_event.event_type,
        description=new_event.description,
        lat=event.lat,
        lon=event.lon,
        start_time=new_event.start_time,
        end_time=new_event.end_time,
        created_at=new_event.created_at
    )

# События в радиусе
@router.get("/nearby")
def get_nearby_events(
    lat: float = Query(...),
    lon: float = Query(...),
    radius: float = Query(1000, description="Радиус в метрах"),
    event_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Найти события в радиусе"""
    user_point = func.ST_SetSRID(func.ST_MakePoint(lon, lat), 4326)
    
    query = db.query(
        Event.id,
        Event.title,
        Event.event_type,
        Event.description,
        func.ST_X(Event.geom).label('lon'),
        func.ST_Y(Event.geom).label('lat'),
        Event.start_time,
        Event.end_time,
        func.ST_Distance(
            func.ST_Transform(Event.geom, 3857),
            func.ST_Transform(user_point, 3857)
        ).label('distance')
    ).filter(
        func.ST_DWithin(
            func.ST_Transform(Event.geom, 3857),
            func.ST_Transform(user_point, 3857),
            radius
        )
    )
    
    if event_type:
        query = query.filter(Event.event_type == event_type)
    
    results = query.order_by(text('distance')).all()
    
    return {
        "count": len(results),
        "events": [
            {
                "id": evt.id,
                "title": evt.title,
                "event_type": evt.event_type,
                "description": evt.description,
                "lat": evt.lat,
                "lon": evt.lon,
                "start_time": evt.start_time,
                "end_time": evt.end_time,
                "distance": round(evt.distance, 2)
            }
            for evt in results
        ]
    }

# Типы событий
@router.get("/types")
def get_event_types(db: Session = Depends(get_db)):
    """Получить список типов событий"""
    types = db.query(
        Event.event_type,
        func.count(Event.id).label('count')
    ).group_by(Event.event_type).all()
    
    return [
        {"type": t[0], "count": t[1]}
        for t in types
    ]