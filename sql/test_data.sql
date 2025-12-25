-- Ленинский район
INSERT INTO districts (name, population, geom) VALUES
('Ленинский район', 35000, ST_SetSRID(ST_GeomFromText('POLYGON((
    39.180 51.670,
    39.200 51.670,
    39.200 51.680,
    39.180 51.680,
    39.180 51.670
))'), 4326));

-- Центральный район
INSERT INTO districts (name, population, geom) VALUES
('Центральный район', 42000, ST_SetSRID(ST_GeomFromText('POLYGON((
    39.190 51.655,
    39.210 51.655,
    39.210 51.665,
    39.190 51.665,
    39.190 51.655
))'), 4326));

-- Больницы
INSERT INTO objects (name, type, address, geom) VALUES
('Городская больница №1', 'hospital', 'проспект Революции, 1', ST_SetSRID(ST_MakePoint(39.185, 51.675), 4326)),
('Центральная больница', 'hospital', 'ул. Студенческая, 5', ST_SetSRID(ST_MakePoint(39.195, 51.660), 4326));

-- Школы
INSERT INTO objects (name, type, address, geom) VALUES
('Школа №123', 'school', 'ул. Школьная, 10', ST_SetSRID(ST_MakePoint(39.188, 51.672), 4326)),
('Гимназия №45', 'school', 'ул. Образования, 15', ST_SetSRID(ST_MakePoint(39.198, 51.657), 4326)),
('Лицей №7', 'school', 'ул. Научная, 20', ST_SetSRID(ST_MakePoint(39.190, 51.678), 4326));

-- Кафе
INSERT INTO objects (name, type, address, geom) VALUES
('Кафе "Уют"', 'cafe', 'проспект Революции, 3', ST_SetSRID(ST_MakePoint(39.187, 51.673), 4326)),
('Ресторан "Городской"', 'cafe', 'ул. Парковая, 8', ST_SetSRID(ST_MakePoint(39.180, 51.658), 4326)),
('Кофейня "Аромат"', 'cafe', 'ул. Тихая, 12', ST_SetSRID(ST_MakePoint(39.192, 51.676), 4326));

-- Парковки
INSERT INTO objects (name, type, address, geom) VALUES
('Парковка №1', 'parking', 'ул. Гаражная, 2', ST_SetSRID(ST_MakePoint(39.186, 51.674), 4326)),
('Центральная парковка', 'parking', 'ул. Транспортная, 7', ST_SetSRID(ST_MakePoint(39.179, 51.659), 4326));

-- Аптеки
INSERT INTO objects (name, type, address, geom) VALUES
('Аптека "Здоровье"', 'pharmacy', 'ул. Лечебная, 4', ST_SetSRID(ST_MakePoint(39.189, 51.671), 4326)),
('Аптека 24/7', 'pharmacy', 'ул. Аптечная, 9', ST_SetSRID(ST_MakePoint(39.196, 51.656), 4326)),
('Фармацентр', 'pharmacy', 'ул. Медицинская, 14', ST_SetSRID(ST_MakePoint(39.193, 51.677), 4326));

-- ДТП
INSERT INTO events (title, event_type, description, geom, start_time, end_time) VALUES
('ДТП на перекрестке', 'accident', 'Столкновение двух автомобилей', ST_SetSRID(ST_MakePoint(39.188, 51.673), 4326), '2024-01-15 08:30:00', '2024-01-15 10:00:00'),
('Авария с участием пешехода', 'accident', 'Наезд на пешехода на пешеходном переходе', ST_SetSRID(ST_MakePoint(39.198, 51.658), 4326), '2024-02-20 17:45:00', '2024-02-20 19:00:00');

-- Ремонты дорог
INSERT INTO events (title, event_type, description, geom, start_time, end_time) VALUES
('Ремонт асфальта', 'repair', 'Ямочный ремонт на проспекте Революции', ST_SetSRID(ST_MakePoint(39.187, 51.672), 4326), '2024-03-10 09:00:00', '2024-03-15 18:00:00'),
('Ремонт водопровода', 'repair', 'Замена участка водопровода', ST_SetSRID(ST_MakePoint(39.196, 51.657), 4326), '2024-04-05 08:00:00', '2024-04-08 17:00:00');

-- Мероприятия
INSERT INTO events (title, event_type, description, geom, start_time, end_time) VALUES
('Городской фестиваль', 'festival', 'Ежегодный фестиваль городской культуры', ST_SetSRID(ST_MakePoint(39.190, 51.675), 4326), '2024-05-01 10:00:00', '2024-05-01 22:00:00'),
('Концерт в парке', 'festival', 'Выступление местных музыкальных коллективов', ST_SetSRID(ST_MakePoint(39.180, 51.660), 4326), '2024-06-15 18:00:00', '2024-06-15 21:00:00'),
('Ярмарка ремесел', 'festival', 'Выставка-продажа изделий ручной работы', ST_SetSRID(ST_MakePoint(39.191, 51.676), 4326), '2024-07-20 09:00:00', '2024-07-20 18:00:00');


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