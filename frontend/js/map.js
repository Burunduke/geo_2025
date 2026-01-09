let map;
let userMarker = null;
let searchCircle = null;
let currentTileLayer = null;
let layers = {
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

// Иконки для разных типов событий
const eventIcons = {
    concert: L.icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-violet.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    }),
    theater: L.icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    }),
    exhibition: L.icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-yellow.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    }),
    sport: L.icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    }),
    festival: L.icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-orange.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    }),
    repair: L.icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-grey.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    }),
    accident: L.icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-black.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    }),
    city_event: L.icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/marker/img/marker-icon-2x-blue.png',
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

    layers.events.addTo(map);

    map.on('click', onMapClick);

    loadEvents();
    loadDistricts();

    // Обработчик смены стиля карты
    document.getElementById('mapStyle').addEventListener('change', (e) => {
        setMapStyle(e.target.value);
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
                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-gold.png',
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

async function loadEvents(type = null, source = null, upcomingOnly = false) {
    try {
        const events = await api.getEvents(type, source, upcomingOnly);
        layers.events.clearLayers();

        events.forEach(evt => {
            const icon = eventIcons[evt.event_type] || eventIcons.festival;
            const marker = L.marker([evt.lat, evt.lon], { icon: icon });
            
            const startTime = new Date(evt.start_time).toLocaleString('ru-RU');
            const endTime = evt.end_time ? new Date(evt.end_time).toLocaleString('ru-RU') : 'Не указано';
            
            // Формируем popup с расширенной информацией
            let popupContent = `
                <div class="event-popup">
                    <h3>${evt.title}</h3>
                    <p><strong>Тип:</strong> ${getEventTypeRu(evt.event_type)}</p>
            `;
            
            if (evt.venue) {
                popupContent += `<p><strong>Место:</strong> ${evt.venue}</p>`;
            }
            
            if (evt.description) {
                popupContent += `<p><strong>Описание:</strong> ${evt.description}</p>`;
            }
            
            popupContent += `
                <p><strong>Начало:</strong> ${startTime}</p>
                <p><strong>Конец:</strong> ${endTime}</p>
            `;
            
            if (evt.price) {
                popupContent += `<p><strong>Цена:</strong> ${evt.price}</p>`;
            }
            
            if (evt.source) {
                popupContent += `<p><strong>Источник:</strong> ${getSourceRu(evt.source)}</p>`;
            }
            
            if (evt.source_url) {
                popupContent += `<p><a href="${evt.source_url}" target="_blank">Подробнее →</a></p>`;
            }
            
            if (evt.image_url) {
                popupContent += `<img src="${evt.image_url}" alt="${evt.title}" style="max-width: 200px; margin-top: 10px;">`;
            }
            
            popupContent += `</div>`;
            
            marker.bindPopup(popupContent, { maxWidth: 300 });
            marker.addTo(layers.events);
        });

        console.log(`Загружено событий: ${events.length}`);
        showInfo(`Загружено событий: ${events.length}`);
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

async function filterEvents() {
    const eventType = document.getElementById('eventTypeFilter').value || null;
    const source = document.getElementById('sourceFilter').value || null;
    await loadEvents(eventType, source, false);
}

async function filterByDate() {
    const dateFilter = document.getElementById('dateFilter').value;
    
    try {
        let result;
        
        switch(dateFilter) {
            case 'today':
                result = await api.getTodayEvents();
                displayEventsList(result.events, `События сегодня (${result.count})`);
                break;
            case 'tomorrow':
                result = await api.getUpcomingEvents(1, 100);
                const tomorrow = new Date();
                tomorrow.setDate(tomorrow.getDate() + 1);
                const tomorrowEvents = result.events.filter(evt => {
                    const evtDate = new Date(evt.start_time);
                    return evtDate.toDateString() === tomorrow.toDateString();
                });
                displayEventsList(tomorrowEvents, `События завтра (${tomorrowEvents.length})`);
                break;
            case 'week':
                result = await api.getUpcomingEvents(7, 100);
                displayEventsList(result.events, `События на неделю (${result.count})`);
                break;
            case 'month':
                result = await api.getUpcomingEvents(30, 200);
                displayEventsList(result.events, `События на месяц (${result.count})`);
                break;
            default:
                await loadEvents();
        }
    } catch (error) {
        console.error('Ошибка фильтрации по дате:', error);
        showError('Ошибка при фильтрации событий');
    }
}

function displayEventsList(events, title) {
    if (!events || events.length === 0) {
        displayResults(`<h4>${title}</h4><p>Событий не найдено</p>`);
        return;
    }
    
    const eventsList = events.map(evt => {
        const startTime = new Date(evt.start_time).toLocaleString('ru-RU');
        return `
            <div class="result-item" onclick="focusOnEvent(${evt.lat}, ${evt.lon})">
                <b>${evt.title}</b><br>
                <small>${getEventTypeRu(evt.event_type)}</small><br>
                ${evt.venue ? `📍 ${evt.venue}<br>` : ''}
                🕐 ${startTime}<br>
                ${evt.price ? `💰 ${evt.price}` : ''}
            </div>
        `;
    }).join('');
    
    displayResults(`<h4>${title}</h4>${eventsList}`);
}

function focusOnEvent(lat, lon) {
    map.setView([lat, lon], 16);
}

async function importFromAfisha() {
    displayResults('<h4>Импорт событий...</h4><p>Пожалуйста, подождите...</p>');
    
    try {
        const result = await api.importFromAfisha('voronezh', null, 30, 50);
        
        displayResults(`
            <h4>✅ Импорт завершен</h4>
            <p><strong>Всего обработано:</strong> ${result.statistics.total}</p>
            <p><strong>Импортировано:</strong> ${result.statistics.imported}</p>
            <p><strong>Дубликатов:</strong> ${result.statistics.duplicates}</p>
            <p><strong>Ошибок:</strong> ${result.statistics.errors}</p>
            ${result.statistics.skipped_no_coords ? `<p><strong>Пропущено (нет координат):</strong> ${result.statistics.skipped_no_coords}</p>` : ''}
        `);
        
        // Перезагрузить события на карте
        await loadEvents();
        
    } catch (error) {
        console.error('Ошибка импорта:', error);
        showError('Ошибка при импорте событий с Яндекс.Афиши');
    }
}

async function importDistrictsFromOSM() {
    displayResults('<h4>Импорт районов из OpenStreetMap...</h4><p>Пожалуйста, подождите, это может занять до 30 секунд...</p>');
    
    try {
        const result = await api.importDistrictsFromOSM('Воронеж', 'Россия');
        
        displayResults(`
            <h4>✅ Импорт районов завершен</h4>
            <p><strong>Город:</strong> ${result.city}</p>
            <p><strong>Всего обработано:</strong> ${result.statistics.total}</p>
            <p><strong>Импортировано новых:</strong> ${result.statistics.imported}</p>
            <p><strong>Обновлено:</strong> ${result.statistics.updated}</p>
            <p><strong>Ошибок:</strong> ${result.statistics.errors}</p>
        `);
        
        // Перезагрузить районы на карте
        await loadDistricts();
        
        // Включить отображение районов
        document.getElementById('showDistricts').checked = true;
        map.addLayer(layers.districts);
        
    } catch (error) {
        console.error('Ошибка импорта районов:', error);
        showError('Ошибка при импорте районов из OpenStreetMap. Попробуйте позже.');
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
        
        const eventsList = Object.entries(stats.events)
            .map(([type, count]) => `${getEventTypeRu(type)}: ${count}`)
            .join('<br>');

        displayResults(`
            <h4>Статистика: ${stats.district}</h4>
            <p><b>Население:</b> ${stats.population?.toLocaleString() || 'Не указано'}</p>
            <p><b>Площадь:</b> ${stats.area_km2} км²</p>
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

function getEventTypeRu(type) {
    const types = {
        concert: '🎵 Концерт',
        theater: '🎭 Театр',
        exhibition: '🖼️ Выставка',
        sport: '⚽ Спорт',
        festival: '🎪 Фестиваль',
        repair: '🚧 Ремонт',
        accident: '🚗 ДТП',
        city_event: '🏛️ Городское мероприятие'
    };
    return types[type] || type;
}

function getSourceRu(source) {
    const sources = {
        yandex_afisha: 'Яндекс.Афиша',
        manual: 'Ручной ввод',
        telegram: 'Telegram'
    };
    return sources[source] || source;
}

document.addEventListener('DOMContentLoaded', initMap);