from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from geoalchemy2.functions import ST_Distance, ST_DWithin, ST_AsGeoJSON, ST_MakePoint, ST_Within, ST_Buffer, ST_Intersects, ST_Area, ST_Transform, ST_SetSRID
from typing import List, Optional
import json
import logging
from ..database import get_db
from ..models import District, Event
from ..schemas import DistrictResponse
from ..utils.osm_districts import import_osm_districts

logger = logging.getLogger(__name__)

router = APIRouter()

# Получить все районы
@router.get("/", response_model=List[DistrictResponse])
def get_districts(db: Session = Depends(get_db)):
    """Получить все районы"""
    try:
        logger.info("Запрос на получение всех районов")
        
        districts = db.query(
            District.id,
            District.name,
            District.population,
            func.ST_AsGeoJSON(District.geom).label('geometry')
        ).all()
        
        logger.info(f"Найдено районов в БД: {len(districts)}")
        
        result = []
        errors = 0
        
        for d in districts:
            try:
                # Проверяем валидность геометрии
                if not d.geometry:
                    logger.warning(f"Район {d.name} (ID: {d.id}) имеет пустую геометрию")
                    errors += 1
                    continue
                
                # Проверяем, что геометрия - валидный JSON
                geometry = json.loads(d.geometry)
                
                # Проверяем базовую структуру GeoJSON
                if not isinstance(geometry, dict) or 'type' not in geometry or 'coordinates' not in geometry:
                    logger.warning(f"Район {d.name} (ID: {d.id}) имеет невалидную геометрию")
                    errors += 1
                    continue
                
                result.append(DistrictResponse(
                    id=d.id,
                    name=d.name,
                    population=d.population,
                    geometry=geometry
                ))
                
            except json.JSONDecodeError as e:
                logger.error(f"Ошибка парсинга геометрии для района {d.name} (ID: {d.id}): {e}")
                errors += 1
            except Exception as e:
                logger.error(f"Ошибка обработки района {d.name} (ID: {d.id}): {e}")
                errors += 1
        
        logger.info(f"Успешно обработано районов: {len(result)}, ошибок: {errors}")
        
        if errors > 0:
            logger.warning(f"При обработке районов возникло {errors} ошибок")
        
        return result
        
    except Exception as e:
        logger.error(f"Ошибка при получении районов: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении районов: {str(e)}"
        )

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

# Удаление всех районов
@router.delete("/clear")
async def clear_all_districts(db: Session = Depends(get_db)):
    """
    Удалить все районы из базы данных
    
    Returns:
        Количество удаленных районов
    """
    try:
        deleted_count = db.query(District).delete()
        db.commit()
        logger.info(f"Удалено районов: {deleted_count}")
        
        return {
            "success": True,
            "deleted_count": deleted_count
        }
    except Exception as e:
        logger.error(f"Ошибка удаления районов: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при удалении районов: {str(e)}"
        )

# Импорт районов из OpenStreetMap
@router.post("/import-osm")
async def import_districts_from_osm(
    city: str = Query("Воронеж", description="Название города"),
    country: str = Query("Россия", description="Название страны"),
    db: Session = Depends(get_db)
):
    """
    Импортировать границы районов из OpenStreetMap
    
    Args:
        city: Название города
        country: Название страны
        
    Returns:
        Статистика импорта
    """
    try:
        logger.info(f"Начат импорт районов для города {city}, {country}")
        
        # Импортируем районы
        stats = import_osm_districts(city=city, country=country)
        
        logger.info(f"Импорт завершен: {stats}")
        
        return {
            "success": True,
            "city": city,
            "country": country,
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Ошибка импорта районов: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при импорте районов: {str(e)}"
        )

# Проверка состояния районов
@router.get("/health")
async def check_districts_health(db: Session = Depends(get_db)):
    """
    Проверить состояние районов в базе данных
    
    Returns:
        Информация о количестве районов и их состоянии
    """
    try:
        # Общее количество районов
        total_count = db.query(District).count()
        
        # Количество районов с валидной геометрией
        valid_geom_count = db.query(District).filter(
            func.ST_IsValid(District.geom)
        ).count()
        
        # Количество районов с пустой геометрией
        null_geom_count = db.query(District).filter(
            District.geom.is_(None)
        ).count()
        
        # Получаем несколько примеров для проверки
        sample_districts = db.query(
            District.id,
            District.name,
            func.ST_AsGeoJSON(District.geom).label('geometry')
        ).limit(3).all()
        
        samples = []
        for d in sample_districts:
            try:
                geometry = json.loads(d.geometry) if d.geometry else None
                samples.append({
                    "id": d.id,
                    "name": d.name,
                    "has_geometry": geometry is not None,
                    "geometry_type": geometry.get("type") if geometry else None
                })
            except:
                samples.append({
                    "id": d.id,
                    "name": d.name,
                    "has_geometry": False,
                    "geometry_type": None,
                    "error": "Invalid JSON"
                })
        
        return {
            "total_districts": total_count,
            "valid_geometry": valid_geom_count,
            "null_geometry": null_geom_count,
            "health_status": "ok" if total_count > 0 and valid_geom_count > 0 else "error",
            "samples": samples
        }
        
    except Exception as e:
        logger.error(f"Ошибка проверки состояния районов: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при проверке состояния районов: {str(e)}"
        )