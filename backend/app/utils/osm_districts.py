"""
OpenStreetMap Districts Importer
Импортирует границы районов города из OpenStreetMap
"""
import requests
import logging
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import District
from ..database import SessionLocal

logger = logging.getLogger(__name__)


class OSMDistrictsImporter:
    """
    Импортер границ районов из OpenStreetMap
    """
    
    OVERPASS_API = "https://overpass-api.de/api/interpreter"
    NOMINATIM_API = "https://nominatim.openstreetmap.org"
    
    def __init__(self, city: str = "Воронеж", country: str = "Россия"):
        """
        Инициализация импортера
        
        Args:
            city: Название города
            country: Название страны
        """
        self.city = city
        self.country = country
        self.headers = {
            'User-Agent': 'CityGeoApp/1.0 (city events mapping application)'
        }
    
    def get_city_districts(self) -> List[Dict]:
        """
        Получить список районов города из OpenStreetMap
        
        Returns:
            Список словарей с информацией о районах
        """
        # Упрощенный запрос для поиска районов
        overpass_query = f"""
        [out:json][timeout:60];
        area[name="{self.city}"]->.city;
        (
          relation["boundary"="administrative"]["admin_level"~"^(8|9|10)$"](area.city);
        );
        out geom;
        """
        
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Запрос районов для города {self.city} (попытка {attempt + 1}/{max_retries})")
                
                response = requests.post(
                    self.OVERPASS_API,
                    data={'data': overpass_query},
                    headers=self.headers,
                    timeout=60
                )
                
                if response.status_code == 504:
                    logger.warning(f"Timeout от Overpass API, повтор через {retry_delay} сек...")
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(retry_delay)
                        continue
                    else:
                        logger.error("Превышено количество попыток")
                        return []
                
                if response.status_code != 200:
                    logger.error(f"Ошибка Overpass API: {response.status_code}")
                    return []
                
                data = response.json()
                districts = []
                
                for element in data.get('elements', []):
                    if element.get('type') == 'relation':
                        district = self._parse_district(element)
                        if district:
                            districts.append(district)
                
                logger.info(f"Найдено районов: {len(districts)}")
                return districts
                
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout при запросе, повтор через {retry_delay} сек...")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay)
                    continue
                else:
                    logger.error("Превышено количество попыток")
                    return []
            except Exception as e:
                logger.error(f"Ошибка при получении районов: {e}", exc_info=True)
                return []
        
        return []
    
    def _parse_district(self, element: Dict) -> Optional[Dict]:
        """
        Парсинг данных района из элемента OSM
        
        Args:
            element: Элемент из ответа Overpass API
            
        Returns:
            Словарь с данными района или None
        """
        try:
            tags = element.get('tags', {})
            name = tags.get('name') or tags.get('name:ru')
            
            if not name:
                return None
            
            # Получаем геометрию
            geometry = self._extract_geometry(element)
            if not geometry:
                return None
            
            # Пытаемся получить население
            population = self._parse_population(tags.get('population'))
            
            return {
                'name': name,
                'geometry': geometry,
                'population': population,
                'osm_id': element.get('id'),
                'admin_level': tags.get('admin_level')
            }
            
        except Exception as e:
            logger.error(f"Ошибка парсинга района: {e}")
            return None
    
    def _extract_geometry(self, element: Dict) -> Optional[Dict]:
        """
        Извлечение геометрии из элемента OSM
        
        Args:
            element: Элемент из ответа Overpass API
            
        Returns:
            GeoJSON геометрия или None
        """
        try:
            members = element.get('members', [])
            
            # Ищем outer ways (внешние границы)
            outer_ways = [m for m in members if m.get('role') == 'outer']
            
            if not outer_ways:
                return None
            
            # Собираем координаты из всех outer ways
            coordinates = []
            for way in outer_ways:
                way_coords = []
                for node in way.get('geometry', []):
                    way_coords.append([node['lon'], node['lat']])
                
                if way_coords:
                    coordinates.append(way_coords)
            
            if not coordinates:
                return None
            
            # Формируем GeoJSON Polygon
            return {
                'type': 'Polygon',
                'coordinates': coordinates
            }
            
        except Exception as e:
            logger.error(f"Ошибка извлечения геометрии: {e}")
            return None
    
    def _parse_population(self, pop_str: Optional[str]) -> Optional[int]:
        """
        Парсинг населения из строки
        
        Args:
            pop_str: Строка с населением
            
        Returns:
            Число или None
        """
        if not pop_str:
            return None
        
        try:
            # Убираем пробелы и другие символы
            pop_str = pop_str.replace(' ', '').replace(',', '')
            return int(pop_str)
        except:
            return None
    
    def import_to_db(self, districts: List[Dict], db: Session = None) -> Dict:
        """
        Импорт районов в базу данных
        
        Args:
            districts: Список районов для импорта
            db: Сессия базы данных
            
        Returns:
            Статистика импорта
        """
        if db is None:
            db = SessionLocal()
            close_db = True
        else:
            close_db = False
        
        try:
            stats = {
                'total': len(districts),
                'imported': 0,
                'updated': 0,
                'errors': 0
            }
            
            for district_data in districts:
                try:
                    name = district_data['name']
                    
                    # Проверяем, существует ли район
                    existing = db.query(District).filter(
                        District.name == name
                    ).first()
                    
                    if existing:
                        # Обновляем существующий район
                        if district_data.get('population'):
                            existing.population = district_data['population']
                        
                        # Обновляем геометрию
                        geometry = district_data['geometry']
                        existing.geom = func.ST_GeomFromGeoJSON(str(geometry).replace("'", '"'))
                        
                        db.commit()
                        stats['updated'] += 1
                        logger.info(f"Обновлен район: {name}")
                    else:
                        # Создаем новый район
                        geometry = district_data['geometry']
                        
                        new_district = District(
                            name=name,
                            population=district_data.get('population'),
                            geom=func.ST_GeomFromGeoJSON(str(geometry).replace("'", '"'))
                        )
                        
                        db.add(new_district)
                        db.commit()
                        stats['imported'] += 1
                        logger.info(f"Импортирован район: {name}")
                        
                except Exception as e:
                    logger.error(f"Ошибка импорта района {district_data.get('name')}: {e}")
                    db.rollback()
                    stats['errors'] += 1
                    continue
            
            logger.info(f"Импорт завершен: {stats}")
            return stats
            
        finally:
            if close_db:
                db.close()


def import_osm_districts(city: str = "Воронеж", country: str = "Россия") -> Dict:
    """
    Удобная функция для импорта районов из OSM
    
    Args:
        city: Название города
        country: Название страны
        
    Returns:
        Статистика импорта
    """
    importer = OSMDistrictsImporter(city=city, country=country)
    districts = importer.get_city_districts()
    
    if not districts:
        logger.warning("Районы не найдены")
        return {
            'total': 0,
            'imported': 0,
            'updated': 0,
            'errors': 0
        }
    
    stats = importer.import_to_db(districts)
    logger.info(f"Импорт районов завершен: {stats}")
    return stats