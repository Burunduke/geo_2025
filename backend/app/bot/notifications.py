"""
Notification System for Telegram Bot
"""
from telegram import Bot
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime
from ..database import SessionLocal
from ..models import TelegramUser, Event
import logging

logger = logging.getLogger(__name__)

async def send_daily_notifications(bot: Bot):
    """
    Send daily notifications to all active users about events in their subscribed districts
    This function should be called by the scheduler every day
    """
    db = SessionLocal()
    try:
        today = date.today()
        logger.info(f"Starting daily notifications for {today}")
        
        # Get all active users
        users = db.query(TelegramUser).filter(
            TelegramUser.is_active == True
        ).all()
        
        logger.info(f"Found {len(users)} active users")
        
        # Get today's events
        events = db.query(Event).filter(
            func.date(Event.start_time) == today
        ).all()
        
        if not events:
            logger.info("No events today, skipping notifications")
            return
        
        sent_count = 0
        error_count = 0
        
        for user in users:
            try:
                # Send notification with today's events
                message = format_daily_notification(today, events)
                await bot.send_message(
                    chat_id=user.chat_id,
                    text=message,
                    parse_mode='Markdown'
                )
                sent_count += 1
                logger.info(f"Sent notification to user {user.telegram_id}")
                
            except Exception as e:
                error_count += 1
                logger.error(f"Error sending notification to user {user.telegram_id}: {e}")
                continue
        
        logger.info(f"Daily notifications completed. Sent: {sent_count}, Errors: {error_count}")
        
    except Exception as e:
        logger.error(f"Error in send_daily_notifications: {e}")
    finally:
        db.close()

def format_daily_notification(today: date, events: list) -> str:
    """Format the daily notification message"""
    text = f"🌅 *Доброе утро!*\n\n"
    text += f"📅 События на сегодня ({today.strftime('%d.%m.%Y')})\n\n"
    
    for event in events:
        event_emoji = {
            'concert': '🎵',
            'theater': '🎭',
            'exhibition': '🖼️',
            'sport': '⚽',
            'festival': '🎪',
            'repair': '🚧',
            'accident': '🚗',
            'city_event': '🏛️'
        }.get(event.event_type, '📍')
        
        text += f"{event_emoji} *{event.title}*\n"
        if event.venue:
            text += f"   📍 {event.venue}\n"
        text += f"   🕐 {event.start_time.strftime('%H:%M')}"
        if event.end_time:
            text += f" - {event.end_time.strftime('%H:%M')}"
        text += "\n"
        if event.price:
            text += f"   💰 {event.price}\n"
        if event.description:
            # Limit description length
            desc = event.description[:100]
            if len(event.description) > 100:
                desc += "..."
            text += f"   {desc}\n"
        if event.source_url:
            text += f"   🔗 [Подробнее]({event.source_url})\n"
        text += "\n"
    
    text += "Хорошего дня! 😊"
    
    return text

async def send_event_notification(bot: Bot, event_id: int):
    """
    Send notification about a new event to users subscribed to the district
    This can be called when a new event is created
    """
    db = SessionLocal()
    try:
        # Get the event
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            logger.warning(f"Event {event_id} not found")
            return
        
        # Get all active users
        users = db.query(TelegramUser).filter(
            TelegramUser.is_active == True
        ).all()
        
        if not users:
            logger.info(f"No active users to notify about event {event_id}")
            return
        
        # Format message
        event_emoji = {
            'concert': '🎵',
            'theater': '🎭',
            'exhibition': '🖼️',
            'sport': '⚽',
            'festival': '🎪',
            'repair': '🚧',
            'accident': '🚗',
            'city_event': '🏛️'
        }.get(event.event_type, '📍')
        
        message = f"🔔 *Новое событие!*\n\n"
        message += f"{event_emoji} *{event.title}*\n\n"
        if event.venue:
            message += f"📍 Место: {event.venue}\n"
        message += f"📅 Дата: {event.start_time.strftime('%d.%m.%Y')}\n"
        message += f"🕐 Время: {event.start_time.strftime('%H:%M')}"
        if event.end_time:
            message += f" - {event.end_time.strftime('%H:%M')}"
        message += "\n"
        if event.price:
            message += f"💰 Цена: {event.price}\n"
        if event.description:
            desc = event.description[:200]
            if len(event.description) > 200:
                desc += "..."
            message += f"\n{desc}\n"
        if event.source_url:
            message += f"\n🔗 [Подробнее]({event.source_url})\n"
        
        # Send to all subscribed users
        sent_count = 0
        for user in users:
            try:
                await bot.send_message(
                    chat_id=user.chat_id,
                    text=message,
                    parse_mode='Markdown'
                )
                sent_count += 1
            except Exception as e:
                logger.error(f"Error sending event notification to user {user.telegram_id}: {e}")
        
        logger.info(f"Sent event notification to {sent_count} users")
        
    except Exception as e:
        logger.error(f"Error in send_event_notification: {e}")
    finally:
        db.close()