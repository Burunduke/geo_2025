"""
Notification System for Telegram Bot
"""
from telegram import Bot
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime
from ..database import SessionLocal
from ..models import TelegramUser, UserSubscription, District, Event
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
        
        # Get all active users with subscriptions
        users_with_subs = db.query(TelegramUser).join(
            UserSubscription,
            TelegramUser.id == UserSubscription.user_id
        ).filter(
            TelegramUser.is_active == True,
            UserSubscription.is_active == True
        ).distinct().all()
        
        logger.info(f"Found {len(users_with_subs)} users with active subscriptions")
        
        sent_count = 0
        error_count = 0
        
        for user in users_with_subs:
            try:
                # Get user's subscriptions
                subscriptions = db.query(UserSubscription).filter(
                    UserSubscription.user_id == user.id,
                    UserSubscription.is_active == True
                ).all()
                
                # Collect events for all subscribed districts
                events_by_district = {}
                
                for sub in subscriptions:
                    district = db.query(District).filter(
                        District.id == sub.district_id
                    ).first()
                    
                    if not district:
                        continue
                    
                    # Find today's events in this district
                    events = db.query(Event).filter(
                        func.ST_Within(Event.geom, district.geom),
                        func.date(Event.start_time) == today
                    ).all()
                    
                    if events:
                        events_by_district[district.name] = events
                
                # Send notification if there are events
                if events_by_district:
                    message = format_daily_notification(today, events_by_district)
                    await bot.send_message(
                        chat_id=user.chat_id,
                        text=message,
                        parse_mode='Markdown'
                    )
                    sent_count += 1
                    logger.info(f"Sent notification to user {user.telegram_id}")
                else:
                    # Optionally send "no events" message
                    # await bot.send_message(
                    #     chat_id=user.chat_id,
                    #     text=f"📅 На сегодня ({today.strftime('%d.%m.%Y')}) нет запланированных событий в ваших районах",
                    #     parse_mode='Markdown'
                    # )
                    pass
                
            except Exception as e:
                error_count += 1
                logger.error(f"Error sending notification to user {user.telegram_id}: {e}")
                continue
        
        logger.info(f"Daily notifications completed. Sent: {sent_count}, Errors: {error_count}")
        
    except Exception as e:
        logger.error(f"Error in send_daily_notifications: {e}")
    finally:
        db.close()

def format_daily_notification(today: date, events_by_district: dict) -> str:
    """Format the daily notification message"""
    text = f"🌅 *Доброе утро!*\n\n"
    text += f"📅 События на сегодня ({today.strftime('%d.%m.%Y')})\n\n"
    
    for district_name, events in events_by_district.items():
        text += f"🏘 *{district_name}*\n"
        
        for event in events:
            event_emoji = {
                'accident': '🚨',
                'repair': '🚧',
                'festival': '🎉',
                'concert': '🎵',
                'theater': '🎭',
                'exhibition': '🖼',
                'sport': '⚽️'
            }.get(event.event_type, '📍')
            
            text += f"\n{event_emoji} *{event.title}*\n"
            text += f"   Тип: {event.event_type}\n"
            text += f"   Время: {event.start_time.strftime('%H:%M')}"
            if event.end_time:
                text += f" - {event.end_time.strftime('%H:%M')}"
            text += "\n"
            if event.description:
                # Limit description length
                desc = event.description[:150]
                if len(event.description) > 150:
                    desc += "..."
                text += f"   {desc}\n"
        
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
        
        # Find which district this event is in
        districts = db.query(District).filter(
            func.ST_Within(event.geom, District.geom)
        ).all()
        
        if not districts:
            logger.info(f"Event {event_id} is not in any district")
            return
        
        # Get users subscribed to these districts
        district_ids = [d.id for d in districts]
        users = db.query(TelegramUser).join(
            UserSubscription,
            TelegramUser.id == UserSubscription.user_id
        ).filter(
            TelegramUser.is_active == True,
            UserSubscription.is_active == True,
            UserSubscription.district_id.in_(district_ids)
        ).distinct().all()
        
        if not users:
            logger.info(f"No users subscribed to districts for event {event_id}")
            return
        
        # Format message
        event_emoji = {
            'accident': '🚨',
            'repair': '🚧',
            'festival': '🎉',
            'concert': '🎵',
            'theater': '🎭',
            'exhibition': '🖼',
            'sport': '⚽️'
        }.get(event.event_type, '📍')
        
        message = f"🔔 *Новое событие!*\n\n"
        message += f"{event_emoji} *{event.title}*\n\n"
        message += f"📍 Район: {', '.join([d.name for d in districts])}\n"
        message += f"📅 Дата: {event.start_time.strftime('%d.%m.%Y')}\n"
        message += f"🕐 Время: {event.start_time.strftime('%H:%M')}"
        if event.end_time:
            message += f" - {event.end_time.strftime('%H:%M')}"
        message += "\n"
        if event.description:
            message += f"\n{event.description}\n"
        
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