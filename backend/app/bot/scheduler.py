"""
Scheduler for automated tasks - event imports, cleanup, and notifications
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import logging
import os
import asyncio
from ..scrapers.kudago import scrape_and_import_kudago_events
from ..scrapers.yandex_afisha import scrape_and_import_yandex_events
from ..cities_config import CITIES
from .notifications import send_daily_notifications
from .realtime_notifications import send_realtime_notifications

logger = logging.getLogger(__name__)

def setup_event_import_scheduler(scheduler: AsyncIOScheduler):
    """
    Setup scheduler for automatic event imports and maintenance tasks
    
    Args:
        scheduler: AsyncIOScheduler instance
    """
    # Get configuration from environment
    import_enabled = os.getenv('AUTO_IMPORT_ENABLED', 'true').lower() == 'true'
    cleanup_enabled = os.getenv('CLEANUP_ENABLED', 'true').lower() == 'true'
    notifications_enabled = os.getenv('NOTIFICATIONS_ENABLED', 'true').lower() == 'true'
    
    if not import_enabled:
        logger.info("Auto import is disabled")
    else:
        # Schedule auto import every 6 hours
        scheduler.add_job(
            auto_import_events_job,
            trigger=CronTrigger(hour='*/6'),  # Every 6 hours
            id='auto_event_import',
            name='Auto import events from all sources',
            replace_existing=True
        )
        logger.info("Scheduled auto import every 6 hours")
    
    if cleanup_enabled:
        # Schedule cleanup at 3:00 AM daily
        scheduler.add_job(
            cleanup_old_events_job,
            trigger=CronTrigger(hour=3, minute=0),
            id='cleanup_old_events',
            name='Cleanup old events',
            replace_existing=True
        )
        logger.info("Scheduled cleanup at 3:00 AM daily")
    
    if notifications_enabled:
        # Schedule daily notifications at 9:00 AM
        scheduler.add_job(
            send_daily_notifications_job,
            trigger=CronTrigger(hour=9, minute=0),
            id='daily_notifications',
            name='Send daily notifications',
            replace_existing=True
        )
        logger.info("Scheduled daily notifications at 9:00 AM")

async def auto_import_events_job():
    """
    Job function to automatically import events from all sources for all cities
    Now includes real-time notifications for new events
    """
    try:
        logger.info("Starting automatic event import for all cities")
        
        all_new_event_ids = []
        
        for city_slug in CITIES.keys():
            try:
                # Import from KudaGo
                kudago_stats = scrape_and_import_kudago_events(
                    city=city_slug,
                    days_ahead=30,
                    limit=100
                )
                logger.info(f"KudaGo import for {city_slug}: {kudago_stats}")
                
                # Collect new event IDs
                if kudago_stats.get('new_event_ids'):
                    all_new_event_ids.extend(kudago_stats['new_event_ids'])
                
                # Import from Yandex Afisha
                yandex_stats = scrape_and_import_yandex_events(
                    city=city_slug,
                    days_ahead=30,
                    limit_per_category=50
                )
                logger.info(f"Yandex Afisha import for {city_slug}: {yandex_stats}")
                
                # Collect new event IDs
                if yandex_stats.get('new_event_ids'):
                    all_new_event_ids.extend(yandex_stats['new_event_ids'])
                
            except Exception as e:
                logger.error(f"Error importing events for city {city_slug}: {e}")
                continue
        
        logger.info(f"Automatic event import completed for all cities. Total new events: {len(all_new_event_ids)}")
        
        # Send real-time notifications for new events
        if all_new_event_ids:
            try:
                from .bot import get_bot_application
                application = get_bot_application()
                if application and application.bot:
                    logger.info(f"Sending real-time notifications for {len(all_new_event_ids)} new events")
                    await send_realtime_notifications(application.bot, all_new_event_ids)
                else:
                    logger.warning("Bot application not available for real-time notifications")
            except Exception as e:
                logger.error(f"Error sending real-time notifications: {e}")
        
    except Exception as e:
        logger.error(f"Error in auto import job: {e}")

def cleanup_old_events_job():
    """
    Job function to cleanup old events
    """
    from ..database import SessionLocal
    from ..models import Event
    
    db = SessionLocal()
    try:
        # Архивировать события старше 7 дней
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        archived_count = db.query(Event).filter(
            Event.end_time < cutoff_date,
            Event.is_archived == False
        ).update({'is_archived': True})
        
        # Удалить архивные события старше 30 дней
        archive_cutoff = datetime.utcnow() - timedelta(days=30)
        deleted_count = db.query(Event).filter(
            Event.is_archived == True,
            Event.end_time < archive_cutoff
        ).delete()
        
        db.commit()
        logger.info(f"Cleanup completed: archived {archived_count}, deleted {deleted_count}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error in cleanup job: {e}")
    finally:
        db.close()

def send_daily_notifications_job():
    """
    Job function to send daily notifications
    """
    try:
        logger.info("Starting daily notifications")
        # Get the bot application instance
        from .bot import get_bot_application
        application = get_bot_application()
        if application:
            send_daily_notifications(application.bot)
            logger.info("Daily notifications completed")
        else:
            logger.error("Bot application not available for notifications")
    except Exception as e:
        logger.error(f"Error in daily notifications job: {e}")