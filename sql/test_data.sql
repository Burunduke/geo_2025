-- Северный район
INSERT INTO districts (name, population, geom) VALUES
('Северный район', 35000, ST_SetSRID(ST_GeomFromText('POLYGON((
    37.610 55.760,
    37.625 55.760,
    37.625 55.770,
    37.610 55.770,
    37.610 55.760
))'), 4326));

-- Восточный район
INSERT INTO districts (name, population, geom) VALUES
('Восточный район', 42000, ST_SetSRID(ST_GeomFromText('POLYGON((
    37.625 55.750,
    37.640 55.750,
    37.640 55.760,
    37.625 55.760,
    37.625 55.750
))'), 4326));

-- ============================================
-- ПРОВЕРКА ДАННЫХ
-- ============================================

-- Подсчет объектов по типам
SELECT type, COUNT(*) as count FROM objects GROUP BY type ORDER BY count DESC;

-- Подсчет событий по типам
SELECT event_type, COUNT(*) as count FROM events GROUP BY event_type ORDER BY count DESC;

-- Список районов с населением
SELECT name, population FROM districts ORDER BY population DESC;

-- Проверка геометрии
SELECT 
    'objects' as table_name,
    COUNT(*) as total,
    COUNT(CASE WHEN ST_IsValid(geom) THEN 1 END) as valid_geom
FROM objects
UNION ALL
SELECT 
    'events',
    COUNT(*),
    COUNT(CASE WHEN ST_IsValid(geom) THEN 1 END)
FROM events
UNION ALL
SELECT 
    'districts',
    COUNT(*),
    COUNT(CASE WHEN ST_IsValid(geom) THEN 1 END)
FROM districts;