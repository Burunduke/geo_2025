let map;
let userMarker = null;
let searchCircle = null;
let currentTileLayer = null;
let currentCity = null;
let dateRangePicker = null;
let selectedEventTypes = [];
let selectedSources = [];
let allEvents = [];
let displayLimit = 500; // По умолчанию показываем 500 событий
let layers = {
    events: L.layerGroup()
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
    // Создание карты (Санкт-Петербург по умолчанию)
    map = L.map('map').setView([59.9343, 30.3351], 11);

    // Установка начального стиля карты
    setMapStyle('osm');

    layers.events.addTo(map);

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

    // Инициализация селектора стиля карты
    initMapStyleSelector();
    
    // Инициализация селектора лимита отображения
    initDisplayLimitSelector();
}

// Инициализация календаря с диапазоном дат
function initDateRangePicker() {
    const inputElement = document.getElementById('dateRangePicker');
    
    if (!inputElement) {
        console.error('Элемент dateRangePicker не найден!');
        return;
    }
    
    try {
        dateRangePicker = flatpickr(inputElement, {
            mode: "range",
            dateFormat: "d.m.Y",
            locale: "ru",
            static: true,
            animate: false,
            position: "auto left",
            onClose: function(selectedDates, dateStr, instance) {
                // Применяем фильтр только после закрытия календаря
                console.log('Календарь закрыт, выбрано дат:', selectedDates.length);
                if (selectedDates.length > 0) {
                    console.log('Выбранные даты:', selectedDates.map(d => d.toISOString()));
                }
                applyFilters();
            }
        });
        
        console.log('Flatpickr инициализирован:', dateRangePicker !== null);
    } catch (error) {
        console.error('Ошибка инициализации Flatpickr:', error);
    }
    
    // Кнопка очистки фильтра дат
    const clearBtn = document.getElementById('clearDateFilter');
    if (clearBtn) {
        clearBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('Нажата кнопка очистки фильтра дат');
            
            if (dateRangePicker && typeof dateRangePicker.clear === 'function') {
                dateRangePicker.clear();
                console.log('Календарь очищен');
            } else {
                console.error('dateRangePicker.clear не является функцией');
                // Альтернативный способ очистки
                if (inputElement) {
                    inputElement.value = '';
                }
            }
            
            // Снимаем выделение с кнопок быстрых фильтров
            const quickDateButtons = document.querySelectorAll('.quick-date-btn');
            quickDateButtons.forEach(b => {
                b.style.background = '';
                b.style.color = '';
            });
            
            applyFilters();
        });
        console.log('Обработчик кнопки очистки установлен');
    } else {
        console.error('Кнопка clearDateFilter не найдена!');
    }
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
    console.log(`Найдено кнопок быстрых фильтров: ${quickDateButtons.length}`);
    
    quickDateButtons.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            const filter = btn.dataset.filter;
            console.log(`Нажата кнопка быстрого фильтра: ${filter}`);
            
            // Снимаем выделение со всех кнопок
            quickDateButtons.forEach(b => {
                b.style.background = '';
                b.style.color = '';
            });
            
            // Выделяем текущую кнопку
            btn.style.background = 'linear-gradient(135deg, var(--primary-color), var(--secondary-color))';
            btn.style.color = 'white';
            
            // Очищаем календарь
            if (dateRangePicker && typeof dateRangePicker.clear === 'function') {
                dateRangePicker.clear();
            } else if (dateRangePicker && dateRangePicker.input) {
                dateRangePicker.input.value = '';
            }
            
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

// Инициализация селектора лимита отображения
function initDisplayLimitSelector() {
    const limitSelect = document.getElementById('displayLimit');
    
    if (!limitSelect) {
        console.error('Элемент displayLimit не найден!');
        return;
    }
    
    limitSelect.addEventListener('change', () => {
        const value = parseInt(limitSelect.value);
        displayLimit = value;
        console.log(`Лимит отображения изменен на: ${displayLimit === -1 ? 'все' : displayLimit}`);
        
        // Применяем фильтры заново с новым лимитом
        applyFilters();
    });
    
    console.log('Селектор лимита отображения инициализирован');
}

// Применение быстрого фильтра дат
async function applyQuickDateFilter(filter) {
    try {
        console.log(`Применение быстрого фильтра: ${filter}`);
        const city = currentCity ? currentCity.slug : 'moscow';
        
        // Получаем все события города
        const allCityEvents = await api.getCityEvents(city, {
            upcomingOnly: false
        });
        
        console.log(`Загружено событий для фильтра: ${allCityEvents.length}`);
        
        const now = new Date();
        let filteredEvents = [];
        let title = '';
        
        switch(filter) {
            case 'today':
                const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0, 0);
                const todayEnd = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59, 999);
                console.log(`Фильтр "Сегодня": ${todayStart.toISOString()} - ${todayEnd.toISOString()}`);
                
                filteredEvents = allCityEvents.filter(evt => {
                    const evtDate = new Date(evt.start_time);
                    return evtDate >= todayStart && evtDate <= todayEnd;
                });
                title = `События сегодня (${filteredEvents.length})`;
                break;
                
            case 'tomorrow':
                const tomorrow = new Date(now);
                tomorrow.setDate(tomorrow.getDate() + 1);
                const tomorrowStart = new Date(tomorrow.getFullYear(), tomorrow.getMonth(), tomorrow.getDate(), 0, 0, 0, 0);
                const tomorrowEnd = new Date(tomorrow.getFullYear(), tomorrow.getMonth(), tomorrow.getDate(), 23, 59, 59, 999);
                console.log(`Фильтр "Завтра": ${tomorrowStart.toISOString()} - ${tomorrowEnd.toISOString()}`);
                
                filteredEvents = allCityEvents.filter(evt => {
                    const evtDate = new Date(evt.start_time);
                    return evtDate >= tomorrowStart && evtDate <= tomorrowEnd;
                });
                title = `События завтра (${filteredEvents.length})`;
                break;
                
            case 'week':
                const weekEnd = new Date(now);
                weekEnd.setDate(weekEnd.getDate() + 7);
                weekEnd.setHours(23, 59, 59, 999);
                console.log(`Фильтр "Неделя": ${now.toISOString()} - ${weekEnd.toISOString()}`);
                
                filteredEvents = allCityEvents.filter(evt => {
                    const evtDate = new Date(evt.start_time);
                    return evtDate >= now && evtDate <= weekEnd;
                });
                title = `События на неделю (${filteredEvents.length})`;
                break;
                
            case 'month':
                const monthEnd = new Date(now);
                monthEnd.setDate(monthEnd.getDate() + 30);
                monthEnd.setHours(23, 59, 59, 999);
                console.log(`Фильтр "Месяц": ${now.toISOString()} - ${monthEnd.toISOString()}`);
                
                filteredEvents = allCityEvents.filter(evt => {
                    const evtDate = new Date(evt.start_time);
                    return evtDate >= now && evtDate <= monthEnd;
                });
                title = `События на месяц (${filteredEvents.length})`;
                break;
        }
        
        console.log(`Отфильтровано событий: ${filteredEvents.length}`);
        
        // Применяем дополнительные фильтры (типы и источники)
        if (selectedEventTypes.length > 0) {
            filteredEvents = filteredEvents.filter(evt =>
                selectedEventTypes.includes(evt.event_type)
            );
            console.log(`После фильтра по типам: ${filteredEvents.length}`);
        }
        
        if (selectedSources.length > 0) {
            filteredEvents = filteredEvents.filter(evt =>
                selectedSources.includes(evt.source)
            );
            console.log(`После фильтра по источникам: ${filteredEvents.length}`);
        }
        
        // Обновляем allEvents для других фильтров
        allEvents = allCityEvents;
        
        displayFilteredEvents(filteredEvents, title);
        
    } catch (error) {
        console.error('Ошибка фильтрации по дате:', error);
        showError('Ошибка при фильтрации событий');
    }
}

// Применение всех фильтров
async function applyFilters() {
    try {
        console.log('=== НАЧАЛО ПРИМЕНЕНИЯ ФИЛЬТРОВ ===');
        
        // Получаем город
        const city = currentCity ? currentCity.slug : 'moscow';
        
        console.log(`Применение фильтров для города: ${city}`);
        console.log(`Выбранные типы: ${selectedEventTypes.join(', ') || 'все'}`);
        console.log(`Выбранные источники: ${selectedSources.join(', ') || 'все'}`);
        console.log(`Календарь инициализирован: ${dateRangePicker !== null}`);
        
        if (dateRangePicker) {
            console.log(`Выбрано дат в календаре: ${dateRangePicker.selectedDates ? dateRangePicker.selectedDates.length : 0}`);
            if (dateRangePicker.selectedDates && dateRangePicker.selectedDates.length > 0) {
                console.log(`Даты:`, dateRangePicker.selectedDates.map(d => d.toISOString()));
            }
        }
        
        // Получаем все события для текущего города
        const eventsData = await api.getCityEvents(city, {
            upcomingOnly: false
        });
        
        // Validate response
        if (!eventsData || !Array.isArray(eventsData)) {
            console.error('Invalid events data received:', eventsData);
            allEvents = [];
            displayFilteredEvents([]);
            return;
        }
        
        allEvents = eventsData;
        console.log(`Загружено событий: ${allEvents.length}`);
        
        let filteredEvents = [...allEvents];
        
        // Фильтр по типам событий
        if (selectedEventTypes.length > 0) {
            filteredEvents = filteredEvents.filter(evt =>
                selectedEventTypes.includes(evt.event_type)
            );
            console.log(`После фильтра по типам: ${filteredEvents.length}`);
        }
        
        // Фильтр по источникам
        if (selectedSources.length > 0) {
            filteredEvents = filteredEvents.filter(evt =>
                selectedSources.includes(evt.source)
            );
            console.log(`После фильтра по источникам: ${filteredEvents.length}`);
        }
        
        console.log(`Всего событий перед фильтром по датам: ${filteredEvents.length}`);
        
        // Фильтр по датам из календаря
        if (dateRangePicker && dateRangePicker.selectedDates && dateRangePicker.selectedDates.length > 0) {
            console.log('Применяем фильтр по датам из календаря');
            const selectedDates = dateRangePicker.selectedDates;
            
            if (selectedDates.length === 1) {
                // Одна дата выбрана - фильтруем события на этот день
                const selectedDate = new Date(selectedDates[0]);
                // Создаем начало и конец дня в локальном времени
                const startOfDay = new Date(selectedDate.getFullYear(), selectedDate.getMonth(), selectedDate.getDate(), 0, 0, 0, 0);
                const endOfDay = new Date(selectedDate.getFullYear(), selectedDate.getMonth(), selectedDate.getDate(), 23, 59, 59, 999);
                
                console.log(`Фильтр по одной дате: ${startOfDay.toLocaleDateString('ru-RU')}`);
                console.log(`Диапазон времени: ${startOfDay.toISOString()} - ${endOfDay.toISOString()}`);
                
                filteredEvents = filteredEvents.filter(evt => {
                    const evtDate = new Date(evt.start_time);
                    const isInRange = evtDate >= startOfDay && evtDate <= endOfDay;
                    if (!isInRange) {
                        console.log(`Событие "${evt.title}" (${evtDate.toISOString()}) не попало в диапазон`);
                    }
                    return isInRange;
                });
                console.log(`После фильтра по дате: ${filteredEvents.length}`);
            } else if (selectedDates.length === 2) {
                // Диапазон дат выбран
                const startDate = new Date(selectedDates[0]);
                const endDate = new Date(selectedDates[1]);
                // Создаем начало первого дня и конец последнего дня в локальном времени
                const startOfRange = new Date(startDate.getFullYear(), startDate.getMonth(), startDate.getDate(), 0, 0, 0, 0);
                const endOfRange = new Date(endDate.getFullYear(), endDate.getMonth(), endDate.getDate(), 23, 59, 59, 999);
                
                console.log(`Фильтр по диапазону: ${startOfRange.toLocaleDateString('ru-RU')} - ${endOfRange.toLocaleDateString('ru-RU')}`);
                console.log(`Диапазон времени: ${startOfRange.toISOString()} - ${endOfRange.toISOString()}`);
                
                filteredEvents = filteredEvents.filter(evt => {
                    const evtDate = new Date(evt.start_time);
                    const isInRange = evtDate >= startOfRange && evtDate <= endOfRange;
                    if (!isInRange) {
                        console.log(`Событие "${evt.title}" (${evtDate.toISOString()}) не попало в диапазон`);
                    }
                    return isInRange;
                });
                console.log(`После фильтра по датам: ${filteredEvents.length}`);
            }
        }
        
        // Отображаем отфильтрованные события
        console.log(`Итого событий после всех фильтров: ${filteredEvents.length}`);
        console.log('=== КОНЕЦ ПРИМЕНЕНИЯ ФИЛЬТРОВ ===');
        displayFilteredEvents(filteredEvents);
        
    } catch (error) {
        console.error('Ошибка применения фильтров:', error);
        console.error('Детали ошибки:', error.message, error.stack);
        showError(`Ошибка при фильтрации событий: ${error.message}`);
    }
}

// Отображение отфильтрованных событий
function displayFilteredEvents(events, title = null) {
    layers.events.clearLayers();
    
    // Применяем лимит отображения
    let eventsToDisplay = events;
    let totalEvents = events.length;
    
    if (displayLimit > 0 && events.length > displayLimit) {
        eventsToDisplay = events.slice(0, displayLimit);
        console.log(`Ограничение отображения: показано ${displayLimit} из ${totalEvents} событий`);
    }
    
    eventsToDisplay.forEach(evt => {
        const icon = eventIcons[evt.event_type] || eventIcons.festival;
        const marker = L.marker([evt.lat, evt.lon], { icon: icon });
        
        // Форматируем даты с учетом часового пояса
        const startDate = new Date(evt.start_time);
        const startTime = formatEventDate(startDate);
        
        let endTime = 'Не указано';
        if (evt.end_time) {
            const endDate = new Date(evt.end_time);
            // Проверяем, не является ли это "бесконечной" датой (круглогодичное событие)
            if (endDate.getFullYear() > 2100) {
                endTime = 'Постоянная экспозиция';
            } else {
                endTime = formatEventDate(endDate);
            }
        }
        
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
    
    // Обновляем счетчик событий (показываем общее количество и отображаемое)
    updateEventCount(eventsToDisplay.length, totalEvents);
    
    // Отображаем список событий
    if (title) {
        displayEventsList(events, title);
    }
    
    console.log(`Отображено событий: ${events.length}`);
}

// Обновление счетчика событий
function updateEventCount(displayedCount, totalCount = null) {
    const eventCountElement = document.getElementById('eventCount');
    const span = eventCountElement.querySelector('span');
    
    if (totalCount !== null && displayedCount < totalCount) {
        span.textContent = `${displayedCount} из ${totalCount} ${getEventWord(totalCount)}`;
    } else {
        span.textContent = `${displayedCount} ${getEventWord(displayedCount)}`;
    }
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
}

async function loadEvents(type = null, source = null, upcomingOnly = false) {
    try {
        const city = currentCity ? currentCity.slug : 'moscow';
        const events = await api.getCityEvents(city, {
            eventType: type,
            upcomingOnly: upcomingOnly
        });
        allEvents = events;
        displayFilteredEvents(events);
    } catch (error) {
        console.error('Ошибка загрузки событий:', error);
        showError('Не удалось загрузить события');
    }
}

function displayEventsList(events, title) {
    if (!events || events.length === 0) {
        displayResults(`<h4>${title}</h4><p>Событий не найдено</p>`);
        return;
    }
    
    const eventsList = events.map(evt => {
        const startTime = formatEventDate(new Date(evt.start_time));
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

async function importFromKudaGo() {
    const city = currentCity ? currentCity.slug : 'voronezh';
    const cityName = currentCity ? currentCity.name : 'Воронеж';
    
    displayResults(`<h4>Импорт из KudaGo для ${cityName}...</h4><p>Загружаем события...<br>Пожалуйста, подождите...</p>`);
    
    try {
        const result = await api.importKudaGoEvents(city, null, 30);
        displayImportResult(result, 'KudaGo');
        await loadEvents();
    } catch (error) {
        console.error('Ошибка импорта KudaGo:', error);
        showError(`Ошибка при импорте событий из KudaGo для ${cityName}`);
    }
}

async function importFromYandex() {
    const city = currentCity ? currentCity.slug : 'voronezh';
    const cityName = currentCity ? currentCity.name : 'Воронеж';
    
    displayResults(`<h4>Импорт из Яндекс.Афиши для ${cityName}...</h4><p>Загружаем события...<br>Пожалуйста, подождите...</p>`);
    
    try {
        const result = await api.importYandexEvents(city, null, 30);
        displayImportResult(result, 'Яндекс.Афиша');
        await loadEvents();
    } catch (error) {
        console.error('Ошибка импорта Яндекс.Афиши:', error);
        showError(`Ошибка при импорте событий из Яндекс.Афиши для ${cityName}`);
    }
}

async function importTestMoscow() {
    const city = currentCity ? currentCity.slug : 'spb';
    const cityName = currentCity ? currentCity.name : 'Санкт-Петербург';
    
    displayResults(`<h4>Импорт тестовых данных для ${cityName}...</h4><p>Создаем тестовые события...<br>Пожалуйста, подождите...</p>`);
    
    try {
        let result;
        if (city === 'moscow') {
            result = await api.importTestMoscowEvents();
        } else if (city === 'spb') {
            result = await api.importTestSpbEvents();
        } else {
            // Для других городов используем СПб по умолчанию
            result = await api.importTestSpbEvents();
        }
        
        displayImportResult(result, `Тестовые данные (${cityName})`);
        await loadEvents();
    } catch (error) {
        console.error('Ошибка импорта тестовых данных:', error);
        showError(`Ошибка при импорте тестовых данных для ${cityName}`);
    }
}

function displayImportResult(result, sourceName) {
    const stats = result.statistics;
    const sourceClass = result.source === 'manual' ? 'manual' : result.source === 'yandex_afisha' ? 'yandex' : 'kudago';
    
    let resultsHtml = `
        <div class="import-result">
            <h4><i class="fas fa-check-circle"></i> Импорт завершен</h4>
            <span class="source-badge ${sourceClass}">${sourceName}</span>
            
            <div class="import-stats">
                <div class="stat-item success">
                    <div class="stat-label">Импортировано</div>
                    <div class="stat-value">${stats.imported}</div>
                </div>
                <div class="stat-item warning">
                    <div class="stat-label">Дубликатов</div>
                    <div class="stat-value">${stats.duplicates}</div>
                </div>
    `;
    
    if (stats.errors > 0) {
        resultsHtml += `
                <div class="stat-item error">
                    <div class="stat-label">Ошибок</div>
                    <div class="stat-value">${stats.errors}</div>
                </div>
        `;
    }
    
    if (stats.skipped_no_coords) {
        resultsHtml += `
                <div class="stat-item warning">
                    <div class="stat-label">Без координат</div>
                    <div class="stat-value">${stats.skipped_no_coords}</div>
                </div>
        `;
    }
    
    resultsHtml += `
            </div>
            <p style="margin-top: 15px; color: var(--text-secondary); font-size: 13px;">
                ${result.message}
            </p>
        </div>
    `;
    
    displayResults(resultsHtml);
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
        kudago: 'KudaGo',
        manual: 'Ручной ввод',
        telegram: 'Telegram'
    };
    return sources[source] || source;
}

// Форматирование даты события с проверкой корректности
function formatEventDate(date) {
    // Проверяем, что дата валидна
    if (!date || isNaN(date.getTime())) {
        return 'Дата не указана';
    }
    
    // Проверяем год - если слишком старый или слишком новый, это ошибка данных
    const year = date.getFullYear();
    if (year < 1900 || year > 2100) {
        return 'Дата уточняется';
    }
    
    // Форматируем нормальную дату
    return date.toLocaleString('ru-RU', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        timeZone: 'Europe/Moscow'
    });
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
            
            if (city.slug === 'spb') {
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
    
    console.log(`Выбран город: ${cityName}`);
}

document.addEventListener('DOMContentLoaded', initMap);