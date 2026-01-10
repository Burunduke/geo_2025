"""
Real-time notification system for new events
Sends notifications to users when new events appear in their area
"""
import logging
import json
from datetime import datetime, time as dt_time
from typing import List, Optional
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session
from telegram import Bot
from telegram.error import TelegramError

from ..database import SessionLocal
from ..models import Event, TelegramUser, NotificationHistory

logger = logging.getLogger(__name__)


class RealtimeNotificationService:
    """Service for sending real-time notifications about new events"""
    
    def __init__(self, bot: Bot):
        """
        Initialize notification service
        
        Args:
            bot: Telegram Bot instance
        """
        self.bot = bot
    
    async def notify_users_about_new_events(self, event_ids: List[int], db: Session = None):
        """
        Notify relevant users about new events based on their preferences
        
        Args:
            event_ids: List of newly created event IDs
            db: Database session (optional)
        """
        if db is None:
            db = SessionLocal()
            close_db = True
        else:
            close_db = False
        
        try:
            if not event_ids:
                logger.info("No new events to notify about")
                return
            
            logger.info(f"Processing notifications for {len(event_ids)} new events")
            
            # Get all events
            events = db.query(Event).filter(Event.id.in_(event_ids)).all()
            
            if not events:
                logger.warning("No events found for given IDs")
                return
            
            # Get all users with notifications enabled
            users = db.query(TelegramUser).filter(
                TelegramUser.notifications_enabled == True,
                TelegramUser.is_active == True,
                TelegramUser.notify_on_import == True
            ).all()
            
            logger.info(f"Found {len(users)} users with notifications enabled")
            
            notification_count = 0
            
            for user in users:
                try:
                    # Check if user is in quiet hours
                    if self._is_quiet_hours(user):
                        logger.debug(f"User {user.telegram_id} is in quiet hours, skipping")
                        continue
                    
                    # Find relevant events for this user
                    relevant_events = self._filter_events_for_user(user, events, db)
                    
                    if not relevant_events:
                        continue
                    
                    # Send notification
                    sent = await self._send_notification_to_user(user, relevant_events, db)
                    if sent:
                        notification_count += sent
                
                except Exception as e:
                    logger.error(f"Error processing notifications for user {user.telegram_id}: {e}")
                    continue
            
            logger.info(f"Sent {notification_count} notifications to users")
            
        except Exception as e:
            logger.error(f"Error in notify_users_about_new_events: {e}", exc_info=True)
        finally:
            if close_db:
                db.close()
    
    def _is_quiet_hours(self, user: TelegramUser) -> bool:
        """
        Check if current time is within user's quiet hours
        
        Args:
            user: TelegramUser instance
        
        Returns:
            True if in quiet hours, False otherwise
        """
        if not user.quiet_hours_start or not user.quiet_hours_end:
            return False
        
        now = datetime.now().time()
        start = user.quiet_hours_start
        end = user.quiet_hours_end
        
        # Handle quiet hours that span midnight
        if start <= end:
            return start <= now <= end
        else:
            return now >= start or now <= end
    
    def _filter_events_for_user(
        self, 
        user: TelegramUser, 
        events: List[Event], 
        db: Session
    ) -> List[Event]:
        """
        Filter events based on user preferences
        
        Args:
            user: TelegramUser instance
            events: List of Event instances
            db: Database session
        
        Returns:
            List of relevant events for the user
        """
        relevant_events = []
        
        # Parse preferred event types
        preferred_types = None
        if user.preferred_event_types:
            try:
                preferred_types = json.loads(user.preferred_event_types)
            except:
                preferred_types = None
        
        for event in events:
            # Check if already notified
            already_notified = db.query(NotificationHistory).filter(
                NotificationHistory.user_id == user.id,
                NotificationHistory.event_id == event.id,
                NotificationHistory.notification_type == 'new_event'
            ).first()
            
            if already_notified:
                continue
            
            # Filter by city if user has preferred city
            if user.preferred_city and event.city != user.preferred_city:
                continue
            
            # Filter by event type if user has preferences
            if preferred_types and event.event_type not in preferred_types:
                continue
            
            # Filter by location if user has set location
            if user.user_location and user.notification_radius:
                # Calculate distance using PostGIS
                distance = db.query(
                    func.ST_Distance(
                        func.ST_Transform(user.user_location, 3857),
                        func.ST_Transform(event.geom, 3857)
                    )
                ).scalar()
                
                if distance and distance > user.notification_radius:
                    continue
            
            relevant_events.append(event)
        
        return relevant_events
    
    async def _send_notification_to_user(
        self, 
        user: TelegramUser, 
        events: List[Event],
        db: Session
    ) -> int:
        """
        Send notification about events to a user
        
        Args:
            user: TelegramUser instance
            events: List of relevant events
            db: Database session
        
        Returns:
            Number of notifications sent
        """
        try:
            # Prepare notification message
            message = self._format_notification_message(events)
            
            # Send message
            await self.bot.send_message(
                chat_id=user.chat_id,
                text=message,
                parse_mode='Markdown',
                disable_web_page_preview=False
            )
            
            # Record notifications in history
            for event in events:
                notification = NotificationHistory(
                    user_id=user.id,
                    event_id=event.id,
                    notification_type='new_event'
                )
                db.add(notification)
            
            db.commit()
            
            logger.info(f"Sent notification to user {user.telegram_id} about {len(events)} events")
            return len(events)
            
        except TelegramError as e:
            logger.error(f"Telegram error sending notification to {user.telegram_id}: {e}")
            
            # Deactivate user if bot was blocked
            if "bot was blocked" in str(e).lower() or "user is deactivated" in str(e).lower():
                user.is_active = False
                db.commit()
                logger.info(f"Deactivated user {user.telegram_id} due to blocked bot")
            
            return 0
        except Exception as e:
            logger.error(f"Error sending notification to user {user.telegram_id}: {e}")
            return 0
    
    def _format_notification_message(self, events: List[Event]) -> str:
        """
        Format notification message for events
        
        Args:
            events: List of Event instances
        
        Returns:
            Formatted message string
        """
        if len(events) == 1:
            event = events[0]
            message = "🔔 *Новое событие в вашем районе!*\n\n"
            message += self._format_single_event(event)
        else:
            message = f"🔔 *{len(events)} новых событий в вашем районе!*\n\n"
            for i, event in enumerate(events[:5], 1):  # Limit to 5 events
                message += f"{i}. {self._format_single_event(event, compact=True)}\n"
            
            if len(events) > 5:
                message += f"\n_...и еще {len(events) - 5} событий_"
        
        return message
    
    def _format_single_event(self, event: Event, compact: bool = False) -> str:
        """
        Format single event for notification
        
        Args:
            event: Event instance
            compact: If True, use compact format
        
        Returns:
            Formatted event string
        """
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
        
        if compact:
            text = f"{event_emoji} *{event.title}*"
            if event.venue:
                text += f" ({event.venue})"
            text += f"\n   📅 {event.start_time.strftime('%d.%m.%Y %H:%M')}"
        else:
            text = f"{event_emoji} *{event.title}*\n"
            if event.venue:
                text += f"📍 {event.venue}\n"
            text += f"📅 {event.start_time.strftime('%d.%m.%Y в %H:%M')}\n"
            if event.price:
                text += f"💰 {event.price}\n"
            if event.description:
                desc = event.description[:150]
                if len(event.description) > 150:
                    desc += "..."
                text += f"\n{desc}\n"
            if event.source_url:
                text += f"\n🔗 [Подробнее]({event.source_url})"
        
        return text


async def send_realtime_notifications(bot: Bot, event_ids: List[int]):
    """
    Convenience function to send real-time notifications
    
    Args:
        bot: Telegram Bot instance
        event_ids: List of newly created event IDs
    """
    service = RealtimeNotificationService(bot)
    await service.notify_users_about_new_events(event_ids)