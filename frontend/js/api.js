const API_BASE_URL = '/api';

class CityGeoAPI {
    constructor(baseUrl = API_BASE_URL) {
        this.baseUrl = baseUrl;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Request failed:', error);
            throw error;
        }
    }

    // События
    
    async getEvents(type = null, source = null, upcomingOnly = false) {
        const params = new URLSearchParams();
        if (type) params.append('event_type', type);
        if (source) params.append('source', source);
        if (upcomingOnly) params.append('upcoming_only', 'true');
        const query = params.toString() ? `?${params}` : '';
        return this.request(`/events/${query}`);
    }

    async getEvent(eventId) {
        return this.request(`/events/${eventId}`);
    }

    async getTodayEvents() {
        return this.request('/events/filter/today');
    }

    async getUpcomingEvents(days = 7, limit = 50) {
        const params = new URLSearchParams({ days, limit });
        return this.request(`/events/filter/upcoming?${params}`);
    }

    async getNearbyEvents(lat, lon, radius, type = null) {
        const params = new URLSearchParams({ lat, lon, radius });
        if (type) params.append('event_type', type);
        return this.request(`/events/nearby?${params}`);
    }

    async createEvent(eventData) {
        return this.request('/events/', {
            method: 'POST',
            body: JSON.stringify(eventData)
        });
    }

    async getEventTypes() {
        return this.request('/events/types');
    }

    async importKudaGoEvents(city = 'voronezh', categories = null, daysAhead = 30) {
        const params = new URLSearchParams({
            city,
            days_ahead: daysAhead
        });
        
        if (categories && categories.length > 0) {
            categories.forEach(cat => params.append('categories', cat));
        }
        
        return this.request(`/events/import/kudago?${params}`, {
            method: 'POST'
        });
    }

    async importYandexEvents(city = 'voronezh', categories = null, daysAhead = 30) {
        const params = new URLSearchParams({
            city,
            days_ahead: daysAhead
        });
        
        if (categories && categories.length > 0) {
            categories.forEach(cat => params.append('categories', cat));
        }
        
        return this.request(`/events/import/yandex?${params}`, {
            method: 'POST'
        });
    }

    async importTestMoscowEvents() {
        return this.request('/events/import/test-moscow', {
            method: 'POST'
        });
    }

    // Города
    
    async getCities() {
        return this.request('/cities');
    }

    // Новые методы с поддержкой городов
    
    async getCityEvents(city, options = {}) {
        const params = new URLSearchParams();
        if (options.eventType) params.append('event_type', options.eventType);
        if (options.upcomingOnly) params.append('upcoming_only', 'true');
        if (options.bounds) params.append('bounds', options.bounds);
        
        const query = params.toString() ? `?${params}` : '';
        return this.request(`/${city}/events${query}`);
    }
    
    async getCityNearbyEvents(city, lat, lon, radius, eventType = null) {
        const params = new URLSearchParams({ lat, lon, radius });
        if (eventType) params.append('event_type', eventType);
        return this.request(`/${city}/events/nearby?${params}`);
    }
}

const api = new CityGeoAPI();