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
    city VARCHAR(50) NOT NULL DEFAULT 'voronezh',
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
    UPDATE events SET city = 'voronezh' WHERE city IS NULL;
    
    -- Делаем поле city обязательным, если есть записи без города
    IF EXISTS (SELECT 1 FROM events WHERE city IS NULL) THEN
        RAISE EXCEPTION 'Не все события имеют установленный город';
    END IF;
END $$;

SELECT PostGIS_version();