-- Очистка всех данных из таблиц
DELETE FROM events;
DELETE FROM districts;

-- Сброс счетчиков автоинкремента
ALTER SEQUENCE events_id_seq RESTART WITH 1;
ALTER SEQUENCE districts_id_seq RESTART WITH 1;

-- Проверка, что таблицы пусты
SELECT 'events' as table_name, COUNT(*) as count FROM events
UNION ALL
SELECT 'districts', COUNT(*) FROM districts;