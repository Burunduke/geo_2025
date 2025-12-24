// map.js - Инициализация и управление картой

let map;
let userMarker = null;
let searchCircle = null;
let layers = {
    objects: L.layerGroup(),
    events: L.layerGroup(),
    districts: L.layerGroup()
};

// Иконки для разных типов объектов
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

// Инициализация карты
function initMap() {
    // Создание карты (центр - Москва)
    map = L.map('map').setView([55.7558, 37.6173], 13);

    // Добавление тайлов OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);

    // Добавление слоёв на карту
    layers.objects.addTo(map);
    layers.events.addTo(map);
    // districts слой добавляется по клику чекбокса

    // Обработчик клика по карте
    map.on('click', onMapClick);

    // Загрузка начальных данных
    loadObjects();
    loadEvents();
    loadDistricts();

    // Обработчики чекбоксов
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

// Клик по карте
function onMapClick(e) {
    const lat = e.latlng.lat;
    const lon = e.latlng.lng;
// Установка маркера пользователя
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

    // Определение района
    findDistrict(lat, lon);
}

// Загрузка объектов
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

// Загрузка событий
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

// Загрузка районов
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

// Поиск объектов в радиусе
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
        
        // Удаление старого круга
        if (searchCircle) {
            map.removeLayer(searchCircle);
        }
        
        // Рисование круга поиска
        searchCircle = L.circle([latlng.lat, latlng.lng], {
            radius: radius,
            color: 'blue',
            fillOpacity: 0.1
        }).addTo(map);

        // Отображение результатов
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

        // Подсветка найденных объектов
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

// Поиск ближайшего объекта
async function findNearest() {
    if (!userMarker) {
        showError('Сначала кликните на карту, чтобы выбрать точку');
        return;
    }

    const objectType = document.getElementById('nearestType').value || null;
    const latlng = userMarker.getLatLng();

    try {
        const result = await api.getNearestObject(latlng.lat, latlng.lng, objectType);
        
        // Рисование линии к ближайшему объекту
        const polyline = L.polyline([
            [latlng.lat, latlng.lng],
            [result.lat, result.lon]
        ], { color: 'red', weight: 3 }).addTo(map);

        // Центрирование карты
        map.fitBounds(polyline.getBounds());

        // Отображение результата
        displayResults(`
            <h4>Ближайший объект</h4>
            <div class="result-item">
                <b>${result.name}</b><br>
                Тип: ${getObjectTypeRu(result.type)}<br>
                Адрес: ${result.address || 'Не указан'}<br>
                Расстояние: ${result.distance.toFixed(0)} м
            </div>
        `);

        // Маркер с popup
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

// Найти район по точке
async function findDistrict(lat, lon) {
    try {
        const result = await api.findDistrictByPoint(lat, lon);
        showInfo(`Вы находитесь в районе: <b>${result.name}</b>`);
    } catch (error) {
        console.log('Точка не принадлежит ни одному району');
    }
}

// Показать статистику района
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

// Вспомогательные функции
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

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', initMap);