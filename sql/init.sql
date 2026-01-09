-- Включаем PostGIS расширение
CREATE EXTENSION IF NOT EXISTS postgis;

-- Таблица с событиями
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Пространственный индекс
CREATE INDEX idx_events_geom ON events USING GIST(geom);

-- Индексы для фильтрации
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_start_time ON events(start_time);
CREATE INDEX idx_events_source ON events(source);

-- Таблица с районами
CREATE TABLE IF NOT EXISTS districts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    population INTEGER,
    geom GEOMETRY(Polygon, 4326) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Пространственный индекс
CREATE INDEX idx_districts_geom ON districts USING GIST(geom);

SELECT PostGIS_version();