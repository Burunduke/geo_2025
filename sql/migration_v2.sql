-- Миграция v2: Добавление новых полей для поддержки городов и улучшенной дедупликации
BEGIN;

-- Добавление новых полей
ALTER TABLE events ADD COLUMN city VARCHAR(50);
ALTER TABLE events ADD COLUMN source_id VARCHAR(100);
ALTER TABLE events ADD COLUMN last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE events ADD COLUMN is_archived BOOLEAN DEFAULT FALSE;

-- Установка значения по умолчанию для существующих записей
UPDATE events SET city = 'voronezh' WHERE city IS NULL;

-- Сделать поле city обязательным после заполнения
ALTER TABLE events ALTER COLUMN city SET NOT NULL;

-- Создание индексов для оптимизации запросов
CREATE INDEX idx_events_city ON events(city);
CREATE INDEX idx_events_source_id ON events(source_id);
CREATE INDEX idx_events_is_archived ON events(is_archived);
CREATE INDEX idx_events_city_type ON events(city, event_type);
CREATE INDEX idx_events_city_time ON events(city, start_time);

COMMIT;

-- Комментарий: После выполнения миграции необходимо запустить скрипт определения городов для существующих событий