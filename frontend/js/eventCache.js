/**
 * Класс для кеширования событий на фронтенде
 * Обеспечивает быструю загрузку событий при переключении между городами
 */
class EventCache {
    constructor() {
        this.cache = new Map(); // city -> events
        this.lastUpdate = new Map(); // city -> timestamp
        this.cacheTimeout = 30 * 60 * 1000; // 30 минут
    }
    
    /**
     * Проверить, действителен ли кеш для города
     * @param {string} city - Слаг города
     * @returns {boolean} - Действителен ли кеш
     */
    isCacheValid(city) {
        const lastUpdate = this.lastUpdate.get(city);
        if (!lastUpdate) return false;
        return (Date.now() - lastUpdate) < this.cacheTimeout;
    }
    
    /**
     * Получить события для города
     * @param {string} city - Слаг города
     * @param {boolean} forceRefresh - Принудительно обновить кеш
     * @returns {Promise<Array>} - Массив событий
     */
    async getEvents(city, forceRefresh = false) {
        if (!forceRefresh && this.isCacheValid(city)) {
            console.log(`Используем кеш для города ${city}`);
            return this.cache.get(city);
        }
        
        try {
            console.log(`Загружаем события для города ${city}`);
            const events = await api.getCityEvents(city);
            this.cache.set(city, events);
            this.lastUpdate.set(city, Date.now());
            console.log(`События для города ${city} загружены и закешированы`);
            return events;
        } catch (error) {
            console.error(`Ошибка загрузки событий для города ${city}:`, error);
            
            // Если есть кеш, вернуть его даже если он устарел
            if (this.cache.has(city)) {
                console.log(`Используем устаревший кеш для города ${city}`);
                return this.cache.get(city);
            }
            
            throw error;
        }
    }
    
    /**
     * Получить события в радиусе для города
     * @param {string} city - Слаг города
     * @param {number} lat - Широта
     * @param {number} lon - Долгота
     * @param {number} radius - Радиус в метрах
     * @param {string} eventType - Тип события (опционально)
     * @returns {Promise<Object>} - Объект с событиями и метаданными
     */
    async getNearbyEvents(city, lat, lon, radius, eventType = null) {
        try {
            const result = await api.getCityNearbyEvents(city, lat, lon, radius, eventType);
            return result;
        } catch (error) {
            console.error(`Ошибка загрузки ближайших событий для города ${city}:`, error);
            throw error;
        }
    }
    
    /**
     * Очистить кеш
     * @param {string} city - Слаг города (если не указан, очистить весь кеш)
     */
    clearCache(city = null) {
        if (city) {
            this.cache.delete(city);
            this.lastUpdate.delete(city);
            console.log(`Кеш для города ${city} очищен`);
        } else {
            this.cache.clear();
            this.lastUpdate.clear();
            console.log('Весь кеш очищен');
        }
    }
    
    /**
     * Получить список городов с кешированными событиями
     * @returns {Array} - Массив слогов городов
     */
    getCachedCities() {
        return Array.from(this.cache.keys());
    }
    
    /**
     * Получить время последнего обновления для города
     * @param {string} city - Слаг города
     * @returns {Date|null} - Время обновления или null
     */
    getLastUpdateTime(city) {
        const timestamp = this.lastUpdate.get(city);
        return timestamp ? new Date(timestamp) : null;
    }
    
    /**
     * Получить статистику кеша
     * @returns {Object} - Статистика кеша
     */
    getStats() {
        const cities = this.getCachedCities();
        const stats = {
            totalCities: cities.length,
            cities: {}
        };
        
        for (const city of cities) {
            const events = this.cache.get(city);
            const lastUpdate = this.getLastUpdateTime(city);
            const isValid = this.isCacheValid(city);
            
            stats.cities[city] = {
                eventCount: events ? events.length : 0,
                lastUpdate: lastUpdate,
                isValid: isValid,
                timeToExpire: isValid ? this.cacheTimeout - (Date.now() - this.lastUpdate.get(city)) : 0
            };
        }
        
        return stats;
    }
}

// Создать глобальный экземпляр кеша
const eventCache = new EventCache();