"""
Скрипт для автоматической загрузки районов из OpenStreetMap при инициализации
"""
import logging
import time
from .database import SessionLocal
from .utils.osm_districts import import_osm_districts
from .cities_config import CITIES

logger = logging.getLogger(__name__)

def init_districts_from_osm():
    """
    Загрузить районы для всех городов из конфигурации
    """
    logger.info("Starting districts initialization from OpenStreetMap...")
    
    db = SessionLocal()
    try:
        # Проверяем, есть ли уже районы в БД
        from .models import District
        existing_count = db.query(District).count()
        
        if existing_count > 0:
            logger.info(f"Districts already exist in database ({existing_count} districts). Skipping initialization.")
            return
        
        logger.info("No districts found. Starting import from OpenStreetMap...")
        
        total_stats = {
            'total': 0,
            'imported': 0,
            'updated': 0,
            'errors': 0
        }
        
        # Импортируем районы только для приоритетных городов
        # Доступные города: voronezh, moscow, spb, ekaterinburg, kazan,
        #                   novosibirsk, nizhny_novgorod, samara, rostov, ufa
        # Для добавления города раскомментируйте его slug в списке ниже
        priority_cities = [
            'voronezh',      # Воронеж
            # 'moscow',      # Москва
            # 'spb',         # Санкт-Петербург
            # 'ekaterinburg', # Екатеринбург
            # 'kazan',       # Казань
            # 'novosibirsk', # Новосибирск
            # 'nizhny_novgorod', # Нижний Новгород
            # 'samara',      # Самара
            # 'rostov',      # Ростов-на-Дону
            # 'ufa',         # Уфа
        ]
        
        for city_slug in priority_cities:
            if city_slug not in CITIES:
                continue
                
            city_info = CITIES[city_slug]
            city_name = city_info['name']
            logger.info(f"Importing districts for {city_name}...")
            
            try:
                stats = import_osm_districts(
                    city=city_name,
                    country=city_info['country']
                )
                
                total_stats['total'] += stats['total']
                total_stats['imported'] += stats['imported']
                total_stats['updated'] += stats['updated']
                total_stats['errors'] += stats['errors']
                
                logger.info(f"  {city_name}: imported={stats['imported']}, errors={stats['errors']}")
                
                # Добавляем задержку между городами, чтобы не перегружать OSM API
                if stats['imported'] > 0:
                    time.sleep(5)
                
            except Exception as e:
                logger.error(f"Error importing districts for {city_name}: {e}")
                total_stats['errors'] += 1
                continue
        
        logger.info(f"Districts initialization completed: {total_stats}")
        
    except Exception as e:
        logger.error(f"Error during districts initialization: {e}", exc_info=True)
    finally:
        db.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_districts_from_osm()