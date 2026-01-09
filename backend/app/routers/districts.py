from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from geoalchemy2.functions import ST_Distance, ST_DWithin, ST_AsGeoJSON, ST_MakePoint, ST_Within, ST_Buffer, ST_Intersects, ST_Area, ST_Transform, ST_SetSRID
from typing import List, Optional
import json
from ..database import get_db
from ..models import District, Event
from ..schemas import DistrictResponse
from ..utils.osm_districts import import_osm_districts

router = APIRouter()

# Получить все районы
@router.get("/", response_model=List[DistrictResponse])
def get_districts(db: Session = Depends(get_db)):
    """Получить все районы"""
    districts = db.query(
        District.id,
        District.name,
        District.population,
        func.ST_AsGeoJSON(District.geom).label('geometry')
    ).all()
    
    return [
        DistrictResponse(
            id=d.id,
            name=d.name,
            population=d.population,
            geometry=json.loads(d.geometry)
        )
        for d in districts
    ]

# Найти район по точке
@router.get("/find")
def find_district_by_point(
    lat: float = Query(..., description="Широта"),
    lon: float = Query(..., description="Долгота"),
    db: Session = Depends(get_db)
):
    """Определить, в каком районе находится точка"""
    user_point = func.ST_SetSRID(func.ST_MakePoint(lon, lat), 4326)
    
    district = db.query(District).filter(
        func.ST_Contains(District.geom, user_point)
    ).first()
    
    if not district:
        raise HTTPException(status_code=404, detail="Точка не принадлежит ни одному району")
    
    return {
        "id": district.id,
        "name": district.name,
        "population": district.population
    }

# События в районе
@router.get("/{district_id}/events")
def get_events_in_district(
    district_id: int,
    event_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Получить все события в районе"""
    district = db.query(District).filter(District.id == district_id).first()
    
    if not district:
        raise HTTPException(status_code=404, detail="Район не найден")
    
    query = db.query(
        Event.id,
        Event.title,
        Event.event_type,
        Event.description,
        func.ST_X(Event.geom).label('lon'),
        func.ST_Y(Event.geom).label('lat'),
        Event.start_time,
        Event.end_time
    ).filter(
        func.ST_Within(Event.geom, district.geom)
    )
    
    if event_type:
        query = query.filter(Event.event_type == event_type)
    
    events = query.all()
    
    return {
        "district": district.name,
        "count": len(events),
        "events": [
            {
                "id": evt.id,
                "title": evt.title,
                "event_type": evt.event_type,
                "description": evt.description,
                "lat": evt.lat,
                "lon": evt.lon,
                "start_time": evt.start_time,
                "end_time": evt.end_time
            }
            for evt in events
        ]
    }

# Статистика по району
@router.get("/{district_id}/stats")
def get_district_stats(district_id: int, db: Session = Depends(get_db)):
    """Получить статистику по району"""
    district = db.query(District).filter(District.id == district_id).first()
    
    if not district:
        raise HTTPException(status_code=404, detail="Район не найден")
    
    # Подсчет событий по типам
    event_stats = db.query(
        Event.event_type,
        func.count(Event.id).label('count')
    ).filter(
        func.ST_Within(Event.geom, district.geom)
    ).group_by(Event.event_type).all()
    
    # Площадь района
    area = db.query(
        func.ST_Area(func.ST_Transform(district.geom, 3857)) / 1000000
    ).scalar()
    
    return {
        "district": district.name,
        "population": district.population,
        "area_km2": round(area, 2),
        "events": {t[0]: t[1] for t in event_stats},
        "total_events": sum(t[1] for t in event_stats)
    }

# Буферная зона вокруг района
@router.get("/{district_id}/buffer")
def get_district_buffer(
    district_id: int,
    radius: float = Query(500, description="Радиус буфера в метрах"),
    db: Session = Depends(get_db)
):
    """Получить буферную зону вокруг района"""
    district = db.query(District).filter(District.id == district_id).first()
    
    if not district:
        raise HTTPException(status_code=404, detail="Район не найден")
    
    buffer = db.query(
        func.ST_AsGeoJSON(
            func.ST_Transform(
                func.ST_Buffer(
                    func.ST_Transform(district.geom, 3857),
                    radius
                ),
                4326
            )
        )
    ).scalar()
    
    return {
        "district": district.name,
        "buffer_radius": radius,
        "geometry": json.loads(buffer)
    }

# Пересечение районов с объектами в радиусе
@router.get("/intersect")
def get_districts_intersecting_point(
    lat: float = Query(...),
    lon: float = Query(...),
    radius: float = Query(1000, description="Радиус в метрах"),
    db: Session = Depends(get_db)
):
    """Найти районы, пересекающиеся с буфером вокруг точки"""
    user_point = func.ST_SetSRID(func.ST_MakePoint(lon, lat), 4326)
    buffer = func.ST_Buffer(func.ST_Transform(user_point, 3857), radius)
    
    districts = db.query(
        District.id,
        District.name,
        District.population,
        func.ST_AsGeoJSON(District.geom).label('geometry')
    ).filter(
        func.ST_Intersects(
            func.ST_Transform(District.geom, 3857),
            buffer
        )
    ).all()
    
    return {
        "count": len(districts),
        "districts": [
            {
                "id": d.id,
                "name": d.name,
                "population": d.population,
                "geometry": json.loads(d.geometry)
            }
            for d in districts
        ]
    }