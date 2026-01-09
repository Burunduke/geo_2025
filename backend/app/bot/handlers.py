"""
Telegram Bot Command Handlers
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from ..database import SessionLocal
from ..models import TelegramUser, UserSubscription, District, Event

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
                "📍 Вы можете подписаться на районы и получать ежедневные уведомления "
                "о событиях, которые произойдут сегодня.\n\n"
                "Доступные команды:\n"
                "/districts - Показать все районы\n"
                "/subscribe - Подписаться на район\n"
                "/unsubscribe - Отписаться от района\n"
                "/myareas - Мои подписки\n"
                "/today - События сегодня в моих районах\n"
                "/help - Помощь"
            )
        else:
            db_user.last_interaction = datetime.utcnow()
            db_user.is_active = True
            db.commit()
            
            welcome_text = (
                f"👋 С возвращением, {user.first_name}!\n\n"
                "Используйте /help для просмотра доступных команд."
            )
        
        await update.message.reply_text(welcome_text)
    finally:
        db.close()

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = (
        "📚 *Доступные команды:*\n\n"
        "/start - Начать работу с ботом\n"
        "/events - События сегодня\n"
        "/tomorrow - События завтра\n"
        "/week - События на неделю\n"
        "/districts - Показать все районы города\n"
        "/subscribe - Подписаться на уведомления о районе\n"
        "/unsubscribe - Отписаться от уведомлений\n"
        "/myareas - Показать мои подписки\n"
        "/help - Показать эту справку\n\n"
        "💡 *Как это работает:*\n"
        "1. Выберите районы, которые вас интересуют\n"
        "2. Подпишитесь на них командой /subscribe\n"
        "3. Каждое утро в 9:00 вы будете получать уведомления о событиях дня\n"
        "4. Используйте /events чтобы проверить события прямо сейчас"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def districts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /districts command - show all districts"""
    db = SessionLocal()
    try:
        districts = db.query(District).all()
        
        if not districts:
            await update.message.reply_text(
                "❌ В базе данных пока нет районов.\n"
                "Обратитесь к администратору для добавления районов."
            )
            return
        
        text = "📍 *Доступные районы:*\n\n"
        for district in districts:
            # Count events in district
            events_count = db.query(func.count(Event.id)).filter(
                func.ST_Within(
                    Event.geom,
                    district.geom
                )
            ).scalar()
            
            text += f"🏘 *{district.name}*\n"
            if district.population:
                text += f"   Население: {district.population:,}\n"
            text += f"   События: {events_count}\n"
            text += f"   ID: `{district.id}`\n\n"
        
        text += "\nИспользуйте /subscribe для подписки на район"
        
        await update.message.reply_text(text, parse_mode='Markdown')
    finally:
        db.close()

async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /subscribe command"""
    user = update.effective_user
    
    # Check if district_id is provided
    if not context.args:
        await update.message.reply_text(
            "❌ Укажите ID района для подписки.\n\n"
            "Использование: `/subscribe <district_id>`\n"
            "Пример: `/subscribe 1`\n\n"
            "Используйте /districts чтобы увидеть список районов",
            parse_mode='Markdown'
        )
        return
    
    try:
        district_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ ID района должен быть числом")
        return
    
    db = SessionLocal()
    try:
        # Get user
        db_user = db.query(TelegramUser).filter(
            TelegramUser.telegram_id == user.id
        ).first()
        
        if not db_user:
            await update.message.reply_text(
                "❌ Пользователь не найден. Используйте /start"
            )
            return
        
        # Check if district exists
        district = db.query(District).filter(District.id == district_id).first()
        if not district:
            await update.message.reply_text(
                f"❌ Район с ID {district_id} не найден.\n"
                "Используйте /districts для просмотра доступных районов"
            )
            return
        
        # Check if already subscribed
        existing = db.query(UserSubscription).filter(
            UserSubscription.user_id == db_user.id,
            UserSubscription.district_id == district_id
        ).first()
        
        if existing:
            if existing.is_active:
                await update.message.reply_text(
                    f"ℹ️ Вы уже подписаны на район *{district.name}*",
                    parse_mode='Markdown'
                )
            else:
                existing.is_active = True
                db.commit()
                await update.message.reply_text(
                    f"✅ Подписка на район *{district.name}* возобновлена!",
                    parse_mode='Markdown'
                )
        else:
            # Create new subscription
            subscription = UserSubscription(
                user_id=db_user.id,
                district_id=district_id,
                is_active=True
            )
            db.add(subscription)
            db.commit()
            
            await update.message.reply_text(
                f"✅ Вы подписались на район *{district.name}*!\n\n"
                f"Вы будете получать уведомления о событиях каждый день в 9:00.\n"
                f"Используйте /today чтобы проверить события прямо сейчас.",
                parse_mode='Markdown'
            )
    finally:
        db.close()

async def unsubscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /unsubscribe command"""
    user = update.effective_user
    
    if not context.args:
        await update.message.reply_text(
            "❌ Укажите ID района для отписки.\n\n"
            "Использование: `/unsubscribe <district_id>`\n"
            "Пример: `/unsubscribe 1`\n\n"
            "Используйте /myareas чтобы увидеть ваши подписки",
            parse_mode='Markdown'
        )
        return
    
    try:
        district_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ ID района должен быть числом")
        return
    
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
        
        subscription = db.query(UserSubscription).filter(
            UserSubscription.user_id == db_user.id,
            UserSubscription.district_id == district_id,
            UserSubscription.is_active == True
        ).first()
        
        if not subscription:
            await update.message.reply_text(
                f"❌ Вы не подписаны на район с ID {district_id}"
            )
            return
        
        district = db.query(District).filter(District.id == district_id).first()
        subscription.is_active = False
        db.commit()
        
        await update.message.reply_text(
            f"✅ Вы отписались от района *{district.name}*",
            parse_mode='Markdown'
        )
    finally:
        db.close()

async def myareas_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /myareas command - show user's subscriptions"""
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
        
        subscriptions = db.query(UserSubscription, District).join(
            District, UserSubscription.district_id == District.id
        ).filter(
            UserSubscription.user_id == db_user.id,
            UserSubscription.is_active == True
        ).all()
        
        if not subscriptions:
            await update.message.reply_text(
                "📭 У вас пока нет активных подписок.\n\n"
                "Используйте /districts чтобы увидеть доступные районы\n"
                "и /subscribe для подписки"
            )
            return
        
        text = "📍 *Ваши подписки:*\n\n"
        for sub, district in subscriptions:
            text += f"🏘 *{district.name}*\n"
            text += f"   ID: `{district.id}`\n"
            text += f"   Время уведомлений: {sub.notification_time}\n\n"
        
        text += "\nИспользуйте `/unsubscribe <id>` для отписки"
        
        await update.message.reply_text(text, parse_mode='Markdown')
    finally:
        db.close()

async def events_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /events command - show today's events in subscribed districts"""
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
        
        # Get user's subscribed districts
        subscriptions = db.query(UserSubscription).filter(
            UserSubscription.user_id == db_user.id,
            UserSubscription.is_active == True
        ).all()
        
        if not subscriptions:
            await update.message.reply_text(
                "📭 У вас нет активных подписок.\n"
                "Используйте /subscribe для подписки на районы"
            )
            return
        
        # Get today's events
        from datetime import date
        today = date.today()
        
        events_by_district = {}
        
        for sub in subscriptions:
            district = db.query(District).filter(District.id == sub.district_id).first()
            
            # Find events in this district for today
            events = db.query(Event).filter(
                func.ST_Within(Event.geom, district.geom),
                func.date(Event.start_time) == today
            ).all()
            
            if events:
                events_by_district[district.name] = events
        
        if not events_by_district:
            await update.message.reply_text(
                "📅 На сегодня нет запланированных событий в ваших районах"
            )
            return
        
        text = f"📅 *События на сегодня ({today.strftime('%d.%m.%Y')}):*\n\n"
        
        for district_name, events in events_by_district.items():
            text += f"🏘 *{district_name}*\n"
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
        
        await update.message.reply_text(text, parse_mode='Markdown')
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
        
        # Get user's subscribed districts
        subscriptions = db.query(UserSubscription).filter(
            UserSubscription.user_id == db_user.id,
            UserSubscription.is_active == True
        ).all()
        
        if not subscriptions:
            await update.message.reply_text(
                "📭 У вас нет активных подписок.\n"
                "Используйте /subscribe для подписки на районы"
            )
            return
        
        # Get tomorrow's events
        from datetime import date, timedelta
        tomorrow = date.today() + timedelta(days=1)
        
        events_by_district = {}
        
        for sub in subscriptions:
            district = db.query(District).filter(District.id == sub.district_id).first()
            
            events = db.query(Event).filter(
                func.ST_Within(Event.geom, district.geom),
                func.date(Event.start_time) == tomorrow
            ).all()
            
            if events:
                events_by_district[district.name] = events
        
        if not events_by_district:
            await update.message.reply_text(
                f"📅 На завтра ({tomorrow.strftime('%d.%m.%Y')}) нет запланированных событий в ваших районах"
            )
            return
        
        text = f"📅 *События на завтра ({tomorrow.strftime('%d.%m.%Y')}):*\n\n"
        
        for district_name, events in events_by_district.items():
            text += f"🏘 *{district_name}*\n"
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
        
        await update.message.reply_text(text, parse_mode='Markdown')
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
        
        # Get user's subscribed districts
        subscriptions = db.query(UserSubscription).filter(
            UserSubscription.user_id == db_user.id,
            UserSubscription.is_active == True
        ).all()
        
        if not subscriptions:
            await update.message.reply_text(
                "📭 У вас нет активных подписок.\n"
                "Используйте /subscribe для подписки на районы"
            )
            return
        
        # Get this week's events
        from datetime import date, timedelta
        today = date.today()
        week_end = today + timedelta(days=7)
        
        events_by_district = {}
        
        for sub in subscriptions:
            district = db.query(District).filter(District.id == sub.district_id).first()
            
            events = db.query(Event).filter(
                func.ST_Within(Event.geom, district.geom),
                func.date(Event.start_time) >= today,
                func.date(Event.start_time) <= week_end
            ).order_by(Event.start_time).all()
            
            if events:
                events_by_district[district.name] = events
        
        if not events_by_district:
            await update.message.reply_text(
                "📅 На ближайшую неделю нет запланированных событий в ваших районах"
            )
            return
        
        text = f"📅 *События на неделю ({today.strftime('%d.%m')} - {week_end.strftime('%d.%m.%Y')}):*\n\n"
        
        for district_name, events in events_by_district.items():
            text += f"🏘 *{district_name}*\n"
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
        
        await update.message.reply_text(text, parse_mode='Markdown')
    finally:
        db.close()