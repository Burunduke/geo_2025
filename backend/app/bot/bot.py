"""
Main Telegram Bot Application
"""
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
import os
from .handlers import (
    start_command,
    help_command,
    districts_command,
    subscribe_command,
    unsubscribe_command,
    myareas_command,
    today_command
)
from .notifications import send_daily_notifications
from .scheduler import setup_event_import_scheduler

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global variables
application = None
scheduler = None

async def start_bot():
    """Initialize and start the Telegram bot"""
    global application, scheduler
    
    # Get bot token from environment
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        raise ValueError("TELEGRAM_BOT_TOKEN is required")
    
    logger.info("Starting Telegram bot...")
    
    # Create application
    application = Application.builder().token(bot_token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("districts", districts_command))
    application.add_handler(CommandHandler("subscribe", subscribe_command))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe_command))
    application.add_handler(CommandHandler("myareas", myareas_command))
    application.add_handler(CommandHandler("today", today_command))
    
    # Setup scheduler for daily notifications
    scheduler = AsyncIOScheduler()
    
    # Get notification time from environment (default: 09:00 Moscow time)
    notification_hour = int(os.getenv('NOTIFICATION_HOUR', '9'))
    notification_minute = int(os.getenv('NOTIFICATION_MINUTE', '0'))
    
    # Schedule daily notifications
    # Note: This uses server time, adjust timezone as needed
    scheduler.add_job(
        send_daily_notifications,
        trigger=CronTrigger(hour=notification_hour, minute=notification_minute),
        args=[application.bot],
        id='daily_notifications',
        name='Send daily event notifications',
        replace_existing=True
    )
    
    # Setup Yandex Afisha import scheduler
    setup_event_import_scheduler(scheduler)
    
    scheduler.start()
    logger.info(f"Scheduler started. Daily notifications at {notification_hour:02d}:{notification_minute:02d}")
    
    # Start the bot
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    
    logger.info("Bot started successfully!")
    
    return application

async def stop_bot():
    """Stop the Telegram bot gracefully"""
    global application, scheduler
    
    logger.info("Stopping Telegram bot...")
    
    if scheduler:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
    
    if application:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()
        logger.info("Bot stopped")

def get_bot_application():
    """Get the current bot application instance"""
    return application