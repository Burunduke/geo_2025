-- Тестовые события для Санкт-Петербурга
-- Координаты центра СПб: 59.9343, 30.3351

-- Очистка старых тестовых событий
DELETE FROM events WHERE source = 'test_spb';

-- Концерты
INSERT INTO events (
    title, event_type, description, geom, start_time, end_time,
    source, source_id, source_url, image_url, price, venue, city
) VALUES 
(
    'Концерт Би-2 в Ледовом дворце',
    'concert',
    'Легендарная группа Би-2 представляет новую программу с лучшими хитами',
    ST_SetSRID(ST_MakePoint(30.2969, 59.9500), 4326),  -- Ледовый дворец
    NOW() + INTERVAL '2 days' + INTERVAL '19 hours',
    NOW() + INTERVAL '2 days' + INTERVAL '22 hours',
    'test_spb',
    'spb_concert_1',
    'https://example.com/bi2',
    NULL,
    'от 2500 ₽',
    'Ледовый дворец',
    'spb'
),
(
    'Симфонический оркестр в Мариинском театре',
    'concert',
    'Вечер классической музыки. Произведения Чайковского и Рахманинова',
    ST_SetSRID(ST_MakePoint(30.2947, 59.9259), 4326),  -- Мариинский театр
    NOW() + INTERVAL '3 days' + INTERVAL '19 hours',
    NOW() + INTERVAL '3 days' + INTERVAL '21 hours 30 minutes',
    'test_spb',
    'spb_concert_2',
    'https://example.com/mariinsky',
    NULL,
    'от 1500 ₽',
    'Мариинский театр',
    'spb'
),
(
    'Рок-фестиваль на Дворцовой площади',
    'festival',
    'Большой open-air фестиваль с участием российских рок-групп',
    ST_SetSRID(ST_MakePoint(30.3158, 59.9387), 4326),  -- Дворцовая площадь
    NOW() + INTERVAL '5 days' + INTERVAL '18 hours',
    NOW() + INTERVAL '5 days' + INTERVAL '23 hours',
    'test_spb',
    'spb_festival_1',
    'https://example.com/rockfest',
    NULL,
    'Бесплатно',
    'Дворцовая площадь',
    'spb'
);

-- Театр
INSERT INTO events (
    title, event_type, description, geom, start_time, end_time,
    source, source_id, source_url, image_url, price, venue, city
) VALUES 
(
    'Евгений Онегин в Александринском театре',
    'theater',
    'Классическая постановка по произведению А.С. Пушкина',
    ST_SetSRID(ST_MakePoint(30.3350, 59.9311), 4326),  -- Александринский театр
    NOW() + INTERVAL '1 day' + INTERVAL '19 hours',
    NOW() + INTERVAL '1 day' + INTERVAL '21 hours 30 minutes',
    'test_spb',
    'spb_theater_1',
    'https://example.com/onegin',
    NULL,
    'от 800 ₽',
    'Александринский театр',
    'spb'
),
(
    'Ревизор в МДТ',
    'theater',
    'Современная интерпретация классической комедии Н.В. Гоголя',
    ST_SetSRID(ST_MakePoint(30.3461, 59.9280), 4326),  -- МДТ
    NOW() + INTERVAL '4 days' + INTERVAL '19 hours',
    NOW() + INTERVAL '4 days' + INTERVAL '21 hours',
    'test_spb',
    'spb_theater_2',
    'https://example.com/revizor',
    NULL,
    'от 1200 ₽',
    'Малый драматический театр',
    'spb'
);

-- Выставки
INSERT INTO events (
    title, event_type, description, geom, start_time, end_time,
    source, source_id, source_url, image_url, price, venue, city
) VALUES 
(
    'Импрессионисты в Эрмитаже',
    'exhibition',
    'Уникальная коллекция французских импрессионистов из собрания музея',
    ST_SetSRID(ST_MakePoint(30.3141, 59.9398), 4326),  -- Эрмитаж
    NOW() + INTERVAL '1 day' + INTERVAL '10 hours',
    NOW() + INTERVAL '30 days' + INTERVAL '18 hours',
    'test_spb',
    'spb_exhibition_1',
    'https://example.com/hermitage',
    NULL,
    'от 500 ₽',
    'Государственный Эрмитаж',
    'spb'
),
(
    'Современное искусство в Эрарте',
    'exhibition',
    'Выставка работ современных российских художников',
    ST_SetSRID(ST_MakePoint(30.3500, 59.9500), 4326),  -- Эрарта
    NOW() + INTERVAL '2 days' + INTERVAL '11 hours',
    NOW() + INTERVAL '45 days' + INTERVAL '19 hours',
    'test_spb',
    'spb_exhibition_2',
    'https://example.com/erarta',
    NULL,
    'от 400 ₽',
    'Музей Эрарта',
    'spb'
),
(
    'Петр I и его эпоха в Петропавловской крепости',
    'exhibition',
    'Историческая выставка, посвященная основателю Санкт-Петербурга',
    ST_SetSRID(ST_MakePoint(30.3167, 59.9500), 4326),  -- Петропавловская крепость
    NOW() + INTERVAL '1 day' + INTERVAL '10 hours',
    NOW() + INTERVAL '60 days' + INTERVAL '18 hours',
    'test_spb',
    'spb_exhibition_3',
    'https://example.com/peter',
    NULL,
    'от 300 ₽',
    'Петропавловская крепость',
    'spb'
);

-- Спорт
INSERT INTO events (
    title, event_type, description, geom, start_time, end_time,
    source, source_id, source_url, image_url, price, venue, city
) VALUES 
(
    'Зенит - Спартак на Газпром Арене',
    'sport',
    'Матч чемпионата России по футболу. Принципиальное дерби',
    ST_SetSRID(ST_MakePoint(30.2225, 59.9728), 4326),  -- Газпром Арена
    NOW() + INTERVAL '6 days' + INTERVAL '19 hours',
    NOW() + INTERVAL '6 days' + INTERVAL '21 hours',
    'test_spb',
    'spb_sport_1',
    'https://example.com/zenit',
    NULL,
    'от 1000 ₽',
    'Газпром Арена',
    'spb'
),
(
    'СКА - ЦСКА. Хоккей',
    'sport',
    'Матч КХЛ между принципиальными соперниками',
    ST_SetSRID(ST_MakePoint(30.2969, 59.9500), 4326),  -- Ледовый дворец
    NOW() + INTERVAL '7 days' + INTERVAL '19 hours 30 minutes',
    NOW() + INTERVAL '7 days' + INTERVAL '22 hours',
    'test_spb',
    'spb_sport_2',
    'https://example.com/ska',
    NULL,
    'от 800 ₽',
    'Ледовый дворец',
    'spb'
);

-- Городские события
INSERT INTO events (
    title, event_type, description, geom, start_time, end_time,
    source, source_id, source_url, image_url, price, venue, city
) VALUES 
(
    'Развод мостов на Неве',
    'city_event',
    'Ежедневное зрелище - развод мостов через Неву. Лучший вид с Дворцовой набережной',
    ST_SetSRID(ST_MakePoint(30.3141, 59.9398), 4326),  -- Дворцовая набережная
    NOW() + INTERVAL '1 day' + INTERVAL '1 hour 25 minutes',
    NOW() + INTERVAL '1 day' + INTERVAL '2 hours 30 minutes',
    'test_spb',
    'spb_city_1',
    'https://example.com/bridges',
    NULL,
    'Бесплатно',
    'Дворцовая набережная',
    'spb'
),
(
    'Белые ночи в Петербурге',
    'festival',
    'Фестиваль Белых ночей - уникальное природное явление и культурная программа',
    ST_SetSRID(ST_MakePoint(30.3351, 59.9343), 4326),  -- Центр города
    NOW() + INTERVAL '1 day',
    NOW() + INTERVAL '30 days',
    'test_spb',
    'spb_festival_2',
    'https://example.com/whitenights',
    NULL,
    'Бесплатно',
    'Центр Санкт-Петербурга',
    'spb'
),
(
    'Экскурсия по крышам Петербурга',
    'city_event',
    'Уникальная возможность увидеть город с высоты птичьего полета',
    ST_SetSRID(ST_MakePoint(30.3200, 59.9300), 4326),  -- Невский проспект
    NOW() + INTERVAL '2 days' + INTERVAL '18 hours',
    NOW() + INTERVAL '2 days' + INTERVAL '20 hours',
    'test_spb',
    'spb_city_2',
    'https://example.com/roofs',
    NULL,
    'от 1500 ₽',
    'Невский проспект',
    'spb'
);

-- Дополнительные события в разных районах
INSERT INTO events (
    title, event_type, description, geom, start_time, end_time,
    source, source_id, source_url, image_url, price, venue, city
) VALUES 
(
    'Джазовый вечер в Джаз Филармоник Холле',
    'concert',
    'Выступление известных джазовых музыкантов',
    ST_SetSRID(ST_MakePoint(30.3600, 59.9250), 4326),  -- Джаз Филармоник Холл
    NOW() + INTERVAL '3 days' + INTERVAL '20 hours',
    NOW() + INTERVAL '3 days' + INTERVAL '23 hours',
    'test_spb',
    'spb_concert_3',
    'https://example.com/jazz',
    NULL,
    'от 1800 ₽',
    'Джаз Филармоник Холл',
    'spb'
),
(
    'Фестиваль уличной еды на Новой Голландии',
    'festival',
    'Гастрономический фестиваль с участием лучших рестораторов города',
    ST_SetSRID(ST_MakePoint(30.2889, 59.9278), 4326),  -- Новая Голландия
    NOW() + INTERVAL '4 days' + INTERVAL '12 hours',
    NOW() + INTERVAL '4 days' + INTERVAL '22 hours',
    'test_spb',
    'spb_festival_3',
    'https://example.com/foodfest',
    NULL,
    'Вход свободный',
    'Новая Голландия',
    'spb'
),
(
    'Балет Лебединое озеро в Мариинском-2',
    'theater',
    'Классический балет П.И. Чайковского в исполнении труппы Мариинского театра',
    ST_SetSRID(ST_MakePoint(30.2833, 59.9222), 4326),  -- Мариинский-2
    NOW() + INTERVAL '5 days' + INTERVAL '19 hours',
    NOW() + INTERVAL '5 days' + INTERVAL '22 hours',
    'test_spb',
    'spb_theater_3',
    'https://example.com/swan',
    NULL,
    'от 2000 ₽',
    'Мариинский театр-2',
    'spb'
);

-- Вывод статистики
SELECT 
    event_type,
    COUNT(*) as count,
    MIN(start_time) as earliest,
    MAX(start_time) as latest
FROM events 
WHERE source = 'test_spb'
GROUP BY event_type
ORDER BY count DESC;

-- Общая статистика
SELECT 
    COUNT(*) as total_events,
    COUNT(DISTINCT event_type) as event_types,
    MIN(start_time) as first_event,
    MAX(start_time) as last_event
FROM events 
WHERE source = 'test_spb';