# Анализатор событий

Веб-приложение для работы с геопространственными данными города: объекты инфраструктуры, события и районы. Построено на FastAPI, PostgreSQL с PostGIS и Leaflet.

## Возможности

- **Управление объектами инфраструктуры**: больницы, школы, кафе, парковки, аптеки
- **Отслеживание событий**: ДТП, ремонты дорог, городские мероприятия
- **Работа с районами**: границы, население, статистика
- **Геопространственные запросы**:
  - Поиск объектов в радиусе
  - Поиск ближайшего объекта
  - Определение района по координатам
  - Статистика по районам
- **Интерактивная карта** с различными слоями и фильтрами

## Структура проекта

```
geo_2025/
├── backend/             # FastAPI приложение
│   ├── app/
│   │   ├── main.py      # Точка входа
│   │   ├── database.py  # Подключение к БД
│   │   ├── models.py    # SQLAlchemy модели
│   │   ├── schemas.py   # Pydantic схемы
│   │   └── routers/     # API эндпоинты
│   │       ├── objects.py
│   │       ├── events.py
│   │       └── districts.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/            # Веб-интерфейс
│   ├── index.html
│   ├── css/style.css
│   ├── js/
│   │   ├── map.js      # Логика карты
│   │   └── api.js      # API клиент
│   ├── Dockerfile
│   └── nginx.conf
├── sql/                # SQL скрипты
│   ├── init.sql        # Инициализация БД
│   ├── test_data.sql   # Тестовые данные
│   └── clear_data.sql  # Очистка данных
├── docker-compose.yml
└── .env
```

## Старт

### Требования

- Docker
- Docker Compose

### 1. Клонирование репозитория

```bash
git clone https://github.com/Burunduke/geo_2025
cd geo_2025
```

### 2. Настройка переменных окружения

Файл `.env` уже настроен с базовыми параметрами:

```env
POSTGRES_USER=geo_user
POSTGRES_PASSWORD=geo_password
POSTGRES_DB=city_geo_db

BACKEND_HOST=backend
BACKEND_PORT=8000
```

### 3. Запуск приложения

```bash
# Запуск всех сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps
```

Приложение будет доступно по адресу: **http://localhost**

API документация: **http://localhost:8000/docs**

### 4. Остановка приложения

```bash
# Остановка сервисов
docker-compose down

# Остановка с удалением томов (полная очистка)
docker-compose down -v
```

## Управление данными

### Загрузка тестовых данных

```bash
docker-compose exec -T db psql -U geo_user -d city_geo_db < sql/test_data.sql
```

Тестовые данные включают:
- 2 района (Ленинский и Центральный)
- 13 объектов инфраструктуры
- 7 событий

### Очистка всех данных

```bash
docker-compose exec -T db psql -U geo_user -d city_geo_db < sql/clear_data.sql
```

### Выполнение произвольных SQL запросов

```bash
# Интерактивная консоль
docker-compose exec db psql -U geo_user -d city_geo_db

# Выполнение запроса
docker-compose exec db psql -U geo_user -d city_geo_db -c "SELECT COUNT(*) FROM objects;"
```

## Разработка

## API Endpoints

### Объекты (`/api/objects`)

- `GET /api/objects/`                       - Получить все объекты
- `GET /api/objects/?object_type=hospital`  - Фильтр по типу
- `POST /api/objects/nearby`                - Поиск в радиусе
- `GET /api/objects/nearest`                - Ближайший объект
- `POST /api/objects/`                      - Создать объект
- `GET /api/objects/types`                  - Типы объектов

### События (`/api/events`)

- `GET /api/events/`                        - Получить все события
- `GET /api/events/?event_type=accident`    - Фильтр по типу
- `GET /api/events/nearby`                  - События в радиусе
- `POST /api/events/`                       - Создать событие
- `GET /api/events/types`                   - Типы событий

### Районы (`/api/districts`)

- `GET /api/districts/`                     - Получить все районы
- `GET /api/districts/find`                 - Найти район по координатам
- `GET /api/districts/{id}/objects`         - Объекты в районе
- `GET /api/districts/{id}/events`          - События в районе
- `GET /api/districts/{id}/stats`           - Статистика района
- `GET /api/districts/{id}/buffer`          - Буферная зона
- `GET /api/districts/intersect`            - Пересекающиеся районы

## База данных

### Структура таблиц

**objects**     - Объекты инфраструктуры
- `id`          - Уникальный идентификатор
- `name`        - Название
- `type`        - Тип (hospital, school, cafe, parking, pharmacy)
- `address`     - Адрес
- `geom`        - Геометрия (Point, SRID 4326)
- `created_at`  - Дата создания

**events**      - События
- `id`          - Уникальный идентификатор
- `title`       - Название
- `event_type`  - Тип (accident, repair, festival)
- `description` - Описание
- `geom`        - Геометрия (Point, SRID 4326)
- `start_time`  - Время начала
- `end_time`    - Время окончания
- `created_at`  - Дата создания

**districts**   - Районы
- `id`          - Уникальный идентификатор
- `name`        - Название
- `population`  - Население
- `geom`        - Геометрия (Polygon, SRID 4326)
- `created_at`  - Дата создания

### Резервное копирование

```bash
# Создание бэкапа
docker-compose exec db pg_dump -U geo_user city_geo_db > backup.sql

# Восстановление из бэкапа
docker-compose exec -T db psql -U geo_user -d city_geo_db < backup.sql
```

## Использование интерфейса

1. **Выбор точки на карте** - Кликните на карту для установки маркера
2. **Поиск в радиусе** - Укажите радиус и тип объекта, нажмите "Искать"
3. **Поиск ближайшего** - Выберите тип объекта и нажмите "Найти"
4. **Слои карты** - Используйте чекбоксы для отображения/скрытия слоев
5. **Информация о районе** - Кликните на район для просмотра статистики

## Стек технологий

### Backend
- **FastAPI** - Веб-фреймворк
- **SQLAlchemy** - ORM для работы с БД
- **GeoAlchemy2** - Расширение для геопространственных данных
- **Pydantic** - Валидация данных

### Frontend
- **Leaflet** - Библиотека для интерактивных карт
- **OpenStreetMap** - Картографические данные
- **JavaScript**

### Database
- **PostgreSQL** - Реляционная БД
- **PostGIS** - Расширение для геопространственных данных

### Infrastructure
- **Docker** - Контейнеризация
- **Docker Compose** - Оркестрация контейнеров
- **Nginx** - Веб-сервер для frontend

## Примеры использования API

### Создание объекта

```bash
curl -X POST "http://localhost:8000/api/objects/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Новая больница",
    "type": "hospital",
    "address": "ул. Примерная, 1",
    "lat": 51.6606,
    "lon": 39.2003
  }'
```

### Поиск объектов в радиусе

```bash
curl -X POST "http://localhost:8000/api/objects/nearby" \
  -H "Content-Type: application/json" \
  -d '{
    "lat": 51.6606,
    "lon": 39.2003,
    "radius": 1000,
    "object_type": "hospital"
  }'
```

### Создание события

```bash
curl -X POST "http://localhost:8000/api/events/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Ремонт дороги",
    "event_type": "repair",
    "description": "Плановый ремонт",
    "lat": 51.6606,
    "lon": 39.2003,
    "start_time": "2024-12-25T09:00:00",
    "end_time": "2024-12-25T18:00:00"
  }'
```