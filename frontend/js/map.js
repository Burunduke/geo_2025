let map;
let userMarker = null;
let searchCircle = null;
let currentTileLayer = null;
let currentCity = null;
let dateRangePicker = null;
let selectedEventTypes = [];
let selectedSources = [];
let allEvents = [];
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
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    })
};

async function initMap() {
    // Создание карты (Воронеж по умолчанию)
    map = L.map('map').setView([51.6606, 39.2003], 13);

    // Установка начального стиля карты
    setMapStyle('osm');

    layers.events.addTo(map);
    layers.districts.addTo(map);

    map.on('click', onMapClick);

    // Инициализация календаря
    initDateRangePicker();
    
    // Инициализация мультиселекта типов событий
    initMultiSelect();
    
    // Инициализация мультиселекта источников
    initSourceMultiSelect();
    
    // Инициализация быстрых фильтров дат
    initQuickDateFilters();

    // Загрузка списка городов
    await loadCities();

    loadEvents();
    await loadDistrictsWithRetry();

    // Инициализация селектора стиля карты
    initMapStyleSelector();
}

// Инициализация календаря с диапазоном дат
function initDateRangePicker() {
    dateRangePicker = flatpickr("#dateRangePicker", {
        mode: "range",
        dateFormat: "d.m.Y",
        locale: "ru",
        static: true,
        animate: false,
        position: "auto left",
        zIndex: 9999,
        onChange: function(selectedDates, dateStr, instance) {
            applyFilters();
        },
        onReady: function(selectedDates, dateStr, instance) {
            // Ensure calendar is visible when opened
            instance.calendar.style.opacity = "1";
            instance.calendar.style.visibility = "visible";
            instance.calendar.style.zIndex = "9999";
            instance.calendar.style.position = "absolute";
        },
        onOpen: function(selectedDates, dateStr, instance) {
            // Ensure calendar is visible when opened
            instance.calendar.style.opacity = "1";
            instance.calendar.style.visibility = "visible";
            instance.calendar.style.zIndex = "9999";
            instance.calendar.style.position = "absolute";
        }
    });
    
    // Кнопка очистки фильтра дат
    document.getElementById('clearDateFilter').addEventListener('click', () => {
        dateRangePicker.clear();
        applyFilters();
    });
}

// Инициализация мультиселекта типов событий
function initMultiSelect() {
    const header = document.getElementById('typeFilterHeader');
    const dropdown = document.getElementById('typeFilterDropdown');
    const checkboxes = document.querySelectorAll('.event-type-checkbox');
    
    // Открытие/закрытие dropdown
    header.addEventListener('click', () => {
        header.classList.toggle('active');
        dropdown.classList.toggle('active');
    });
    
    // Закрытие при клике вне элемента
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.multiselect-container')) {
            header.classList.remove('active');
            dropdown.classList.remove('active');
        }
    });
    
    // Обработка выбора чекбоксов
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            updateSelectedTypes();
            applyFilters();
        });
    });
}

// Обновление списка выбранных типов
function updateSelectedTypes() {
    const checkboxes = document.querySelectorAll('.event-type-checkbox:checked');
    selectedEventTypes = Array.from(checkboxes).map(cb => cb.value);
    
    const selectedText = document.querySelector('.selected-text');
    if (selectedEventTypes.length === 0) {
        selectedText.textContent = 'Все события';
    } else if (selectedEventTypes.length === 1) {
        const checkbox = document.querySelector(`.event-type-checkbox[value="${selectedEventTypes[0]}"]`);
        const label = checkbox.closest('.checkbox-label').querySelector('.checkbox-text').textContent;
        selectedText.textContent = label;
    } else {
        selectedText.textContent = `Выбрано: ${selectedEventTypes.length}`;
    }
}

// Инициализация мультиселекта источников
function initSourceMultiSelect() {
    const header = document.getElementById('sourceFilterHeader');
    const dropdown = document.getElementById('sourceFilterDropdown');
    const checkboxes = document.querySelectorAll('.source-checkbox');
    
    // Открытие/закрытие dropdown
    header.addEventListener('click', () => {
        header.classList.toggle('active');
        dropdown.classList.toggle('active');
    });
    
    // Закрытие при клике вне элемента
    document.addEventListener('click', (e) => {
        if (!e.target.closest('#sourceFilterHeader') && !e.target.closest('#sourceFilterDropdown')) {
            header.classList.remove('active');
            dropdown.classList.remove('active');
        }
    });
    
    // Обработка выбора чекбоксов
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            updateSelectedSources();
            applyFilters();
        });
    });
}

// Обновление списка выбранных источников
function updateSelectedSources() {
    const checkboxes = document.querySelectorAll('.source-checkbox:checked');
    selectedSources = Array.from(checkboxes).map(cb => cb.value);
    
    const selectedText = document.querySelector('#sourceFilterHeader .selected-text');
    if (selectedSources.length === 0) {
        selectedText.textContent = 'Все источники';
    } else if (selectedSources.length === 1) {
        const checkbox = document.querySelector(`.source-checkbox[value="${selectedSources[0]}"]`);
        const label = checkbox.closest('.checkbox-label').querySelector('.checkbox-text').textContent;
        selectedText.textContent = label;
    } else {
        selectedText.textContent = `Выбрано: ${selectedSources.length}`;
    }
}

// Инициализация быстрых фильтров дат
function initQuickDateFilters() {
    const quickDateButtons = document.querySelectorAll('.quick-date-btn');
    
    quickDateButtons.forEach(btn => {
        btn.addEventListener('click', async () => {
            const filter = btn.dataset.filter;
            
            // Снимаем выделение со всех кнопок
            quickDateButtons.forEach(b => b.style.background = '');
            
            // Выделяем текущую кнопку
            btn.style.background = 'linear-gradient(135deg, var(--primary-color), var(--secondary-color))';
            btn.style.color = 'white';
            
            // Очищаем календарь
            dateRangePicker.clear();
            
            // Применяем быстрый фильтр
            await applyQuickDateFilter(filter);
        });
    });
}

// Инициализация селектора стиля карты
function initMapStyleSelector() {
    const toggleBtn = document.getElementById('mapStyleToggle');
    const dropdown = document.getElementById('mapStyleDropdown');
    const styleOptions = document.querySelectorAll('.style-option');
    
    // Открытие/закрытие dropdown
    toggleBtn.addEventListener('click', () => {
        toggleBtn.classList.toggle('active');
        dropdown.classList.toggle('active');
    });
    
    // Закрытие при клике вне элемента
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.map-style-selector')) {
            toggleBtn.classList.remove('active');
            dropdown.classList.remove('active');
        }
    });
    
    // Обработка выбора стиля
    styleOptions.forEach(option => {
        option.addEventListener('click', () => {
            const style = option.dataset.style;
            setMapStyle(style);
            
            // Обновляем активный класс
            styleOptions.forEach(opt => opt.classList.remove('active'));
            option.classList.add('active');
            
            // Закрываем dropdown
            toggleBtn.classList.remove('active');
            dropdown.classList.remove('active');
        });
    });
    
    // Устанавливаем активный стиль по умолчанию
    const defaultOption = document.querySelector('.style-option[data-style="osm"]');
    if (defaultOption) {
        defaultOption.classList.add('active');
    }
}

// Применение быстрого фильтра дат
async function applyQuickDateFilter(filter) {
    try {
        let result;
        
        switch(filter) {
            case 'today':
                result = await api.getTodayEvents();
                displayFilteredEvents(result.events, `События сегодня (${result.count})`);
                break;
            case 'tomorrow':
                result = await api.getUpcomingEvents(1, 100);
                const tomorrow = new Date();
                tomorrow.setDate(tomorrow.getDate() + 1);
                const tomorrowEvents = result.events.filter(evt => {
                    const evtDate = new Date(evt.start_time);
                    return evtDate.toDateString() === tomorrow.toDateString();
                });
                displayFilteredEvents(tomorrowEvents, `События завтра (${tomorrowEvents.length})`);
                break;
            case 'week':
                result = await api.getUpcomingEvents(7, 100);
                displayFilteredEvents(result.events, `События на неделю (${result.count})`);
                break;
            case 'month':
                result = await api.getUpcomingEvents(30, 200);
                displayFilteredEvents(result.events, `События на месяц (${result.count})`);
                break;
        }
    } catch (error) {
        console.error('Ошибка фильтрации по дате:', error);
        showError('Ошибка при фильтрации событий');
    }
}

// Применение всех фильтров
async function applyFilters() {
    try {
        // Получаем все события
        allEvents = await api.getEvents(null, null, false);
        
        let filteredEvents = [...allEvents];
        
        // Фильтр по типам событий
        if (selectedEventTypes.length > 0) {
            filteredEvents = filteredEvents.filter(evt =>
                selectedEventTypes.includes(evt.event_type)
            );
        }
        
        // Фильтр по источникам
        if (selectedSources.length > 0) {
            filteredEvents = filteredEvents.filter(evt =>
                selectedSources.includes(evt.source)
            );
        }
        
        // Фильтр по датам из календаря
        const selectedDates = dateRangePicker.selectedDates;
        if (selectedDates.length === 2) {
            const startDate = selectedDates[0];
            const endDate = selectedDates[1];
            endDate.setHours(23, 59, 59, 999); // Включаем весь конечный день
            
            filteredEvents = filteredEvents.filter(evt => {
                const evtDate = new Date(evt.start_time);
                return evtDate >= startDate && evtDate <= endDate;
            });
        }
        
        // Отображаем отфильтрованные события
        displayFilteredEvents(filteredEvents);
        
    } catch (error) {
        console.error('Ошибка применения фильтров:', error);
        showError('Ошибка при фильтрации событий');
    }
}

// Отображение отфильтрованных событий
function displayFilteredEvents(events, title = null) {
    layers.events.clearLayers();
    
    events.forEach(evt => {
        const icon = eventIcons[evt.event_type] || eventIcons.festival;
        const marker = L.marker([evt.lat, evt.lon], { icon: icon });
        
        const startTime = new Date(evt.start_time).toLocaleString('ru-RU');
        const endTime = evt.end_time ? new Date(evt.end_time).toLocaleString('ru-RU') : 'Не указано';
        
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
            popupContent += `<img src="${evt.image_url}" alt="${evt.title}" style="max-width: 200px; margin-top: 10px; border-radius: 8px;">`;
        }
        
        popupContent += `</div>`;
        
        marker.bindPopup(popupContent, { maxWidth: 300 });
        marker.addTo(layers.events);
    });
    
    // Обновляем счетчик событий
    updateEventCount(events.length);
    
    // Отображаем список событий
    if (title) {
        displayEventsList(events, title);
    }
    
    console.log(`Отображено событий: ${events.length}`);
}

// Обновление счетчика событий
function updateEventCount(count) {
    const eventCountElement = document.getElementById('eventCount');
    const span = eventCountElement.querySelector('span');
    span.textContent = `${count} ${getEventWord(count)}`;
}

// Склонение слова "событие"
function getEventWord(count) {
    const lastDigit = count % 10;
    const lastTwoDigits = count % 100;
    
    if (lastTwoDigits >= 11 && lastTwoDigits <= 19) {
        return 'событий';
    }
    
    if (lastDigit === 1) {
        return 'событие';
    }
    
    if (lastDigit >= 2 && lastDigit <= 4) {
        return 'события';
    }
    
    return 'событий';
}

function setMapStyle(styleKey) {
    if (currentTileLayer) {
        map.removeLayer(currentTileLayer);
    }

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
        allEvents = events;
        displayFilteredEvents(events);
    } catch (error) {
        console.error('Ошибка загрузки событий:', error);
        showError('Не удалось загрузить события');
    }
}

async function loadDistricts() {
    try {
        console.log('Начинаю загрузку районов...');
        const districts = await api.getDistricts();
        
        if (!districts || !Array.isArray(districts)) {
            console.error('Получены некорректные данные районов:', districts);
            showError('Ошибка загрузки районов: некорректные данные');
            return;
        }
        
        console.log(`Получено районов от API: ${districts.length}`);
        layers.districts.clearLayers();
        
        districts.forEach((district, index) => {
            try {
                if (!district.geometry || !district.name) {
                    console.warn(`Район ${index} пропущен - отсутствуют необходимые поля:`, district);
                    return;
                }
                
                const geoJsonLayer = L.geoJSON(district.geometry, {
                    style: {
                        color: '#667eea',
                        weight: 2,
                        fillOpacity: 0.1
                    },
                    onEachFeature: function (feature, layer) {
                        layer.on('error', function(e) {
                            console.error(`Ошибка отображения района "${district.name}":`, e);
                        });
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
                
            } catch (error) {
                console.error(`Ошибка обработки района ${index} (${district.name}):`, error);
            }
        });

        console.log(`Загружено районов: ${districts.length}`);
        
        if (!map.hasLayer(layers.districts)) {
            map.addLayer(layers.districts);
            console.log('Слой районов добавлен на карту');
        }
        
    } catch (error) {
        console.error('Ошибка загрузки районов:', error);
        showError('Не удалось загрузить районы: ' + error.message);
    }
}

async function loadDistrictsWithRetry(maxRetries = 3, retryDelay = 2000) {
    let retryCount = 0;
    let lastError = null;
    
    while (retryCount < maxRetries) {
        try {
            console.log(`Попытка загрузки районов (${retryCount + 1}/${maxRetries})`);
            await loadDistricts();
            
            if (layers.districts.getLayers().length > 0) {
                console.log('Районы успешно загружены');
                return;
            } else {
                console.warn('Районы загрузились, но слой пуст');
                lastError = new Error('Слой районов пуст после загрузки');
            }
        } catch (error) {
            lastError = error;
            console.error(`Ошибка при попытке ${retryCount + 1}:`, error);
        }
        
        retryCount++;
        
        if (retryCount < maxRetries) {
            console.log(`Повторная попытка через ${retryDelay} мс...`);
            await new Promise(resolve => setTimeout(resolve, retryDelay));
            retryDelay *= 1.5;
        }
    }
    
    if (lastError) {
        console.error(`Не удалось загрузить районы после ${maxRetries} попыток:`, lastError);
        showError(`Не удалось загрузить районы.`);
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
        
        await loadEvents();
        
    } catch (error) {
        console.error('Ошибка импорта:', error);
        showError('Ошибка при импорте событий с Яндекс.Афиши');
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

async function loadCities() {
    try {
        const result = await api.getCities();
        const citySelect = document.getElementById('citySelect');
        
        citySelect.innerHTML = '';
        
        result.cities.forEach(city => {
            const option = document.createElement('option');
            option.value = city.slug;
            option.textContent = city.name;
            option.dataset.lat = city.lat;
            option.dataset.lon = city.lon;
            option.dataset.zoom = city.zoom;
            
            if (city.slug === 'voronezh') {
                option.selected = true;
                currentCity = city;
            }
            
            citySelect.appendChild(option);
        });
        
        citySelect.addEventListener('change', changeCity);
        
        console.log(`Загружено городов: ${result.cities.length}`);
    } catch (error) {
        console.error('Ошибка загрузки городов:', error);
        showError('Не удалось загрузить список городов');
    }
}

async function changeCity() {
    const citySelect = document.getElementById('citySelect');
    const selectedOption = citySelect.options[citySelect.selectedIndex];
    
    if (!selectedOption) return;
    
    const lat = parseFloat(selectedOption.dataset.lat);
    const lon = parseFloat(selectedOption.dataset.lon);
    const zoom = parseInt(selectedOption.dataset.zoom);
    const cityName = selectedOption.textContent;
    
    map.setView([lat, lon], zoom);
    
    currentCity = {
        slug: selectedOption.value,
        name: cityName,
        lat: lat,
        lon: lon,
        zoom: zoom
    };
    
    await loadEvents();
    
    try {
        await loadDistricts();
        
        const mapBounds = map.getBounds();
        const districtsInView = layers.districts.getLayers().filter(layer => {
            const layerBounds = layer.getBounds();
            return layerBounds && mapBounds.intersects(layerBounds);
        });
        
        if (districtsInView.length === 0) {
            console.log(`Районы для города ${cityName} не найдены в области видимости, начинаем загрузку...`);
            showInfo(`Загрузка районов для города ${cityName}...`);
            
            const result = await api.importDistrictsFromOSM(cityName, 'Россия');
            
            if (result.success && result.statistics.imported > 0) {
                showInfo(`Успешно загружено ${result.statistics.imported} районов для города ${cityName}`);
                await loadDistricts();
            } else {
                showError(`Не удалось загрузить районы для города ${cityName}`);
            }
        }
    } catch (error) {
        console.error('Ошибка при проверке/загрузке районов:', error);
        showError('Ошибка при загрузке районов');
    }
    
    console.log(`Выбран город: ${cityName}`);
}

document.addEventListener('DOMContentLoaded', initMap);