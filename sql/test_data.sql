-- Тестовые данные для проекта "Карта событий города"

-- Районы города
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

-- Советский район
INSERT INTO districts (name, population, geom) VALUES
('Советский район', 38000, ST_SetSRID(ST_GeomFromText('POLYGON((
    39.200 51.665,
    39.220 51.665,
    39.220 51.675,
    39.200 51.675,
    39.200 51.665
))'), 4326));

-- События

-- Культурные события (как будто импортированы с Яндекс.Афиши)
INSERT INTO events (title, event_type, description, geom, start_time, end_time, source, source_url, venue, price) VALUES
('Концерт симфонического оркестра', 'concert', 'Вечер классической музыки. Произведения Чайковского и Рахманинова', 
 ST_SetSRID(ST_MakePoint(39.195, 51.660), 4326), 
 CURRENT_TIMESTAMP + INTERVAL '3 days', 
 CURRENT_TIMESTAMP + INTERVAL '3 days' + INTERVAL '3 hours',
 'yandex_afisha', 
 'https://afisha.yandex.ru/voronezh/concert/...',
 'Концертный зал им. Ростроповича',
 '500-2000 ₽'),

('Спектакль "Ревизор"', 'theater', 'Классическая постановка по Гоголю в современной интерпретации',
 ST_SetSRID(ST_MakePoint(39.198, 51.658), 4326),
 CURRENT_TIMESTAMP + INTERVAL '5 days',
 CURRENT_TIMESTAMP + INTERVAL '5 days' + INTERVAL '2 hours',
 'yandex_afisha',
 'https://afisha.yandex.ru/voronezh/theatre/...',
 'Театр драмы им. Кольцова',
 '300-1500 ₽'),

('Выставка современного искусства', 'exhibition', 'Работы молодых художников Воронежа',
 ST_SetSRID(ST_MakePoint(39.190, 51.675), 4326),
 CURRENT_TIMESTAMP + INTERVAL '1 day',
 CURRENT_TIMESTAMP + INTERVAL '30 days',
 'yandex_afisha',
 'https://afisha.yandex.ru/voronezh/exhibition/...',
 'Художественный музей им. Крамского',
 'Бесплатно'),

('Футбольный матч: Факел - Спартак', 'sport', 'Чемпионат России по футболу',
 ST_SetSRID(ST_MakePoint(39.180, 51.670), 4326),
 CURRENT_TIMESTAMP + INTERVAL '7 days',
 CURRENT_TIMESTAMP + INTERVAL '7 days' + INTERVAL '2 hours',
 'yandex_afisha',
 'https://afisha.yandex.ru/voronezh/sport/...',
 'Стадион "Факел"',
 '500-3000 ₽'),

('Джазовый фестиваль', 'festival', 'Три дня джазовой музыки с участием российских и зарубежных исполнителей',
 ST_SetSRID(ST_MakePoint(39.205, 51.668), 4326),
 CURRENT_TIMESTAMP + INTERVAL '10 days',
 CURRENT_TIMESTAMP + INTERVAL '13 days',
 'yandex_afisha',
 'https://afisha.yandex.ru/voronezh/festival/...',
 'Парк "Алые паруса"',
 '1000-5000 ₽');

-- Городские события (добавлены вручную)
INSERT INTO events (title, event_type, description, geom, start_time, end_time, source, venue) VALUES
('Ремонт дороги на проспекте Революции', 'repair', 'Ямочный ремонт асфальтового покрытия. Возможны задержки движения',
 ST_SetSRID(ST_MakePoint(39.187, 51.672), 4326),
 CURRENT_TIMESTAMP,
 CURRENT_TIMESTAMP + INTERVAL '5 days',
 'manual',
 'Проспект Революции, участок от ул. Кольцовской до ул. Пушкинской'),

('ДТП на перекрестке', 'accident', 'Столкновение двух автомобилей. Движение затруднено',
 ST_SetSRID(ST_MakePoint(39.188, 51.673), 4326),
 CURRENT_TIMESTAMP - INTERVAL '2 hours',
 CURRENT_TIMESTAMP + INTERVAL '1 hour',
 'manual',
 'Перекресток ул. Ленина и пр. Революции'),

('Городской субботник', 'city_event', 'Общегородской субботник по уборке территории',
 ST_SetSRID(ST_MakePoint(39.191, 51.676), 4326),
 CURRENT_TIMESTAMP + INTERVAL '2 days',
 CURRENT_TIMESTAMP + INTERVAL '2 days' + INTERVAL '4 hours',
 'manual',
 'Парк "Алые паруса"'),

('Замена водопровода', 'repair', 'Плановая замена участка водопровода. Возможно отключение воды',
 ST_SetSRID(ST_MakePoint(39.196, 51.657), 4326),
 CURRENT_TIMESTAMP + INTERVAL '1 day',
 CURRENT_TIMESTAMP + INTERVAL '4 days',
 'manual',
 'Ул. Студенческая, д. 5-15');

-- Статистика
SELECT 
    event_type,
    COUNT(*) as count,
    COUNT(CASE WHEN source = 'yandex_afisha' THEN 1 END) as from_afisha,
    COUNT(CASE WHEN source = 'manual' THEN 1 END) as manual
FROM events 
GROUP BY event_type 
ORDER BY count DESC;

-- Список районов с населением
SELECT name, population FROM districts ORDER BY population DESC;

-- Проверка геометрии
SELECT 
    'events' as table_name,
    COUNT(*) as total,
    COUNT(CASE WHEN ST_IsValid(geom) THEN 1 END) as valid_geom
FROM events
UNION ALL
SELECT 
    'districts',
    COUNT(*),
    COUNT(CASE WHEN ST_IsValid(geom) THEN 1 END)
FROM districts;

-- Предстоящие события
SELECT 
    title,
    event_type,
    venue,
    start_time,
    source
FROM events
WHERE start_time > CURRENT_TIMESTAMP
ORDER BY start_time
LIMIT 10;