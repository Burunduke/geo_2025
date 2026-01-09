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

    async getEventsByDistrict(districtId, upcomingOnly = false) {
        const params = upcomingOnly ? '?upcoming_only=true' : '';
        return this.request(`/events/by-district/${districtId}${params}`);
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

    async importFromAfisha(city = 'voronezh', categories = null, daysAhead = 30, limitPerCategory = 50) {
        const params = new URLSearchParams({ 
            city, 
            days_ahead: daysAhead,
            limit_per_category: limitPerCategory
        });
        
        if (categories && categories.length > 0) {
            categories.forEach(cat => params.append('categories', cat));
        }
        
        return this.request(`/events/import-afisha?${params}`, {
            method: 'POST'
        });
    }

    // Районы
    
    async getDistricts() {
        return this.request('/districts/');
    }

    async findDistrictByPoint(lat, lon) {
        const params = new URLSearchParams({ lat, lon });
        return this.request(`/districts/find?${params}`);
    }

    async getDistrictStats(districtId) {
        return this.request(`/districts/${districtId}/stats`);
    }

    async getDistrictBuffer(districtId, radius = 500) {
        return this.request(`/districts/${districtId}/buffer?radius=${radius}`);
    }

    async getIntersectingDistricts(lat, lon, radius = 1000) {
        const params = new URLSearchParams({ lat, lon, radius });
        return this.request(`/districts/intersect?${params}`);
    }

    async importDistrictsFromOSM(city = 'Воронеж', country = 'Россия') {
        const params = new URLSearchParams({ city, country });
        return this.request(`/districts/import-osm?${params}`, {
            method: 'POST'
        });
    }

    // Города
    
    async getCities() {
        return this.request('/cities');
    }

    // Проверка состояния районов
    
    async checkDistrictsHealth() {
        return this.request('/districts/health');
    }
}

const api = new CityGeoAPI();