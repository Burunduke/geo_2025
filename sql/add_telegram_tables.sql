-- Add Telegram Bot tables to the database

-- Create telegram_users table
CREATE TABLE IF NOT EXISTS telegram_users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    chat_id BIGINT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on telegram_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_telegram_users_telegram_id ON telegram_users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_telegram_users_is_active ON telegram_users(is_active);

-- Create user_subscriptions table
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES telegram_users(id) ON DELETE CASCADE,
    district_id INTEGER NOT NULL REFERENCES districts(id) ON DELETE CASCADE,
    notification_time VARCHAR(5) DEFAULT '09:00',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, district_id)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user_id ON user_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_district_id ON user_subscriptions(district_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_is_active ON user_subscriptions(is_active);

-- Add comments for documentation
COMMENT ON TABLE telegram_users IS 'Telegram bot users';
COMMENT ON TABLE user_subscriptions IS 'User subscriptions to district notifications';

COMMENT ON COLUMN telegram_users.telegram_id IS 'Telegram user ID';
COMMENT ON COLUMN telegram_users.chat_id IS 'Telegram chat ID for sending messages';
COMMENT ON COLUMN telegram_users.is_active IS 'Whether user is active (not blocked bot)';
COMMENT ON COLUMN telegram_users.last_interaction IS 'Last time user interacted with bot';

COMMENT ON COLUMN user_subscriptions.notification_time IS 'Preferred notification time in HH:MM format';
COMMENT ON COLUMN user_subscriptions.is_active IS 'Whether subscription is active';