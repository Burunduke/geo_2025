from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from geoalchemy2.functions import ST_Distance, ST_DWithin, ST_AsGeoJSON, ST_MakePoint
from typing import List, Optional
from datetime import datetime, timedelta
import logging
from ..database import get_db
from ..models import Event
from ..schemas import EventResponse, EventCreate

logger = logging.getLogger(__name__)

router = APIRouter()

# Получить все события (устаревший endpoint - рекомендуется использовать /{city}/events)
@router.get("/events", response_model=List[EventResponse])
def get_events(
    event_type: Optional[str] = None,
    source: Optional[str] = None,
    active_only: Optional[bool] = False,
    upcoming_only: Optional[bool] = False,
    db: Session = Depends(get_db)
):
    """Получить все события с фильтрацией (устаревший - используйте /{city}/events)"""
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
    ).filter(Event.is_archived == False)
    
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
@router.post("/events", response_model=EventResponse)
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
        venue=event.venue,
        city='moscow'  # Временно, пока не будет передачи города в схеме
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
@router.get("/events/{event_id}", response_model=EventResponse)
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

# События в радиусе (устаревший endpoint - рекомендуется использовать /{city}/events/nearby)
@router.get("/events/nearby")
def get_nearby_events(
    lat: float = Query(...),
    lon: float = Query(...),
    radius: float = Query(1000, description="Радиус в метрах"),
    event_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Найти события в радиусе (устаревший - используйте /{city}/events/nearby)"""
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
        Event.is_archived == False,
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
@router.get("/events/filter/today")
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
@router.get("/events/filter/upcoming")
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

# Типы событий
@router.get("/events/types")
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

# Импорт событий из KudaGo
@router.post("/events/import/kudago")
async def import_kudago_events(
    city: str = Query("voronezh", description="Город для импорта"),
    categories: Optional[List[str]] = Query(None, description="Категории событий"),
    days_ahead: int = Query(30, description="Дней вперед"),
    limit: int = Query(500, description="Максимальное количество событий для импорта"),
    db: Session = Depends(get_db)
):
    """
    Импортировать события из KudaGo
    
    Параметры:
    - city: Город (voronezh, moscow, spb и т.д.)
    - categories: Список категорий (concert, theater, exhibition, sport, festival)
    - days_ahead: Количество дней вперед для импорта
    - limit: Максимальное количество событий (по умолчанию 500)
    """
    from ..scrapers.kudago import scrape_and_import_kudago_events
    from ..bot.realtime_notifications import send_realtime_notifications
    from ..bot import get_bot
    
    try:
        stats = scrape_and_import_kudago_events(
            city=city,
            categories=categories,
            days_ahead=days_ahead,
            limit=limit
        )
        # Calculate imported as created + updated
        imported = stats.get('created', 0) + stats.get('updated', 0)
        
        # Send notifications about new events
        new_event_ids = stats.get('new_event_ids', [])
        if new_event_ids:
            try:
                bot = get_bot()
                if bot:
                    await send_realtime_notifications(bot, new_event_ids)
                    logger.info(f"Sent notifications for {len(new_event_ids)} new events")
            except Exception as e:
                logger.error(f"Error sending notifications: {e}")
                # Don't fail the import if notifications fail
        
        return {
            "status": "success",
            "source": "kudago",
            "statistics": {
                **stats,
                "imported": imported
            },
            "message": f"Импортировано {imported} событий из KudaGo"
        }
    except Exception as e:
        logger.error(f"KudaGo import error: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка импорта из KudaGo: {str(e)}")

# Импорт событий из Яндекс.Афиши
@router.post("/events/import/yandex")
async def import_yandex_events(
    city: str = Query("voronezh", description="Город для импорта"),
    categories: Optional[List[str]] = Query(None, description="Категории событий"),
    days_ahead: int = Query(30, description="Дней вперед"),
    db: Session = Depends(get_db)
):
    """
    Импортировать события из Яндекс.Афиши
    
    Параметры:
    - city: Город (voronezh, moscow, spb и т.д.)
    - categories: Список категорий (concert, theater, exhibition, sport, festival)
    - days_ahead: Количество дней вперед для импорта
    """
    from ..scrapers.yandex_afisha import scrape_and_import_yandex_events
    from ..bot.realtime_notifications import send_realtime_notifications
    from ..bot import get_bot
    
    try:
        stats = scrape_and_import_yandex_events(
            city=city,
            categories=categories,
            days_ahead=days_ahead,
            limit_per_category=50
        )
        # Calculate imported as created + updated
        imported = stats.get('created', 0) + stats.get('updated', 0)
        
        # Send notifications about new events
        new_event_ids = stats.get('new_event_ids', [])
        if new_event_ids:
            try:
                bot = get_bot()
                if bot:
                    await send_realtime_notifications(bot, new_event_ids)
                    logger.info(f"Sent notifications for {len(new_event_ids)} new events")
            except Exception as e:
                logger.error(f"Error sending notifications: {e}")
                # Don't fail the import if notifications fail
        
        return {
            "status": "success",
            "source": "yandex_afisha",
            "statistics": {
                **stats,
                "imported": imported
            },
            "message": f"Импортировано {imported} событий из Яндекс.Афиши"
        }
    except Exception as e:
        logger.error(f"Yandex Afisha import error: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка импорта из Яндекс.Афиши: {str(e)}")

# Импорт тестовых данных для Москвы
@router.post("/events/import/test-moscow")
async def import_test_moscow_events(db: Session = Depends(get_db)):
    """
    Импортировать тестовые события для Москвы (для демонстрации)
    """
    import random
    from datetime import datetime, timedelta
    from ..bot.realtime_notifications import send_realtime_notifications
    from ..bot import get_bot
    
    # Moscow venues with real coordinates
    venues = [
        {"name": "Большой театр", "lat": 55.7603, "lon": 37.6186, "address": "Театральная пл., 1"},
        {"name": "Крокус Сити Холл", "lat": 55.8233, "lon": 37.4108, "address": "65-66 км МКАД"},
        {"name": "Лужники", "lat": 55.7153, "lon": 37.5531, "address": "Лужнецкая наб., 24"},
        {"name": "Третьяковская галерея", "lat": 55.7414, "lon": 37.6207, "address": "Лаврушинский пер., 10"},
        {"name": "Парк Горького", "lat": 55.7312, "lon": 37.6017, "address": "ул. Крымский Вал, 9"},
        {"name": "ВДНХ", "lat": 55.8304, "lon": 37.6278, "address": "пр-т Мира, 119"},
        {"name": "Зарядье", "lat": 55.7513, "lon": 37.6286, "address": "ул. Варварка, 6"},
    ]
    
    # Event templates by category
    event_templates = {
        'concert': [
            "Концерт классической музыки",
            "Рок-концерт",
            "Джазовый вечер",
            "Симфонический оркестр",
            "Концерт популярной музыки"
        ],
        'theater': [
            "Спектакль 'Вишневый сад'",
            "Комедия 'Ревизор'",
            "Драма 'Три сестры'",
            "Мюзикл 'Чикаго'",
            "Детский спектакль"
        ],
        'exhibition': [
            "Выставка современного искусства",
            "Фотовыставка",
            "Выставка живописи",
            "Историческая экспозиция",
            "Выставка скульптуры"
        ],
        'sport': [
            "Футбольный матч",
            "Баскетбольная игра",
            "Хоккейный матч",
            "Волейбольный турнир",
            "Легкоатлетические соревнования"
        ],
        'festival': [
            "Городской фестиваль",
            "Фестиваль уличной еды",
            "Музыкальный фестиваль",
            "Фестиваль искусств",
            "Культурный фестиваль"
        ]
    }
    
    imported = 0
    errors = 0
    new_event_ids = []
    
    for category, templates in event_templates.items():
        for i, template in enumerate(templates):
            try:
                venue = random.choice(venues)
                days_offset = random.randint(1, 30)
                start_time = datetime.now() + timedelta(days=days_offset, hours=random.randint(10, 20))
                
                # Check for duplicates
                existing = db.query(Event).filter(
                    Event.title == f"{template} (тест)",
                    Event.source == 'manual',
                    func.date(Event.start_time) == func.date(start_time)
                ).first()
                
                if existing:
                    continue
                
                new_event = Event(
                    title=f"{template} (тест)",
                    event_type=category,
                    description=f"Тестовое событие для демонстрации. {template} в {venue['name']}.",
                    geom=func.ST_SetSRID(func.ST_MakePoint(venue['lon'], venue['lat']), 4326),
                    start_time=start_time,
                    end_time=start_time + timedelta(hours=2),
                    source='manual',
                    source_url=None,
                    image_url=None,
                    price=random.choice(['Бесплатно', 'от 500 ₽', '300-800 ₽', 'от 1000 ₽', '1500-3000 ₽']),
                    venue=venue['name'],
                    city='moscow'
                )
            
                db.add(new_event)
                db.flush()  # Get the ID
                new_event_ids.append(new_event.id)
                db.commit()
                imported += 1
                
            except Exception as e:
                logger.error(f"Error importing test event: {e}")
                db.rollback()
                errors += 1
    
    # Send notifications about new events
    if new_event_ids:
        try:
            bot = get_bot()
            if bot:
                await send_realtime_notifications(bot, new_event_ids)
                logger.info(f"Sent notifications for {len(new_event_ids)} new test events")
        except Exception as e:
            logger.error(f"Error sending notifications: {e}")
            # Don't fail the import if notifications fail
    
    return {
        "status": "success",
        "source": "manual",
        "statistics": {
            "total": len([t for templates in event_templates.values() for t in templates]),
            "imported": imported,
            "duplicates": 0,
            "errors": errors,
            "new_event_ids": new_event_ids
        },
        "message": f"Импортировано {imported} тестовых событий для Москвы"
    }

# Импорт тестовых данных для Санкт-Петербурга
@router.post("/events/import/test-spb")
async def import_test_spb_events(db: Session = Depends(get_db)):
    """
    Импортировать тестовые события для Санкт-Петербурга (для демонстрации)
    """
    import random
    from datetime import datetime, timedelta
    from ..bot.realtime_notifications import send_realtime_notifications
    from ..bot import get_bot
    
    # Saint Petersburg venues with real coordinates
    venues = [
        {"name": "Мариинский театр", "lat": 59.9259, "lon": 30.2967, "address": "Театральная пл., 1"},
        {"name": "Эрмитаж", "lat": 59.9398, "lon": 30.3146, "address": "Дворцовая наб., 34"},
        {"name": "Петропавловская крепость", "lat": 59.9504, "lon": 30.3164, "address": "Петропавловская крепость, 3"},
        {"name": "Исаакиевский собор", "lat": 59.9341, "lon": 30.3061, "address": "Исаакиевская пл., 4"},
        {"name": "Газпром Арена", "lat": 59.9726, "lon": 30.2214, "address": "Футбольная аллея, 1"},
        {"name": "БКЗ Октябрьский", "lat": 59.9291, "lon": 30.3195, "address": "Лиговский пр., 6"},
        {"name": "Летний сад", "lat": 59.9453, "lon": 30.3356, "address": "Летний сад"},
    ]
    
    # Event templates by category
    event_templates = {
        'concert': [
            "Концерт симфонического оркестра",
            "Рок-фестиваль",
            "Джазовый концерт",
            "Концерт классической музыки",
            "Вечер романсов"
        ],
        'theater': [
            "Балет 'Лебединое озеро'",
            "Опера 'Евгений Онегин'",
            "Спектакль 'Горе от ума'",
            "Мюзикл 'Анна Каренина'",
            "Драма 'Вишневый сад'"
        ],
        'exhibition': [
            "Выставка импрессионистов",
            "Современное искусство",
            "Фотовыставка 'Петербург'",
            "Выставка русской живописи",
            "Историческая экспозиция"
        ],
        'sport': [
            "Футбольный матч Зенит",
            "Хоккейный матч СКА",
            "Баскетбольная игра",
            "Волейбольный турнир",
            "Легкоатлетические соревнования"
        ],
        'festival': [
            "Фестиваль 'Белые ночи'",
            "Фестиваль уличной еды",
            "Музыкальный фестиваль",
            "Фестиваль искусств",
            "День города"
        ]
    }
    
    imported = 0
    errors = 0
    new_event_ids = []
    
    for category, templates in event_templates.items():
        for i, template in enumerate(templates):
            try:
                venue = random.choice(venues)
                days_offset = random.randint(1, 30)
                start_time = datetime.now() + timedelta(days=days_offset, hours=random.randint(10, 20))
                
                # Check for duplicates
                existing = db.query(Event).filter(
                    Event.title == f"{template} (тест)",
                    Event.source == 'manual',
                    func.date(Event.start_time) == func.date(start_time)
                ).first()
                
                if existing:
                    continue
                
                new_event = Event(
                    title=f"{template} (тест)",
                    event_type=category,
                    description=f"Тестовое событие для демонстрации. {template} в {venue['name']}.",
                    geom=func.ST_SetSRID(func.ST_MakePoint(venue['lon'], venue['lat']), 4326),
                    start_time=start_time,
                    end_time=start_time + timedelta(hours=2),
                    source='manual',
                    source_url=None,
                    image_url=None,
                    price=random.choice(['Бесплатно', 'от 500 ₽', '300-800 ₽', 'от 1000 ₽', '1500-3000 ₽']),
                    venue=venue['name'],
                    city='spb'
                )
            
                db.add(new_event)
                db.flush()  # Get the ID
                new_event_ids.append(new_event.id)
                db.commit()
                imported += 1
                
            except Exception as e:
                logger.error(f"Error importing test event: {e}")
                db.rollback()
                errors += 1
    
    # Send notifications about new events
    if new_event_ids:
        try:
            bot = get_bot()
            if bot:
                await send_realtime_notifications(bot, new_event_ids)
                logger.info(f"Sent notifications for {len(new_event_ids)} new test events")
        except Exception as e:
            logger.error(f"Error sending notifications: {e}")
            # Don't fail the import if notifications fail
    
    return {
        "status": "success",
        "source": "manual",
        "statistics": {
            "total": len([t for templates in event_templates.values() for t in templates]),
            "imported": imported,
            "duplicates": 0,
            "errors": errors,
            "new_event_ids": new_event_ids
        },
        "message": f"Импортировано {imported} тестовых событий для Санкт-Петербурга"
    }

# Новые endpoints с поддержкой городов

# Получить события для конкретного города
@router.get("/{city}/events", response_model=List[EventResponse])
def get_city_events(
    city: str,
    event_type: Optional[str] = None,
    upcoming_only: Optional[bool] = None,
    bounds: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Получить события для конкретного города"""
    # Проверить, что город существует в конфигурации
    from ..cities_config import CITIES
    if city not in CITIES:
        raise HTTPException(status_code=404, detail=f"Город '{city}' не найден")
    
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
        Event.city == city,
        Event.is_archived == False
    )
    
    # Фильтр по видимой области карты
    if bounds:
        try:
            north, south, east, west = map(float, bounds.split(','))
            query = query.filter(
                func.ST_Within(
                    Event.geom,
                    func.ST_MakeEnvelope(west, south, east, north, 4326)
                )
            )
        except ValueError:
            pass  # Невалидные bounds - игнорируем
    
    if upcoming_only is True:
        query = query.filter(Event.start_time > datetime.utcnow())
    
    if event_type:
        query = query.filter(Event.event_type == event_type)
    
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

# События в радиусе для конкретного города
@router.get("/{city}/events/nearby")
def get_city_nearby_events(
    city: str,
    lat: float = Query(...),
    lon: float = Query(...),
    radius: float = Query(1000, description="Радиус в метрах"),
    event_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Найти события в радиусе для конкретного города"""
    # Проверить, что город существует в конфигурации
    from ..cities_config import CITIES
    if city not in CITIES:
        raise HTTPException(status_code=404, detail=f"Город '{city}' не найден")
    
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
        Event.city == city,
        Event.is_archived == False,
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
        "city": city,
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