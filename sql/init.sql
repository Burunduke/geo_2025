-- Включаем PostGIS расширение
CREATE EXTENSION IF NOT EXISTS postgis;

-- Таблица с событиями (обновленная схема v2)
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    description TEXT,
    geom GEOMETRY(Point, 4326) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    source VARCHAR(50) DEFAULT 'manual',  -- yandex_afisha, manual, telegram
    source_url VARCHAR(500),
    image_url VARCHAR(500),
    price VARCHAR(100),
    venue VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Новые поля из миграции v2
    city VARCHAR(50) NOT NULL DEFAULT 'spb',
    source_id VARCHAR(100),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_archived BOOLEAN DEFAULT FALSE
);

-- Пространственный индекс
CREATE INDEX IF NOT EXISTS idx_events_geom ON events USING GIST(geom);

-- Индексы для фильтрации
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_start_time ON events(start_time);
CREATE INDEX IF NOT EXISTS idx_events_source ON events(source);

-- Новые индексы из миграции v2
CREATE INDEX IF NOT EXISTS idx_events_city ON events(city);
CREATE INDEX IF NOT EXISTS idx_events_source_id ON events(source_id);
CREATE INDEX IF NOT EXISTS idx_events_is_archived ON events(is_archived);
CREATE INDEX IF NOT EXISTS idx_events_city_type ON events(city, event_type);
CREATE INDEX IF NOT EXISTS idx_events_city_time ON events(city, start_time);

-- Установка значения по умолчанию для существующих записей (если таблица уже существует)
DO $$
BEGIN
    -- Обновляем только те записи, где city еще не установлен
    UPDATE events SET city = 'spb' WHERE city IS NULL;
    
    -- Делаем поле city обязательным, если есть записи без города
    IF EXISTS (SELECT 1 FROM events WHERE city IS NULL) THEN
        RAISE EXCEPTION 'Не все события имеют установленный город';
    END IF;
END $$;

-- ============================================================================
-- TELEGRAM USERS AND NOTIFICATIONS (Migration 002)
-- ============================================================================

-- Create telegram_users table with notification preferences
CREATE TABLE IF NOT EXISTS telegram_users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    chat_id BIGINT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Notification preferences
    notifications_enabled BOOLEAN DEFAULT FALSE,
    notification_radius INTEGER DEFAULT 5000,  -- Radius in meters (default 5km)
    user_location GEOMETRY(Point, 4326),  -- User's location for notifications
    preferred_city VARCHAR(50),  -- User's preferred city
    
    -- Event type preferences (JSON array of event types)
    preferred_event_types TEXT,  -- JSON array: ["concert", "theater", "exhibition"]
    
    -- Notification settings
    notify_on_import BOOLEAN DEFAULT TRUE,  -- Send notification when new events are imported
    quiet_hours_start TIME,  -- Start of quiet hours (no notifications)
    quiet_hours_end TIME  -- End of quiet hours
);

-- Create indexes for telegram_users
CREATE INDEX IF NOT EXISTS idx_telegram_users_telegram_id ON telegram_users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_telegram_users_chat_id ON telegram_users(chat_id);
CREATE INDEX IF NOT EXISTS idx_telegram_users_notifications_enabled ON telegram_users(notifications_enabled);
CREATE INDEX IF NOT EXISTS idx_telegram_users_location ON telegram_users USING GIST(user_location);
CREATE INDEX IF NOT EXISTS idx_telegram_users_city ON telegram_users(preferred_city);

-- Create notification_history table
CREATE TABLE IF NOT EXISTS notification_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES telegram_users(id) ON DELETE CASCADE,
    event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notification_type VARCHAR(50) DEFAULT 'new_event',  -- new_event, daily_digest, etc.
    
    UNIQUE(user_id, event_id, notification_type)
);

-- Create indexes for notification_history
CREATE INDEX IF NOT EXISTS idx_notification_history_user_id ON notification_history(user_id);
CREATE INDEX IF NOT EXISTS idx_notification_history_event_id ON notification_history(event_id);
CREATE INDEX IF NOT EXISTS idx_notification_history_sent_at ON notification_history(sent_at);

-- Add comments to tables
COMMENT ON TABLE telegram_users IS 'Telegram bot users with notification preferences';
COMMENT ON TABLE notification_history IS 'History of sent notifications to prevent duplicates';

-- Add comments to important columns
COMMENT ON COLUMN telegram_users.notification_radius IS 'Notification radius in meters from user location';
COMMENT ON COLUMN telegram_users.user_location IS 'User location point for proximity-based notifications';
COMMENT ON COLUMN telegram_users.preferred_event_types IS 'JSON array of preferred event types';

SELECT PostGIS_version();