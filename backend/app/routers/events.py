from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from geoalchemy2.functions import ST_Distance, ST_DWithin, ST_AsGeoJSON, ST_MakePoint
from typing import List, Optional
from datetime import datetime, timedelta
from ..database import get_db
from ..models import Event, District
from ..schemas import EventResponse, EventCreate

router = APIRouter()

# Получить все события
@router.get("/", response_model=List[EventResponse])
def get_events(
    event_type: Optional[str] = None,
    source: Optional[str] = None,
    active_only: Optional[bool] = False,
    upcoming_only: Optional[bool] = False,
    db: Session = Depends(get_db)
):
    """Получить все события с фильтрацией"""
    query = db.query(
        Event.id,
        Event.title,
        Event.event_type,
        Event.description,
        func.ST_X(Event.geom).label('lon'),
        func.ST_Y(Event.geom).label('lat'),
        Event.start_time,
        Event.end_time,
        Event.source,
        Event.source_url,
        Event.image_url,
        Event.price,
        Event.venue,
        Event.created_at
    )
    
    if event_type:
        query = query.filter(Event.event_type == event_type)
    
    if source:
        query = query.filter(Event.source == source)
    
    if active_only:
        now = datetime.utcnow()
        query = query.filter(
            Event.start_time <= now,
            (Event.end_time >= now) | (Event.end_time.is_(None))
        )
    
    if upcoming_only:
        query = query.filter(Event.start_time > datetime.utcnow())
    
    events = query.order_by(Event.start_time).all()
    
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
            source=evt.source,
            source_url=evt.source_url,
            image_url=evt.image_url,
            price=evt.price,
            venue=evt.venue,
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
        end_time=event.end_time,
        source=event.source or 'manual',
        source_url=event.source_url,
        image_url=event.image_url,
        price=event.price,
        venue=event.venue
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
        source=new_event.source,
        source_url=new_event.source_url,
        image_url=new_event.image_url,
        price=new_event.price,
        venue=new_event.venue,
        created_at=new_event.created_at
    )

# Получить событие по ID
@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    """Получить детали события по ID"""
    event = db.query(
        Event.id,
        Event.title,
        Event.event_type,
        Event.description,
        func.ST_X(Event.geom).label('lon'),
        func.ST_Y(Event.geom).label('lat'),
        Event.start_time,
        Event.end_time,
        Event.source,
        Event.source_url,
        Event.image_url,
        Event.price,
        Event.venue,
        Event.created_at
    ).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return EventResponse(
        id=event.id,
        title=event.title,
        event_type=event.event_type,
        description=event.description,
        lat=event.lat,
        lon=event.lon,
        start_time=event.start_time,
        end_time=event.end_time,
        source=event.source,
        source_url=event.source_url,
        image_url=event.image_url,
        price=event.price,
        venue=event.venue,
        created_at=event.created_at
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

# События сегодня
@router.get("/filter/today")
def get_today_events(db: Session = Depends(get_db)):
    """Получить события на сегодня"""
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    events = db.query(
        Event.id,
        Event.title,
        Event.event_type,
        Event.description,
        func.ST_X(Event.geom).label('lon'),
        func.ST_Y(Event.geom).label('lat'),
        Event.start_time,
        Event.end_time,
        Event.source,
        Event.source_url,
        Event.image_url,
        Event.price,
        Event.venue,
        Event.created_at
    ).filter(
        Event.start_time >= today_start,
        Event.start_time < today_end
    ).order_by(Event.start_time).all()
    
    return {
        "date": today_start.date().isoformat(),
        "count": len(events),
        "events": [
            EventResponse(
                id=evt.id,
                title=evt.title,
                event_type=evt.event_type,
                description=evt.description,
                lat=evt.lat,
                lon=evt.lon,
                start_time=evt.start_time,
                end_time=evt.end_time,
                source=evt.source,
                source_url=evt.source_url,
                image_url=evt.image_url,
                price=evt.price,
                venue=evt.venue,
                created_at=evt.created_at
            )
            for evt in events
        ]
    }

# Предстоящие события
@router.get("/filter/upcoming")
def get_upcoming_events(
    days: int = Query(7, description="Количество дней вперед"),
    limit: int = Query(50, description="Максимальное количество событий"),
    db: Session = Depends(get_db)
):
    """Получить предстоящие события"""
    now = datetime.utcnow()
    future_date = now + timedelta(days=days)
    
    events = db.query(
        Event.id,
        Event.title,
        Event.event_type,
        Event.description,
        func.ST_X(Event.geom).label('lon'),
        func.ST_Y(Event.geom).label('lat'),
        Event.start_time,
        Event.end_time,
        Event.source,
        Event.source_url,
        Event.image_url,
        Event.price,
        Event.venue,
        Event.created_at
    ).filter(
        Event.start_time > now,
        Event.start_time <= future_date
    ).order_by(Event.start_time).limit(limit).all()
    
    return {
        "period": f"next_{days}_days",
        "count": len(events),
        "events": [
            EventResponse(
                id=evt.id,
                title=evt.title,
                event_type=evt.event_type,
                description=evt.description,
                lat=evt.lat,
                lon=evt.lon,
                start_time=evt.start_time,
                end_time=evt.end_time,
                source=evt.source,
                source_url=evt.source_url,
                image_url=evt.image_url,
                price=evt.price,
                venue=evt.venue,
                created_at=evt.created_at
            )
            for evt in events
        ]
    }

# События в районе
@router.get("/by-district/{district_id}")
def get_events_by_district(
    district_id: int,
    upcoming_only: bool = Query(False),
    db: Session = Depends(get_db)
):
    """Получить события в конкретном районе"""
    district = db.query(District).filter(District.id == district_id).first()
    if not district:
        raise HTTPException(status_code=404, detail="District not found")
    
    query = db.query(
        Event.id,
        Event.title,
        Event.event_type,
        Event.description,
        func.ST_X(Event.geom).label('lon'),
        func.ST_Y(Event.geom).label('lat'),
        Event.start_time,
        Event.end_time,
        Event.source,
        Event.source_url,
        Event.image_url,
        Event.price,
        Event.venue,
        Event.created_at
    ).filter(
        func.ST_Within(Event.geom, District.geom),
        District.id == district_id
    )
    
    if upcoming_only:
        query = query.filter(Event.start_time > datetime.utcnow())
    
    events = query.order_by(Event.start_time).all()
    
    return {
        "district_id": district_id,
        "district_name": district.name,
        "count": len(events),
        "events": [
            EventResponse(
                id=evt.id,
                title=evt.title,
                event_type=evt.event_type,
                description=evt.description,
                lat=evt.lat,
                lon=evt.lon,
                start_time=evt.start_time,
                end_time=evt.end_time,
                source=evt.source,
                source_url=evt.source_url,
                image_url=evt.image_url,
                price=evt.price,
                venue=evt.venue,
                created_at=evt.created_at
            )
            for evt in events
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

# Импорт событий с Яндекс.Афиши
@router.post("/import-afisha")
def import_afisha_events(
    city: str = Query("voronezh", description="Город для импорта"),
    categories: Optional[List[str]] = Query(None, description="Категории событий"),
    days_ahead: int = Query(30, description="Дней вперед"),
    limit_per_category: int = Query(50, description="Лимит на категорию"),
    geocoder_api_key: Optional[str] = Query(None, description="API ключ Yandex Geocoder"),
    db: Session = Depends(get_db)
):
    """
    Импортировать события с Яндекс.Афиши
    
    Параметры:
    - city: Город (voronezh, moscow, spb и т.д.)
    - categories: Список категорий (concert, theatre, exhibition, sport, festival)
    - days_ahead: Количество дней вперед для импорта
    - limit_per_category: Максимум событий на категорию
    - geocoder_api_key: API ключ для геокодирования адресов (опционально)
    """
    from ..scrapers.yandex_afisha import scrape_and_import_yandex_events
    
    try:
        stats = scrape_and_import_yandex_events(
            city=city,
            categories=categories,
            geocoder_api_key=geocoder_api_key,
            days_ahead=days_ahead,
            limit_per_category=limit_per_category
        )
        
        return {
            "status": "success",
            "message": f"Импорт завершен: {stats['imported']} событий добавлено",
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при импорте событий: {str(e)}"
        )