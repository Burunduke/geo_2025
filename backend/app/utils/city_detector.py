"""
Утилита для определения города по координатам
"""
from ..cities_config import CITIES

def detect_city_by_coordinates(lat: float, lon: float) -> str:
    """
    Определить город по координатам
    
    Args:
        lat: Широта
        lon: Долгота
        
    Returns:
        Строка с slug города (например, 'moscow', 'voronezh')
    """
    closest_city = None
    min_distance = float('inf')
    
    for city_slug, city_info in CITIES.items():
        city_lat = city_info['lat']
        city_lon = city_info['lon']
        
        # Простое евклидово расстояние (для демонстрации)
        # В реальном проекте можно использовать более точные алгоритмы
        distance = ((lat - city_lat) ** 2 + (lon - city_lon) ** 2) ** 0.5
        
        if distance < min_distance:
            min_distance = distance
            closest_city = city_slug
    
    return closest_city or 'voronezh'  # fallback

def migrate_existing_events(db):
    """
    Мигрировать существующие события - определить город по координатам
    
    Args:
        db: Сессия базы данных
    """
    from ..models import Event
    from sqlalchemy import text
    
    # Получить все существующие события
    events = db.query(Event).all()
    
    migrated = 0
    errors = 0
    
    for event in events:
        try:
            # Получить координаты события
            result = db.execute(
                text("SELECT ST_Y(geom) as lat, ST_X(geom) as lon FROM events WHERE id = :id"),
                {"id": event.id}
            ).first()
            
            if result and result.lat and result.lon:
                city = detect_city_by_coordinates(result.lat, result.lon)
                
                # Обновить город
                db.execute(
                    text("UPDATE events SET city = :city, last_updated = CURRENT_TIMESTAMP WHERE id = :id"),
                    {"city": city, "id": event.id}
                )
                
                migrated += 1
                print(f"Мигрировано событие {event.id}: {event.title} -> {city}")
            else:
                print(f"Событие {event.id}: не удалось получить координаты")
                errors += 1
                
        except Exception as e:
            print(f"Ошибка миграции события {event.id}: {e}")
            errors += 1
            continue
    
    db.commit()
    print(f"Миграция завершена: {migrated} успешно, {errors} ошибок")
    
    return migrated, errors

if __name__ == "__main__":
    # Тестирование функции определения города
    test_coordinates = [
        (55.7558, 37.6173),  # Москва
        (59.9343, 30.3351),  # Санкт-Петербург
        (51.6606, 39.2003),  # Воронеж
        (56.8389, 60.6057),  # Екатеринбург
    ]
    
    for lat, lon in test_coordinates:
        city = detect_city_by_coordinates(lat, lon)
        print(f"Координаты ({lat}, {lon}) -> город: {city}")