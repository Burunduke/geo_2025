"""
Main Telegram Bot Application
"""
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
import os
from .handlers import (
    start_command,
    help_command,
    events_command,
    tomorrow_command,
    week_command,
    get_main_menu_keyboard
)
from .notification_handlers import (
    notifications_command,
    setup_notifications_command,
    receive_location,
    skip_location,
    receive_radius,
    receive_event_types,
    receive_city,
    cancel_setup,
    enable_notifications_command,
    disable_notifications_command,
    LOCATION,
    RADIUS,
    EVENT_TYPES,
    CITY,
    CONFIRM
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
    application.add_handler(CommandHandler("events", events_command))
    application.add_handler(CommandHandler("today", events_command))  # Alias for events
    application.add_handler(CommandHandler("tomorrow", tomorrow_command))
    application.add_handler(CommandHandler("week", week_command))
    
    # Add notification command handlers
    application.add_handler(CommandHandler("notifications", notifications_command))
    application.add_handler(CommandHandler("enable_notifications", enable_notifications_command))
    application.add_handler(CommandHandler("disable_notifications", disable_notifications_command))
    
    # IMPORTANT: Add conversation handler BEFORE text message handlers
    # This ensures ConversationHandler has priority over menu buttons
    notification_setup_handler = ConversationHandler(
        entry_points=[
            CommandHandler("setup_notifications", setup_notifications_command),
            MessageHandler(filters.Regex("^⚙️ Настроить уведомления$"), setup_notifications_command)
        ],
        states={
            LOCATION: [
                MessageHandler(filters.LOCATION, receive_location),
                CommandHandler("skip", skip_location)
            ],
            RADIUS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_radius)
            ],
            EVENT_TYPES: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_event_types)
            ],
            CITY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_city)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_setup)],
        name="notification_setup",
        persistent=False
    )
    application.add_handler(notification_setup_handler)
    
    # Add text message handlers for menu buttons (AFTER ConversationHandler)
    application.add_handler(MessageHandler(filters.Regex("^📅 События сегодня$"), events_command))
    application.add_handler(MessageHandler(filters.Regex("^📆 События завтра$"), tomorrow_command))
    application.add_handler(MessageHandler(filters.Regex("^📊 События на неделю$"), week_command))
    application.add_handler(MessageHandler(filters.Regex("^🔔 Уведомления$"), notifications_command))
    application.add_handler(MessageHandler(filters.Regex("^ℹ️ Помощь$"), help_command))
    
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

def get_bot():
    """Get the current bot instance"""
    if application:
        return application.bot
    return None