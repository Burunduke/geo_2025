-- Очистка всех данных из таблиц
DELETE FROM events;
DELETE FROM objects;
DELETE FROM districts;

-- Сброс счетчиков автоинкремента
ALTER SEQUENCE events_id_seq RESTART WITH 1;
ALTER SEQUENCE objects_id_seq RESTART WITH 1;
ALTER SEQUENCE districts_id_seq RESTART WITH 1;

-- Проверка, что таблицы пусты
SELECT 'objects' as table_name, COUNT(*) as count FROM objects
UNION ALL
SELECT 'events', COUNT(*) FROM events
UNION ALL
SELECT 'districts', COUNT(*) FROM districts;