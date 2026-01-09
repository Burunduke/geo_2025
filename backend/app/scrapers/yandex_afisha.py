"""
Yandex Afisha Scraper
Scrapes events from Yandex Afisha for a specific city
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import re
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import Event, District
from ..database import SessionLocal

logger = logging.getLogger(__name__)

class YandexAfishaScraper:
    """
    Scraper for Yandex Afisha events
    
    Note: Yandex Afisha structure may change. This is a basic implementation
    that may need adjustments based on the actual website structure.
    """
    
    def __init__(self, city: str = "voronezh"):
        """
        Initialize scraper for a specific city
        
        Args:
            city: City name in URL format (e.g., 'voronezh', 'moscow', 'spb')
        """
        self.city = city
        self.base_url = f"https://afisha.yandex.ru/{city}"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def scrape_events(self, categories: Optional[List[str]] = None) -> List[Dict]:
        """
        Scrape events from Yandex Afisha
        
        Args:
            categories: List of categories to scrape (e.g., ['concert', 'theatre', 'exhibition'])
                       If None, scrapes all categories
        
        Returns:
            List of event dictionaries
        """
        if categories is None:
            categories = ['concert', 'theatre', 'exhibition', 'sport']
        
        all_events = []
        
        for category in categories:
            try:
                logger.info(f"Scraping {category} events from Yandex Afisha")
                events = self._scrape_category(category)
                all_events.extend(events)
                logger.info(f"Found {len(events)} {category} events")
            except Exception as e:
                logger.error(f"Error scraping {category}: {e}")
                continue
        
        return all_events
    
    def _scrape_category(self, category: str) -> List[Dict]:
        """
        Scrape events for a specific category
        
        Note: This is a simplified implementation. The actual Yandex Afisha
        structure may require different parsing logic.
        """
        url = f"{self.base_url}/{category}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return []
        
        soup = BeautifulSoup(response.content, 'lxml')
        events = []
        
        # This is a placeholder parsing logic
        # The actual selectors need to be adjusted based on Yandex Afisha's current structure
        event_cards = soup.find_all('div', class_='event-card')  # Adjust selector
        
        for card in event_cards:
            try:
                event = self._parse_event_card(card, category)
                if event:
                    events.append(event)
            except Exception as e:
                logger.error(f"Error parsing event card: {e}")
                continue
        
        return events
    
    def _parse_event_card(self, card, category: str) -> Optional[Dict]:
        """
        Parse individual event card
        
        Note: Selectors are placeholders and need to be adjusted
        """
        try:
            # Extract event details (adjust selectors based on actual HTML)
            title_elem = card.find('h3', class_='event-title')  # Adjust
            title = title_elem.text.strip() if title_elem else None
            
            if not title:
                return None
            
            # Extract date and time
            date_elem = card.find('div', class_='event-date')  # Adjust
            date_str = date_elem.text.strip() if date_elem else None
            
            # Extract location/address
            location_elem = card.find('div', class_='event-location')  # Adjust
            location = location_elem.text.strip() if location_elem else None
            
            # Extract description
            desc_elem = card.find('div', class_='event-description')  # Adjust
            description = desc_elem.text.strip() if desc_elem else None
            
            # Parse date (this is simplified, needs proper date parsing)
            start_time = self._parse_date(date_str) if date_str else datetime.now()
            
            # Try to extract coordinates from location (if available)
            # This is a placeholder - actual implementation would need geocoding
            lat, lon = self._geocode_location(location) if location else (None, None)
            
            return {
                'title': title,
                'event_type': self._map_category_to_type(category),
                'description': description,
                'location': location,
                'lat': lat,
                'lon': lon,
                'start_time': start_time,
                'source': 'yandex_afisha',
                'source_url': card.get('href', '')  # Adjust
            }
        
        except Exception as e:
            logger.error(f"Error parsing event card: {e}")
            return None
    
    def _parse_date(self, date_str: str) -> datetime:
        """
        Parse date string to datetime
        
        This is a simplified implementation. Needs to handle various date formats.
        """
        # Common patterns in Russian date formats
        patterns = [
            r'(\d{1,2})\s+(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)',
            r'(\d{1,2})\.(\d{1,2})\.(\d{4})',
            r'сегодня',
            r'завтра'
        ]
        
        # Handle "today" and "tomorrow"
        if 'сегодня' in date_str.lower():
            return datetime.now().replace(hour=19, minute=0, second=0, microsecond=0)
        elif 'завтра' in date_str.lower():
            return (datetime.now() + timedelta(days=1)).replace(hour=19, minute=0, second=0, microsecond=0)
        
        # Try to parse other formats
        # This is simplified - real implementation needs more robust parsing
        try:
            # Try standard format
            return datetime.strptime(date_str, '%d.%m.%Y')
        except:
            # Default to tomorrow evening if parsing fails
            return (datetime.now() + timedelta(days=1)).replace(hour=19, minute=0, second=0, microsecond=0)
    
    def _geocode_location(self, location: str) -> tuple:
        """
        Convert location string to coordinates
        
        This is a placeholder. Real implementation would use:
        - Yandex Geocoder API
        - Google Geocoding API
        - Or extract coordinates if they're in the HTML
        """
        # Default coordinates for Voronezh city center
        default_coords = (51.6605, 39.2005)
        
        # In a real implementation, you would:
        # 1. Use Yandex Geocoder API
        # 2. Cache results to avoid repeated API calls
        # 3. Handle API errors gracefully
        
        return default_coords
    
    def _map_category_to_type(self, category: str) -> str:
        """Map Yandex Afisha category to our event type"""
        mapping = {
            'concert': 'concert',
            'theatre': 'theater',
            'exhibition': 'exhibition',
            'sport': 'sport',
            'cinema': 'cinema',
            'festival': 'festival'
        }
        return mapping.get(category, 'festival')
    
    def import_events_to_db(self, events: List[Dict], db: Session = None) -> Dict:
        """
        Import scraped events to database with deduplication
        
        Returns:
            Dictionary with import statistics
        """
        if db is None:
            db = SessionLocal()
            close_db = True
        else:
            close_db = False
        
        try:
            stats = {
                'total': len(events),
                'imported': 0,
                'duplicates': 0,
                'errors': 0
            }
            
            for event_data in events:
                try:
                    # Skip events without coordinates
                    if not event_data.get('lat') or not event_data.get('lon'):
                        logger.warning(f"Skipping event without coordinates: {event_data.get('title')}")
                        stats['errors'] += 1
                        continue
                    
                    # Check for duplicates (same title, similar date, similar location)
                    existing = db.query(Event).filter(
                        Event.title == event_data['title'],
                        func.date(Event.start_time) == func.date(event_data['start_time'])
                    ).first()
                    
                    if existing:
                        logger.info(f"Duplicate event found: {event_data['title']}")
                        stats['duplicates'] += 1
                        continue
                    
                    # Create new event
                    new_event = Event(
                        title=event_data['title'],
                        event_type=event_data['event_type'],
                        description=event_data.get('description'),
                        geom=func.ST_SetSRID(
                            func.ST_MakePoint(event_data['lon'], event_data['lat']),
                            4326
                        ),
                        start_time=event_data['start_time'],
                        end_time=event_data.get('end_time')
                    )
                    
                    db.add(new_event)
                    db.commit()
                    stats['imported'] += 1
                    logger.info(f"Imported event: {event_data['title']}")
                    
                except Exception as e:
                    logger.error(f"Error importing event {event_data.get('title')}: {e}")
                    db.rollback()
                    stats['errors'] += 1
                    continue
            
            return stats
            
        finally:
            if close_db:
                db.close()

def scrape_and_import_yandex_events(city: str = "voronezh", categories: Optional[List[str]] = None):
    """
    Convenience function to scrape and import events in one call
    """
    scraper = YandexAfishaScraper(city=city)
    events = scraper.scrape_events(categories=categories)
    
    if not events:
        logger.warning("No events found to import")
        return {'total': 0, 'imported': 0, 'duplicates': 0, 'errors': 0}
    
    stats = scraper.import_events_to_db(events)
    logger.info(f"Import completed: {stats}")
    return stats