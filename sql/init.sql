-- init.sql
-- Инициализация базы данных City Geo App

-- Включаем PostGIS расширение
CREATE EXTENSION IF NOT EXISTS postgis;

-- ============================================
-- ТАБЛИЦА ОБЪЕКТОВ ИНФРАСТРУКТУРЫ
-- ============================================
CREATE TABLE IF NOT EXISTS objects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    address VARCHAR(255),
    geom GEOMETRY(Point, 4326) NOT NULL,  -- WGS84
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание пространственного индекса (GIST)
CREATE INDEX idx_objects_geom ON objects USING GIST(geom);

-- Индекс для фильтрации по типу
CREATE INDEX idx_objects_type ON objects(type);

-- ============================================
-- ТАБЛИЦА СОБЫТИЙ
-- ============================================
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    description TEXT,
    geom GEOMETRY(Point, 4326) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Пространственный индекс
CREATE INDEX idx_events_geom ON events USING GIST(geom);

-- Индексы для фильтрации
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_start_time ON events(start_time);

-- ============================================
-- ТАБЛИЦА РАЙОНОВ
-- ============================================
CREATE TABLE IF NOT EXISTS districts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    population INTEGER,
    geom GEOMETRY(Polygon, 4326) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Пространственный индекс
CREATE INDEX idx_districts_geom ON districts USING GIST(geom);

-- ============================================
-- ПРОВЕРКА УСТАНОВКИ
-- ============================================
SELECT PostGIS_version();