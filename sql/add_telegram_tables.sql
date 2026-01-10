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

-- Add comments for documentation
COMMENT ON TABLE telegram_users IS 'Telegram bot users';

COMMENT ON COLUMN telegram_users.telegram_id IS 'Telegram user ID';
COMMENT ON COLUMN telegram_users.chat_id IS 'Telegram chat ID for sending messages';
COMMENT ON COLUMN telegram_users.is_active IS 'Whether user is active (not blocked bot)';
COMMENT ON COLUMN telegram_users.last_interaction IS 'Last time user interacted with bot';