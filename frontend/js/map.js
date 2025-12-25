let map;
let userMarker = null;
let searchCircle = null;
let currentTileLayer = null;
let layers = {
    objects: L.layerGroup(),
    events: L.layerGroup(),
    districts: L.layerGroup()
};

const mapStyles = {
    osm: {
        url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    },
    dark: {
        url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
        attribution: '© OpenStreetMap contributors © CARTO',
        maxZoom: 19
    },
    light: {
        url: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
        attribution: '© OpenStreetMap contributors © CARTO',
        maxZoom: 19
    },
    satellite: {
        url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attribution: '© Esri',
        maxZoom: 19
    },
    toner: {
        url: 'https://stamen-tiles-{s}.a.ssl.fastly.net/toner/{z}/{x}/{y}{r}.png',
        attribution: '© Stamen Design © OpenStreetMap contributors',
        maxZoom: 19
    },
    terrain: {
        url: 'https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}{r}.jpg',
        attribution: '© Stamen Design © OpenStreetMap contributors',
        maxZoom: 19
    }
};

const icons = {
    hospital: L.icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    }),
    school: L.icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    }),
    cafe: L.icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    }),
    parking: L.icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-grey.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    }),
    pharmacy: L.icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-violet.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    }),
    event: L.icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-orange.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    })
};

function initMap() {
    // Создание карты (Воронеж)
    map = L.map('map').setView([51.6606, 39.2003], 13);

    // Установка начального стиля карты
    setMapStyle('osm');

    layers.objects.addTo(map);
    layers.events.addTo(map);

    map.on('click', onMapClick);

    loadObjects();
    loadEvents();
    loadDistricts();

    // Обработчик смены стиля карты
    document.getElementById('mapStyle').addEventListener('change', (e) => {
        setMapStyle(e.target.value);
    });

    document.getElementById('showObjects').addEventListener('change', (e) => {
        if (e.target.checked) {
            map.addLayer(layers.objects);
        } else {
            map.removeLayer(layers.objects);
        }
    });

    document.getElementById('showEvents').addEventListener('change', (e) => {
        if (e.target.checked) {
            map.addLayer(layers.events);
        } else {
            map.removeLayer(layers.events);
        }
    });

    document.getElementById('showDistricts').addEventListener('change', (e) => {
        if (e.target.checked) {
            map.addLayer(layers.districts);
        } else {
            map.removeLayer(layers.districts);
        }
    });
}

function setMapStyle(styleKey) {
    // Удаляем текущий слой карты, если он существует
    if (currentTileLayer) {
        map.removeLayer(currentTileLayer);
    }

    // Добавляем новый слой карты
    const style = mapStyles[styleKey];
    currentTileLayer = L.tileLayer(style.url, {
        attribution: style.attribution,
        maxZoom: style.maxZoom
    }).addTo(map);

    console.log(`Стиль карты изменён на: ${styleKey}`);
}

function onMapClick(e) {
    const lat = e.latlng.lat;
    const lon = e.latlng.lng;
    if (userMarker) {
        userMarker.setLatLng([lat, lon]);
    } else {
        userMarker = L.marker([lat, lon], {
            icon: L.icon({
                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-yellow.png',
                shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34],
                shadowSize: [41, 41]
            })
        }).addTo(map);
        userMarker.bindPopup('Ваше местоположение').openPopup();
    }

    findDistrict(lat, lon);
}

async function loadObjects() {
    try {
        const objects = await api.getObjects();
        layers.objects.clearLayers();

        objects.forEach(obj => {
            const icon = icons[obj.type] || icons.hospital;
            const marker = L.marker([obj.lat, obj.lon], { icon: icon });
            
            marker.bindPopup(`
                <b>${obj.name}</b><br>
                Тип: ${getObjectTypeRu(obj.type)}<br>
                Адрес: ${obj.address || 'Не указан'}
            `);
            
            marker.addTo(layers.objects);
        });

        console.log(`Загружено объектов: ${objects.length}`);
    } catch (error) {
        console.error('Ошибка загрузки объектов:', error);
        showError('Не удалось загрузить объекты');
    }
}

async function loadEvents() {
    try {
        const events = await api.getEvents();
        layers.events.clearLayers();

        events.forEach(evt => {
            const marker = L.marker([evt.lat, evt.lon], { icon: icons.event });
            
            const startTime = new Date(evt.start_time).toLocaleString('ru-RU');
            const endTime = evt.end_time ? new Date(evt.end_time).toLocaleString('ru-RU') : 'Не указано';
            
            marker.bindPopup(`
                <b>${evt.title}</b><br>
                Тип: ${getEventTypeRu(evt.event_type)}<br>
                Описание: ${evt.description || 'Нет описания'}<br>
                Начало: ${startTime}<br>
                Конец: ${endTime}
            `);
            
            marker.addTo(layers.events);
        });

        console.log(`Загружено событий: ${events.length}`);
    } catch (error) {
        console.error('Ошибка загрузки событий:', error);
        showError('Не удалось загрузить события');
    }
}

async function loadDistricts() {
    try {
        const districts = await api.getDistricts();
        layers.districts.clearLayers();

        districts.forEach(district => {
            const geoJsonLayer = L.geoJSON(district.geometry, {
                style: {
                    color: '#3388ff',
                    weight: 2,
                    fillOpacity: 0.1
                }
            });
            
            geoJsonLayer.bindPopup(`
                <b>${district.name}</b><br>
                Население: ${district.population ? district.population.toLocaleString() : 'Не указано'}
            `);
            
            geoJsonLayer.on('click', async () => {
                await showDistrictStats(district.id);
            });
            
            geoJsonLayer.addTo(layers.districts);
        });

        console.log(`Загружено районов: ${districts.length}`);
    } catch (error) {
        console.error('Ошибка загрузки районов:', error);
    }
}

async function searchNearby() {
    if (!userMarker) {
        showError('Сначала кликните на карту, чтобы выбрать точку');
        return;
    }

    const radius = parseFloat(document.getElementById('radius').value);
    const objectType = document.getElementById('objectType').value || null;
    const latlng = userMarker.getLatLng();

try {
        const result = await api.getNearbyObjects(latlng.lat, latlng.lng, radius, objectType);
        
        if (searchCircle) {
            map.removeLayer(searchCircle);
        }
        
        searchCircle = L.circle([latlng.lat, latlng.lng], {
            radius: radius,
            color: 'blue',
            fillOpacity: 0.1
        }).addTo(map);

        displayResults(`
            <h4>Найдено объектов: ${result.count}</h4>
            ${result.objects.map(obj => `
                <div class="result-item">
                    <b>${obj.name}</b><br>
                    Тип: ${getObjectTypeRu(obj.type)}<br>
                    Расстояние: ${obj.distance.toFixed(0)} м
                </div>
            `).join('')}
        `);

        result.objects.forEach(obj => {
            const marker = L.marker([obj.lat, obj.lon], { 
                icon: icons[obj.type] || icons.hospital
            }).addTo(map);
            marker.bindPopup(`
                <b>${obj.name}</b><br>
                Расстояние: ${obj.distance.toFixed(0)} м
            `).openPopup();
        });

    } catch (error) {
        console.error('Ошибка поиска:', error);
        showError('Ошибка при поиске объектов');
    }
}

async function findNearest() {
    if (!userMarker) {
        showError('Сначала кликните на карту, чтобы выбрать точку');
        return;
    }

    const objectType = document.getElementById('nearestType').value || null;
    const latlng = userMarker.getLatLng();

    try {
        const result = await api.getNearestObject(latlng.lat, latlng.lng, objectType);
        
        const polyline = L.polyline([
            [latlng.lat, latlng.lng],
            [result.lat, result.lon]
        ], { color: 'red', weight: 3 }).addTo(map);

        map.fitBounds(polyline.getBounds());

        displayResults(`
            <h4>Ближайший объект</h4>
            <div class="result-item">
                <b>${result.name}</b><br>
                Тип: ${getObjectTypeRu(result.type)}<br>
                Адрес: ${result.address || 'Не указан'}<br>
                Расстояние: ${result.distance.toFixed(0)} м
            </div>
        `);

        L.marker([result.lat, result.lon], { 
            icon: icons[result.type] || icons.hospital
        }).addTo(map).bindPopup(`
            <b>${result.name}</b><br>
            Расстояние: ${result.distance.toFixed(0)} м
        `).openPopup();

    } catch (error) {
        console.error('Ошибка поиска:', error);
        showError('Ошибка при поиске ближайшего объекта');
    }
}

async function findDistrict(lat, lon) {
    try {
        const result = await api.findDistrictByPoint(lat, lon);
        showInfo(`Вы находитесь в районе: <b>${result.name}</b>`);
    } catch (error) {
        console.log('Точка не принадлежит ни одному району');
    }
}

async function showDistrictStats(districtId) {
    try {
        const stats = await api.getDistrictStats(districtId);
        
        const objectsList = Object.entries(stats.objects)
            .map(([type, count]) => `${getObjectTypeRu(type)}: ${count}`)
            .join('<br>');
        
        const eventsList = Object.entries(stats.events)
            .map(([type, count]) => `${getEventTypeRu(type)}: ${count}`)
            .join('<br>');

displayResults(`
            <h4>Статистика: ${stats.district}</h4>
            <p><b>Население:</b> ${stats.population?.toLocaleString() || 'Не указано'}</p>
            <p><b>Площадь:</b> ${stats.area_km2} км²</p>
            <p><b>Объектов:</b> ${stats.total_objects}</p>
            <div style="margin-left: 10px; font-size: 0.9em;">
                ${objectsList || 'Нет данных'}
            </div>
            <p><b>Событий:</b> ${stats.total_events}</p>
            <div style="margin-left: 10px; font-size: 0.9em;">
                ${eventsList || 'Нет данных'}
            </div>
        `);
    } catch (error) {
        console.error('Ошибка получения статистики:', error);
        showError('Не удалось загрузить статистику района');
    }
}

function displayResults(html) {
    document.getElementById('results').innerHTML = html;
}

function showError(message) {
    displayResults(`<div class="error">❌ ${message}</div>`);
}

function showInfo(message) {
    displayResults(`<div class="info">ℹ️ ${message}</div>`);
}

function getObjectTypeRu(type) {
    const types = {
        hospital: 'Больница',
        school: 'Школа',
        cafe: 'Кафе',
        parking: 'Парковка',
        pharmacy: 'Аптека'
    };
    return types[type] || type;
}

function getEventTypeRu(type) {
    const types = {
        accident: 'ДТП',
        repair: 'Ремонт',
        festival: 'Мероприятие'
    };
    return types[type] || type;
}

document.addEventListener('DOMContentLoaded', initMap);