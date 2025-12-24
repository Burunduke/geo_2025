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

    // Объекты
    
    async getObjects(type = null) {
        const params = type ? `?object_type=${type}` : '';
        return this.request(`/objects/${params}`);
    }

    async getNearbyObjects(lat, lon, radius, type = null) {
        return this.request('/objects/nearby', {
            method: 'POST',
            body: JSON.stringify({
                lat: lat,
                lon: lon,
                radius: radius,
                object_type: type
            })
        });
    }

    async getNearestObject(lat, lon, type = null) {
        const params = new URLSearchParams({ lat, lon });
        if (type) params.append('object_type', type);
        return this.request(`/objects/nearest?${params}`);
    }

    async createObject(name, type, address, lat, lon) {
        return this.request('/objects/', {
            method: 'POST',
            body: JSON.stringify({
                name: name,
                type: type,
                address: address,
                lat: lat,
                lon: lon
            })
        });
    }

    async getObjectTypes() {
        return this.request('/objects/types');
    }

    // События
    
    async getEvents(type = null, activeOnly = false) {
        const params = new URLSearchParams();
        if (type) params.append('event_type', type);
        if (activeOnly) params.append('active_only', 'true');
        const query = params.toString() ? `?${params}` : '';
        return this.request(`/events/${query}`);
    }

    async getNearbyEvents(lat, lon, radius, type = null) {
        const params = new URLSearchParams({ lat, lon, radius });
        if (type) params.append('event_type', type);
        return this.request(`/events/nearby?${params}`);
    }

    async createEvent(title, eventType, description, lat, lon, startTime, endTime = null) {
        return this.request('/events/', {
            method: 'POST',
            body: JSON.stringify({
                title: title,
                event_type: eventType,
                description: description,
                lat: lat,
                lon: lon,
                start_time: startTime,
                end_time: endTime
            })
        });
    }

    async getEventTypes() {
        return this.request('/events/types');
    }

    // Районы
    
    async getDistricts() {
        return this.request('/districts/');
    }

    async findDistrictByPoint(lat, lon) {
        const params = new URLSearchParams({ lat, lon });
        return this.request(`/districts/find?${params}`);
    }

    async getObjectsInDistrict(districtId, type = null) {
        const params = type ? `?object_type=${type}` : '';
        return this.request(`/districts/${districtId}/objects${params}`);
    }

    async getEventsInDistrict(districtId, type = null) {
        const params = type ? `?event_type=${type}` : '';
        return this.request(`/districts/${districtId}/events${params}`);
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
}

const api = new CityGeoAPI();