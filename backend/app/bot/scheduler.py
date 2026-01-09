"""
Scheduler for periodic tasks
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
import os
from ..scrapers.yandex_afisha import scrape_and_import_yandex_events

logger = logging.getLogger(__name__)

def setup_event_import_scheduler(scheduler: AsyncIOScheduler):
    """
    Setup scheduler for automatic event imports from Yandex Afisha
    
    Args:
        scheduler: AsyncIOScheduler instance
    """
    # Get configuration from environment
    import_enabled = os.getenv('YANDEX_AFISHA_IMPORT_ENABLED', 'true').lower() == 'true'
    import_hour = int(os.getenv('YANDEX_AFISHA_IMPORT_HOUR', '2'))  # 2 AM by default
    import_minute = int(os.getenv('YANDEX_AFISHA_IMPORT_MINUTE', '0'))
    city = os.getenv('YANDEX_AFISHA_CITY', 'voronezh')
    
    if not import_enabled:
        logger.info("Yandex Afisha import is disabled")
        return
    
    # Schedule daily import
    scheduler.add_job(
        import_yandex_events_job,
        trigger=CronTrigger(hour=import_hour, minute=import_minute),
        args=[city],
        id='yandex_afisha_import',
        name='Import events from Yandex Afisha',
        replace_existing=True
    )
    
    logger.info(f"Scheduled Yandex Afisha import for {import_hour:02d}:{import_minute:02d} daily")

def import_yandex_events_job(city: str):
    """
    Job function to import events from Yandex Afisha
    This runs in a separate thread/process
    """
    try:
        logger.info(f"Starting Yandex Afisha import for {city}")
        
        # Define categories to scrape
        categories = ['concert', 'theatre', 'exhibition', 'sport']
        
        # Run the scraper
        stats = scrape_and_import_yandex_events(city=city, categories=categories)
        
        logger.info(
            f"Yandex Afisha import completed: "
            f"Total: {stats['total']}, "
            f"Imported: {stats['imported']}, "
            f"Duplicates: {stats['duplicates']}, "
            f"Errors: {stats['errors']}"
        )
        
    except Exception as e:
        logger.error(f"Error in Yandex Afisha import job: {e}")