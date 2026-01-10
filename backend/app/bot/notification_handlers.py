"""
Telegram Bot Handlers for Notification Settings
Handles user preferences for real-time notifications
"""
import json
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from sqlalchemy import func
from datetime import datetime

from ..database import SessionLocal
from ..models import TelegramUser
from .handlers import get_main_menu_keyboard

logger = logging.getLogger(__name__)

# Conversation states
LOCATION, RADIUS, EVENT_TYPES, CITY, CONFIRM = range(5)


async def notifications_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /notifications command - show notification settings"""
    user = update.effective_user
    
    db = SessionLocal()
    try:
        db_user = db.query(TelegramUser).filter(
            TelegramUser.telegram_id == user.id
        ).first()
        
        if not db_user:
            await update.message.reply_text(
                "❌ Пользователь не найден. Используйте /start"
            )
            return
        
        # Show current settings
        status = "✅ Включены" if db_user.notifications_enabled else "❌ Выключены"
        
        text = f"🔔 *Настройки уведомлений*\n\n"
        text += f"Статус: {status}\n"
        
        if db_user.notifications_enabled:
            text += f"\n📍 *Ваши настройки:*\n"
            
            if db_user.user_location:
                text += f"• Местоположение: установлено\n"
            else:
                text += f"• Местоположение: не установлено\n"
            
            text += f"• Радиус: {db_user.notification_radius}м\n"
            
            if db_user.preferred_city:
                text += f"• Город: {db_user.preferred_city}\n"
            
            if db_user.preferred_event_types:
                try:
                    types = json.loads(db_user.preferred_event_types)
                    type_names = {
                        'concert': 'Концерты',
                        'theater': 'Театр',
                        'exhibition': 'Выставки',
                        'sport': 'Спорт',
                        'festival': 'Фестивали'
                    }
                    type_list = [type_names.get(t, t) for t in types]
                    text += f"• Типы событий: {', '.join(type_list)}\n"
                except:
                    pass
        
        text += "\n*Доступные команды:*\n"
        text += "/setup_notifications - Настроить уведомления\n"
        
        if db_user.notifications_enabled:
            text += "/disable_notifications - Отключить уведомления\n"
        else:
            text += "/enable_notifications - Включить уведомления\n"
        
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=get_main_menu_keyboard())
        
    finally:
        db.close()


async def setup_notifications_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start notification setup conversation"""
    user = update.effective_user
    
    db = SessionLocal()
    try:
        db_user = db.query(TelegramUser).filter(
            TelegramUser.telegram_id == user.id
        ).first()
        
        if not db_user:
            await update.message.reply_text(
                "❌ Пользователь не найден. Используйте /start"
            )
            return ConversationHandler.END
        
        # Ask for location
        location_keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton("📍 Отправить местоположение", request_location=True)]],
            one_time_keyboard=True,
            resize_keyboard=True
        )
        
        await update.message.reply_text(
            "🔔 *Настройка уведомлений*\n\n"
            "Я буду присылать вам уведомления о новых событиях в вашем районе.\n\n"
            "📍 Сначала отправьте ваше местоположение, чтобы я знал, где вы находитесь.\n\n"
            "Или отправьте /skip чтобы пропустить этот шаг.",
            reply_markup=location_keyboard,
            parse_mode='Markdown'
        )
        
        return LOCATION
        
    finally:
        db.close()


async def receive_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive user location"""
    user = update.effective_user
    location = update.message.location
    
    if location:
        # Store location in context
        context.user_data['location'] = {
            'lat': location.latitude,
            'lon': location.longitude
        }
        
        # Ask for radius
        radius_keyboard = ReplyKeyboardMarkup(
            [
                ["1 км", "3 км"],
                ["5 км", "10 км"],
                ["15 км", "20 км"]
            ],
            one_time_keyboard=True,
            resize_keyboard=True
        )
        
        await update.message.reply_text(
            "✅ Местоположение получено!\n\n"
            "📏 Теперь выберите радиус поиска событий:",
            reply_markup=radius_keyboard
        )
        
        return RADIUS
    else:
        await update.message.reply_text(
            "❌ Не удалось получить местоположение. Попробуйте еще раз или отправьте /skip"
        )
        return LOCATION


async def skip_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Skip location step"""
    context.user_data['location'] = None
    
    # Ask for city instead
    await update.message.reply_text(
        "Хорошо, без местоположения.\n\n"
        "🏙️ Укажите ваш город (например: voronezh, moscow, spb):",
        reply_markup=ReplyKeyboardRemove()
    )
    
    return CITY


async def receive_radius(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive notification radius"""
    radius_text = update.message.text
    
    # Parse radius from text
    try:
        radius_km = int(radius_text.split()[0])
        radius_m = radius_km * 1000
        context.user_data['radius'] = radius_m
        
        # Ask for event types
        event_keyboard = ReplyKeyboardMarkup(
            [
                ["🎵 Концерты", "🎭 Театр"],
                ["🖼️ Выставки", "⚽ Спорт"],
                ["🎪 Фестивали", "✅ Все типы"]
            ],
            one_time_keyboard=True,
            resize_keyboard=True
        )
        
        await update.message.reply_text(
            f"✅ Радиус установлен: {radius_km} км\n\n"
            "🎯 Какие типы событий вас интересуют?\n"
            "(Можете выбрать несколько через запятую или выбрать 'Все типы')",
            reply_markup=event_keyboard
        )
        
        return EVENT_TYPES
        
    except:
        await update.message.reply_text(
            "❌ Не удалось распознать радиус. Выберите из предложенных вариантов:"
        )
        return RADIUS


async def receive_event_types(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive preferred event types"""
    text = update.message.text
    
    # Map emoji to event types
    type_mapping = {
        '🎵': 'concert',
        'концерт': 'concert',
        '🎭': 'theater',
        'театр': 'theater',
        '🖼️': 'exhibition',
        'выставк': 'exhibition',
        '⚽': 'sport',
        'спорт': 'sport',
        '🎪': 'festival',
        'фестивал': 'festival'
    }
    
    if 'все' in text.lower():
        event_types = ['concert', 'theater', 'exhibition', 'sport', 'festival']
    else:
        event_types = []
        text_lower = text.lower()
        for key, value in type_mapping.items():
            if key in text_lower:
                if value not in event_types:
                    event_types.append(value)
    
    if not event_types:
        event_types = ['concert', 'theater', 'exhibition', 'sport', 'festival']
    
    context.user_data['event_types'] = event_types
    
    # If location was provided, skip city selection
    if context.user_data.get('location'):
        return await confirm_settings(update, context)
    
    # Ask for city
    await update.message.reply_text(
        "✅ Типы событий сохранены!\n\n"
        "🏙️ Укажите ваш город (например: voronezh, moscow, spb):",
        reply_markup=ReplyKeyboardRemove()
    )
    
    return CITY


async def receive_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive preferred city"""
    city = update.message.text.strip().lower()
    context.user_data['city'] = city
    
    return await confirm_settings(update, context)


async def confirm_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm and save settings"""
    user = update.effective_user
    
    db = SessionLocal()
    try:
        db_user = db.query(TelegramUser).filter(
            TelegramUser.telegram_id == user.id
        ).first()
        
        if not db_user:
            await update.message.reply_text(
                "❌ Ошибка: пользователь не найден"
            )
            return ConversationHandler.END
        
        # Update user settings
        db_user.notifications_enabled = True
        db_user.notify_on_import = True
        
        if context.user_data.get('location'):
            loc = context.user_data['location']
            db_user.user_location = func.ST_SetSRID(
                func.ST_MakePoint(loc['lon'], loc['lat']),
                4326
            )
        
        if context.user_data.get('radius'):
            db_user.notification_radius = context.user_data['radius']
        
        if context.user_data.get('event_types'):
            db_user.preferred_event_types = json.dumps(context.user_data['event_types'])
        
        if context.user_data.get('city'):
            db_user.preferred_city = context.user_data['city']
        
        db_user.last_interaction = datetime.utcnow()
        
        db.commit()
        
        await update.message.reply_text(
            "✅ *Уведомления настроены!*\n\n"
            "Теперь вы будете получать уведомления о новых событиях в вашем районе.\n\n"
            "Используйте /notifications для просмотра настроек.",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode='Markdown'
        )
        
        # Clear context
        context.user_data.clear()
        
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error saving notification settings: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка при сохранении настроек. Попробуйте позже."
        )
        return ConversationHandler.END
    finally:
        db.close()


async def cancel_setup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel notification setup"""
    context.user_data.clear()
    
    await update.message.reply_text(
        "❌ Настройка уведомлений отменена.",
        reply_markup=ReplyKeyboardRemove()
    )
    
    return ConversationHandler.END


async def enable_notifications_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enable notifications"""
    user = update.effective_user
    
    db = SessionLocal()
    try:
        db_user = db.query(TelegramUser).filter(
            TelegramUser.telegram_id == user.id
        ).first()
        
        if not db_user:
            await update.message.reply_text(
                "❌ Пользователь не найден. Используйте /start"
            )
            return
        
        if not db_user.user_location and not db_user.preferred_city:
            await update.message.reply_text(
                "❌ Сначала настройте уведомления с помощью /setup_notifications"
            )
            return
        
        db_user.notifications_enabled = True
        db_user.last_interaction = datetime.utcnow()
        db.commit()
        
        await update.message.reply_text(
            "✅ Уведомления включены!\n\n"
            "Вы будете получать уведомления о новых событиях."
        )
        
    finally:
        db.close()


async def disable_notifications_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Disable notifications"""
    user = update.effective_user
    
    db = SessionLocal()
    try:
        db_user = db.query(TelegramUser).filter(
            TelegramUser.telegram_id == user.id
        ).first()
        
        if not db_user:
            await update.message.reply_text(
                "❌ Пользователь не найден. Используйте /start"
            )
            return
        
        db_user.notifications_enabled = False
        db_user.last_interaction = datetime.utcnow()
        db.commit()
        
        await update.message.reply_text(
            "✅ Уведомления отключены.\n\n"
            "Используйте /enable_notifications чтобы включить их снова."
        )
        
    finally:
        db.close()