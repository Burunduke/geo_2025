"""
KudaGo API Scraper
Scrapes events from KudaGo using their official public API
API Documentation: https://docs.kudago.com/
"""
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import time
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import Event
from ..database import SessionLocal

logger = logging.getLogger(__name__)


class KudaGoScraper:
    """
    Scraper for KudaGo events using their official public API
    
    KudaGo provides a well-documented REST API with no authentication required.
    API is more reliable and structured than Yandex Afisha.
    """
    
    # API endpoints
    API_BASE = "https://kudago.com/public-api/v1.4"
    
    # Event type mapping from KudaGo categories to our types
    TYPE_MAPPING = {
        'concert': 'concert',
        'concerts': 'concert',
        'theater': 'theater',
        'theatre': 'theater',
        'exhibition': 'exhibition',
        'exhibitions': 'exhibition',
        'sport': 'sport',
        'festival': 'festival',
        'festivals': 'festival',
        'cinema': 'festival',
        'party': 'festival',
        'show': 'festival',
        'entertainment': 'festival',
        'kids': 'festival',
        'education': 'festival',
        'business': 'festival',
        'other': 'festival'
    }
    
    # City slug mapping
    CITY_MAPPING = {
        'voronezh': 'vrn',
        'moscow': 'msk',
        'spb': 'spb',
        'saint-petersburg': 'spb',
        'petersburg': 'spb',
        'ekaterinburg': 'ekb',
        'kazan': 'kzn',
        'nizhny-novgorod': 'nnv',
        'novosibirsk': 'nsk',
        'samara': 'smr',
        'krasnoyarsk': 'krs',
        'krasnodar': 'krd',
        'sochi': 'sochi',
        'rostov': 'rnd'
    }
    
    def __init__(self, city: str = "voronezh"):
        """
        Initialize scraper for a specific city
        
        Args:
            city: City name (e.g., 'voronezh', 'moscow', 'spb')
        """
        self.city = city
        self.city_slug = self.CITY_MAPPING.get(city.lower(), 'vrn')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def scrape_events(self, 
                     categories: Optional[List[str]] = None,
                     days_ahead: int = 30,
                     limit: int = 100) -> List[Dict]:
        """
        Scrape events from KudaGo API
        
        Args:
            categories: List of categories to scrape (e.g., ['concert', 'theater', 'exhibition'])
                       If None, scrapes all available categories
            days_ahead: Number of days ahead to fetch events for
            limit: Maximum total events to fetch
        
        Returns:
            List of event dictionaries with all required fields
        """
        all_events = []
        
        try:
            logger.info(f"Fetching events from KudaGo API for {self.city}")
            
            # Calculate date range
            now = datetime.now()
            actual_since = int(now.timestamp())
            actual_until = int((now + timedelta(days=days_ahead)).timestamp())
            
            # Build API request parameters
            params = {
                'location': self.city_slug,
                'actual_since': actual_since,
                'actual_until': actual_until,
                'page_size': min(limit, 100),  # API max is 100 per page
                'fields': 'id,title,description,body_text,location,place,dates,price,is_free,images,site_url,categories',
                'expand': 'place,location',
                'order_by': 'publication_date'
            }
            
            # Add category filter if specified
            if categories:
                # Map our category names to KudaGo slugs
                kudago_categories = []
                for cat in categories:
                    if cat in self.TYPE_MAPPING:
                        kudago_categories.append(cat)
                if kudago_categories:
                    params['categories'] = ','.join(kudago_categories)
            
            # Fetch events from API
            events = self._fetch_events_paginated(params, limit)
            
            # Parse events
            for event_data in events:
                try:
                    event = self._parse_event(event_data)
                    if event:
                        all_events.append(event)
                except Exception as e:
                    logger.error(f"Error parsing event: {e}", exc_info=True)
                    continue
            
            logger.info(f"Successfully scraped {len(all_events)} events from KudaGo")
            
        except Exception as e:
            logger.error(f"Error fetching events from KudaGo: {e}", exc_info=True)
        
        return all_events
    
    def _fetch_events_paginated(self, params: Dict, max_events: int) -> List[Dict]:
        """
        Fetch events with pagination support
        
        Args:
            params: API request parameters
            max_events: Maximum number of events to fetch
        
        Returns:
            List of event data dictionaries
        """
        all_events = []
        page = 1
        
        while len(all_events) < max_events:
            try:
                params['page'] = page
                
                response = self.session.get(
                    f"{self.API_BASE}/events/",
                    params=params,
                    timeout=10
                )
                
                if response.status_code != 200:
                    logger.warning(f"API returned status {response.status_code}")
                    break
                
                data = response.json()
                results = data.get('results', [])
                
                if not results:
                    break
                
                all_events.extend(results)
                
                # Check if there are more pages
                if not data.get('next'):
                    break
                
                page += 1
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error fetching page {page}: {e}")
                break
        
        return all_events[:max_events]
    
    def _parse_event(self, data: Dict) -> Optional[Dict]:
        """
        Parse individual event from KudaGo API response
        
        Args:
            data: Event data from API
        
        Returns:
            Parsed event dictionary or None if parsing fails
        """
        try:
            # Extract basic information
            event_id = data.get('id')
            title = data.get('title', '').strip()
            
            if not title:
                return None
            
            # Extract description
            description = (
                data.get('description', '') or
                data.get('body_text', '') or
                ''
            ).strip()
            
            # Limit description length
            if description:
                description = description[:500]
            
            # Extract dates
            start_time, end_time = self._parse_dates(data)
            
            if not start_time:
                return None
            
            # Extract location information
            place = data.get('place', {})
            if not place and isinstance(data.get('location'), dict):
                place = data.get('location', {})
            
            venue_name = ''
            lat = None
            lon = None
            
            if place:
                venue_name = place.get('title', '') or place.get('name', '')
                coords = place.get('coords', {})
                if coords:
                    lat = coords.get('lat')
                    lon = coords.get('lon')
            
            # Skip events without coordinates
            if not lat or not lon:
                logger.debug(f"Skipping event without coordinates: {title}")
                return None
            
            # Extract image
            image_url = self._extract_image_url(data)
            
            # Extract price
            price = self._extract_price(data)
            
            # Build source URL
            source_url = data.get('site_url', '')
            if not source_url and event_id:
                source_url = f"https://kudago.com/{self.city_slug}/event/{event_id}/"
            
            # Determine event type from categories
            event_type = self._determine_event_type(data)
            
            return {
                'title': title,
                'event_type': event_type,
                'description': description if description else None,
                'venue': venue_name,
                'lat': float(lat),
                'lon': float(lon),
                'start_time': start_time,
                'end_time': end_time,
                'source': 'kudago',
                'source_id': str(event_id),  # Новое поле
                'source_url': source_url,
                'image_url': image_url,
                'price': price,
                'city': self.city  # Новое поле
            }
            
        except Exception as e:
            logger.error(f"Error parsing event: {e}", exc_info=True)
            return None
    
    def _parse_dates(self, data: Dict) -> tuple:
        """
        Parse event dates from KudaGo data
        
        Returns:
            Tuple of (start_time, end_time)
        """
        dates = data.get('dates', [])
        
        if not dates:
            return None, None
        
        try:
            # Get the first upcoming date
            first_date = dates[0]
            
            # Parse start time
            start_timestamp = first_date.get('start')
            if start_timestamp:
                start_time = datetime.fromtimestamp(start_timestamp)
            else:
                start_date_str = first_date.get('start_date')
                if start_date_str:
                    start_time = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
                else:
                    return None, None
            
            # Parse end time
            end_time = None
            end_timestamp = first_date.get('end')
            if end_timestamp:
                end_time = datetime.fromtimestamp(end_timestamp)
            else:
                end_date_str = first_date.get('end_date')
                if end_date_str:
                    end_time = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
            
            return start_time, end_time
            
        except Exception as e:
            logger.error(f"Error parsing dates: {e}")
            return None, None
    
    def _extract_image_url(self, data: Dict) -> Optional[str]:
        """
        Extract image URL from event data
        """
        images = data.get('images', [])
        
        if images and isinstance(images, list) and len(images) > 0:
            image = images[0]
            if isinstance(image, dict):
                # Try different image sizes
                for size in ['image', 'source', 'thumbnails']:
                    url = image.get(size)
                    if url:
                        return url
            elif isinstance(image, str):
                return image
        
        return None
    
    def _extract_price(self, data: Dict) -> Optional[str]:
        """
        Extract price information from event data
        """
        # Check if free
        if data.get('is_free'):
            return "Бесплатно"
        
        # Get price string
        price = data.get('price', '').strip()
        if price:
            return price
        
        return None
    
    def _determine_event_type(self, data: Dict) -> str:
        """
        Determine event type from categories
        """
        categories = data.get('categories', [])
        
        if not categories:
            return 'festival'
        
        # Try to match first category
        for category in categories:
            if isinstance(category, str):
                cat_slug = category.lower()
            elif isinstance(category, dict):
                cat_slug = category.get('slug', '').lower()
            else:
                continue
            
            if cat_slug in self.TYPE_MAPPING:
                return self.TYPE_MAPPING[cat_slug]
        
        return 'festival'
    
    def import_events_to_db(self, events: List[Dict], db: Session = None) -> Dict:
        """
        Import scraped events to database with deduplication
        
        Args:
            events: List of event dictionaries
            db: Database session (optional, will create new if not provided)
        
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
                'created': 0,
                'updated': 0,
                'duplicates': 0,
                'errors': 0,
                'skipped_no_coords': 0
            }
            
            for event_data in events:
                try:
                    # Validate required fields
                    if not event_data.get('title'):
                        logger.warning("Skipping event without title")
                        stats['errors'] += 1
                        continue
                    
                    # Skip events without coordinates
                    if not event_data.get('lat') or not event_data.get('lon'):
                        logger.warning(f"Skipping event without coordinates: {event_data.get('title')}")
                        stats['skipped_no_coords'] += 1
                        continue
                    
                    # Check for duplicates by source_id
                    existing = None
                    if event_data.get('source_id'):
                        existing = db.query(Event).filter(
                            Event.source_id == event_data['source_id'],
                            Event.source == 'kudago'
                        ).first()
                    
                    # Fallback to old deduplication if no source_id
                    if not existing:
                        existing = db.query(Event).filter(
                            Event.title == event_data['title'],
                            Event.source == 'kudago',
                            func.date(Event.start_time) == func.date(event_data['start_time'])
                        ).first()
                    
                    if existing:
                        # Update existing event
                        existing.description = event_data.get('description', existing.description)
                        existing.image_url = event_data.get('image_url', existing.image_url)
                        existing.price = event_data.get('price', existing.price)
                        existing.last_updated = datetime.utcnow()
                        stats['updated'] += 1
                        logger.info(f"Updated event: {event_data['title']}")
                    else:
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
                            end_time=event_data.get('end_time'),
                            source='kudago',
                            source_id=event_data.get('source_id'),
                            source_url=event_data.get('source_url'),
                            image_url=event_data.get('image_url'),
                            price=event_data.get('price'),
                            venue=event_data.get('venue'),
                            city=event_data.get('city', self.city)
                        )
                        
                        db.add(new_event)
                        stats['created'] += 1
                        logger.info(f"Created event: {event_data['title']}")
                    
                    db.commit()
                    
                except Exception as e:
                    logger.error(f"Error importing event {event_data.get('title')}: {e}", exc_info=True)
                    db.rollback()
                    stats['errors'] += 1
                    continue
            
            logger.info(f"KudaGo import completed: {stats}")
            return stats
            
        finally:
            if close_db:
                db.close()


def scrape_and_import_kudago_events(
    city: str = "voronezh",
    categories: Optional[List[str]] = None,
    days_ahead: int = 30,
    limit: int = 100
) -> Dict:
    """
    Convenience function to scrape and import KudaGo events in one call
    
    Args:
        city: City name (e.g., 'voronezh', 'moscow', 'spb')
        categories: List of categories to scrape
        days_ahead: Number of days ahead to fetch events
        limit: Maximum number of events to fetch
    
    Returns:
        Dictionary with import statistics
    """
    scraper = KudaGoScraper(city=city)
    events = scraper.scrape_events(
        categories=categories,
        days_ahead=days_ahead,
        limit=limit
    )
    
    if not events:
        logger.warning("No events found to import from KudaGo")
        return {
            'total': 0,
            'imported': 0,
            'duplicates': 0,
            'errors': 0,
            'skipped_no_coords': 0
        }
    
    stats = scraper.import_events_to_db(events)
    logger.info(f"KudaGo scraping and import completed: {stats}")
    return stats