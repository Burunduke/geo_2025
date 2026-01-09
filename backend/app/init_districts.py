"""
Скрипт для автоматической загрузки районов из OpenStreetMap при инициализации
"""
import logging
import time
import sys
from .database import SessionLocal
from .utils.osm_districts import import_osm_districts
from .cities_config import CITIES

logger = logging.getLogger(__name__)

def init_districts_from_osm():
    """
    Загрузить районы для всех городов из конфигурации
    """
    print("=" * 80)
    print("🌍 НАЧАЛО ИНИЦИАЛИЗАЦИИ РАЙОНОВ ИЗ OPENSTREETMAP")
    print("=" * 80)
    
    db = SessionLocal()
    try:
        # Импортируем районы только для приоритетных городов
        # Доступные города: voronezh, moscow, spb, ekaterinburg, kazan,
        #                   novosibirsk, nizhny_novgorod, samara, rostov, ufa
        # Для добавления города раскомментируйте его slug в списке ниже
        priority_cities = [
            'voronezh',      # Воронеж
            'moscow',      # Москва
            'spb',         # Санкт-Петербург
            # 'ekaterinburg', # Екатеринбург
            # 'kazan',       # Казань
            # 'novosibirsk', # Новосибирск
            # 'nizhny_novgorod', # Нижний Новгород
            # 'samara',      # Самара
            # 'rostov',      # Ростов-на-Дону
            # 'ufa',         # Уфа
        ]
        
        total_cities = len(priority_cities)
        processed_cities = 0
        total_stats = {
            'total': 0,
            'imported': 0,
            'updated': 0,
            'errors': 0
        }
        
        print(f"📋 План обработки: {total_cities} городов")
        print("-" * 80)
        
        for city_slug in priority_cities:
            if city_slug not in CITIES:
                continue
                
            processed_cities += 1
            city_info = CITIES[city_slug]
            city_name = city_info['name']
            
            print(f"\n🏙️  [{processed_cities}/{total_cities}] Обработка города: {city_name}")
            print("-" * 40)
            
            try:
                stats = import_osm_districts(
                    city=city_name,
                    country=city_info['country']
                )
                
                total_stats['total'] += stats['total']
                total_stats['imported'] += stats['imported']
                total_stats['updated'] += stats['updated']
                total_stats['errors'] += stats['errors']
                
                # Выводим детальную статистику по городу
                print(f"  ✅ Успешно обработано: {stats['imported']} районов")
                if stats['updated'] > 0:
                    print(f"  🔄 Обновлено: {stats['updated']} районов")
                if stats['errors'] > 0:
                    print(f"  ❌ Ошибок: {stats['errors']}")
                
                # Проверяем, были ли найдены районы
                if stats['total'] == 0:
                    print(f"  ⚠️  Внимание: районы не найдены (возможно, таймаут OSM API)")
                    total_stats['errors'] += 1
                
                # Добавляем задержку между городами, чтобы не перегружать OSM API
                if stats['imported'] > 0:
                    print(f"  ⏳ Пауза 5 секунд перед следующим городом...")
                    time.sleep(5)
                
            except Exception as e:
                print(f"  ❌ Ошибка при обработке города {city_name}: {e}")
                total_stats['errors'] += 1
                continue
        
        # Итоговая статистика
        print("\n" + "=" * 80)
        print("📊 ИТОГИ ОБРАБОТКИ:")
        print(f"  🏙️  Всего городов обработано: {processed_cities}/{total_cities}")
        print(f"  📍 Всего районов найдено: {total_stats['total']}")
        print(f"  ✅ Успешно импортировано: {total_stats['imported']}")
        print(f"  🔄 Обновлено: {total_stats['updated']}")
        print(f"  ❌ Ошибок: {total_stats['errors']}")
        
        if total_stats['imported'] + total_stats['updated'] > 0:
            print("\n🎉 Инициализация районов успешно завершена!")
        else:
            print("\n⚠️  Внимание: не удалось импортировать районы")
        
        print("=" * 80)
        
        # Записываем флаг завершения в файл для health check
        import os
        os.makedirs('/app/data', exist_ok=True)
        with open('/app/data/districts_initialized', 'w') as f:
            f.write('initialized')
        
    except Exception as e:
        print(f"\n❌ Критическая ошибка при инициализации районов: {e}")
        logger.error(f"Error during districts initialization: {e}", exc_info=True)
    finally:
        db.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_districts_from_osm()