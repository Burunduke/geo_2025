"""
Конфигурация городов России для карты событий
"""

CITIES = {
    "voronezh": {
        "name": "Воронеж",
        "name_en": "Voronezh",
        "lat": 51.6606,
        "lon": 39.2003,
        "zoom": 13,
        "country": "Россия"
    },
    "moscow": {
        "name": "Москва",
        "name_en": "Moscow",
        "lat": 55.7558,
        "lon": 37.6173,
        "zoom": 11,
        "country": "Россия"
    },
    "spb": {
        "name": "Санкт-Петербург",
        "name_en": "Saint Petersburg",
        "lat": 59.9343,
        "lon": 30.3351,
        "zoom": 11,
        "country": "Россия"
    },
    "ekaterinburg": {
        "name": "Екатеринбург",
        "name_en": "Yekaterinburg",
        "lat": 56.8389,
        "lon": 60.6057,
        "zoom": 12,
        "country": "Россия"
    },
    "kazan": {
        "name": "Казань",
        "name_en": "Kazan",
        "lat": 55.7964,
        "lon": 49.1089,
        "zoom": 12,
        "country": "Россия"
    },
    "novosibirsk": {
        "name": "Новосибирск",
        "name_en": "Novosibirsk",
        "lat": 55.0084,
        "lon": 82.9357,
        "zoom": 12,
        "country": "Россия"
    },
    "nizhny_novgorod": {
        "name": "Нижний Новгород",
        "name_en": "Nizhny Novgorod",
        "lat": 56.3269,
        "lon": 44.0059,
        "zoom": 12,
        "country": "Россия"
    },
    "samara": {
        "name": "Самара",
        "name_en": "Samara",
        "lat": 53.2001,
        "lon": 50.1500,
        "zoom": 12,
        "country": "Россия"
    },
    "rostov": {
        "name": "Ростов-на-Дону",
        "name_en": "Rostov-on-Don",
        "lat": 47.2357,
        "lon": 39.7015,
        "zoom": 12,
        "country": "Россия"
    },
    "ufa": {
        "name": "Уфа",
        "name_en": "Ufa",
        "lat": 54.7388,
        "lon": 55.9721,
        "zoom": 12,
        "country": "Россия"
    }
}

def get_city_info(city_slug: str) -> dict:
    """Получить информацию о городе по slug"""
    return CITIES.get(city_slug.lower())

def get_all_cities() -> list:
    """Получить список всех городов"""
    return [
        {
            "slug": slug,
            **info
        }
        for slug, info in CITIES.items()
    ]