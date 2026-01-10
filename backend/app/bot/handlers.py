"""
Telegram Bot Command Handlers
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date, timedelta
from ..database import SessionLocal
from ..models import TelegramUser, Event


def get_main_menu_keyboard():
    """Get main menu keyboard with buttons"""
    keyboard = [
        [KeyboardButton("📅 События сегодня"), KeyboardButton("📆 События завтра")],
        [KeyboardButton("📊 События на неделю"), KeyboardButton("🔔 Уведомления")],
        [KeyboardButton("⚙️ Настроить уведомления"), KeyboardButton("ℹ️ Помощь")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    db = SessionLocal()
    try:
        # Create or update user
        db_user = db.query(TelegramUser).filter(
            TelegramUser.telegram_id == user.id
        ).first()
        
        if not db_user:
            db_user = TelegramUser(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                chat_id=chat_id,
                is_active=True
            )
            db.add(db_user)
            db.commit()
            
            welcome_text = (
                f"👋 Привет, {user.first_name}!\n\n"
                "Я бот для уведомлений о событиях в вашем городе.\n\n"
                "Используйте кнопки меню ниже для навигации 👇"
            )
        else:
            db_user.last_interaction = datetime.utcnow()
            db_user.is_active = True
            db.commit()
            
            welcome_text = (
                f"👋 С возвращением, {user.first_name}!\n\n"
                "Используйте кнопки меню ниже для навигации 👇"
            )
        
        await update.message.reply_text(welcome_text, reply_markup=get_main_menu_keyboard())
    finally:
        db.close()

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = (
        "📚 *Справка по боту*\n\n"
        "*📅 Просмотр событий:*\n"
        "• События сегодня - показать события на сегодня\n"
        "• События завтра - показать события на завтра\n"
        "• События на неделю - показать события на 7 дней\n\n"
        "*🔔 Уведомления:*\n"
        "• Уведомления - посмотреть текущие настройки\n"
        "• Настроить уведомления - настроить персональные уведомления\n\n"
        "💡 *Как работают уведомления:*\n"
        "1. Нажмите 'Настроить уведомления'\n"
        "2. Отправьте свою геолокацию\n"
        "3. Выберите радиус поиска (1-20 км)\n"
        "4. Выберите типы событий\n"
        "5. Получайте уведомления о новых событиях автоматически!\n\n"
        "🎯 *Типы событий:*\n"
        "🎵 Концерты • 🎭 Театр • 🖼️ Выставки\n"
        "⚽ Спорт • 🎪 Фестивали\n\n"
        "Используйте кнопки меню для навигации 👇"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=get_main_menu_keyboard())

async def events_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /events command - show today's events"""
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
        
        # Get today's events
        today = date.today()
        
        events = db.query(Event).filter(
            func.date(Event.start_time) == today
        ).all()
        
        if not events:
            await update.message.reply_text(
                "📅 На сегодня нет запланированных событий"
            )
            return
        
        text = f"📅 *События на сегодня ({today.strftime('%d.%m.%Y')}):*\n\n"
        
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
                
                text += f"\n{event_emoji} *{event.title}*\n"
                if event.venue:
                    text += f"   📍 {event.venue}\n"
                text += f"   🕐 {event.start_time.strftime('%H:%M')}"
                if event.end_time:
                    text += f" - {event.end_time.strftime('%H:%M')}"
                text += "\n"
                if event.price:
                    text += f"   💰 {event.price}\n"
                if event.description:
                    desc = event.description[:100]
                    if len(event.description) > 100:
                        desc += "..."
                    text += f"   {desc}\n"
                if event.source_url:
                    text += f"   🔗 [Подробнее]({event.source_url})\n"
                text += "\n"
        
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=get_main_menu_keyboard())
    finally:
        db.close()

async def tomorrow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /tomorrow command - show tomorrow's events"""
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
        
        # Get tomorrow's events
        tomorrow = date.today() + timedelta(days=1)
        
        events = db.query(Event).filter(
            func.date(Event.start_time) == tomorrow
        ).all()
        
        if not events:
            await update.message.reply_text(
                f"📅 На завтра ({tomorrow.strftime('%d.%m.%Y')}) нет запланированных событий"
            )
            return
        
        text = f"📅 *События на завтра ({tomorrow.strftime('%d.%m.%Y')}):*\n\n"
        
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
                
                text += f"\n{event_emoji} *{event.title}*\n"
                if event.venue:
                    text += f"   📍 {event.venue}\n"
                text += f"   🕐 {event.start_time.strftime('%H:%M')}"
                if event.end_time:
                    text += f" - {event.end_time.strftime('%H:%M')}"
                text += "\n"
                if event.price:
                    text += f"   💰 {event.price}\n"
                if event.description:
                    desc = event.description[:100]
                    if len(event.description) > 100:
                        desc += "..."
                    text += f"   {desc}\n"
                if event.source_url:
                    text += f"   🔗 [Подробнее]({event.source_url})\n"
                text += "\n"
        
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=get_main_menu_keyboard())
    finally:
        db.close()

async def week_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /week command - show this week's events"""
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
        
        # Get this week's events
        today = date.today()
        week_end = today + timedelta(days=7)
        
        events = db.query(Event).filter(
            func.date(Event.start_time) >= today,
            func.date(Event.start_time) <= week_end
        ).order_by(Event.start_time).all()
        
        if not events:
            await update.message.reply_text(
                "📅 На ближайшую неделю нет запланированных событий"
            )
            return
        
        text = f"📅 *События на неделю ({today.strftime('%d.%m')} - {week_end.strftime('%d.%m.%Y')}):*\n\n"
        
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
                
                text += f"\n{event_emoji} *{event.title}*\n"
                text += f"   📅 {event.start_time.strftime('%d.%m.%Y')}\n"
                if event.venue:
                    text += f"   📍 {event.venue}\n"
                text += f"   🕐 {event.start_time.strftime('%H:%M')}"
                if event.end_time:
                    text += f" - {event.end_time.strftime('%H:%M')}"
                text += "\n"
                if event.price:
                    text += f"   💰 {event.price}\n"
                if event.source_url:
                    text += f"   🔗 [Подробнее]({event.source_url})\n"
                text += "\n"
        
        await update.message.reply_text(text, parse_mode='Markdown', reply_markup=get_main_menu_keyboard())
    finally:
        db.close()