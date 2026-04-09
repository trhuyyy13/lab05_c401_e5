/**
 * NEO — VinFast AI Assistant
 * Frontend JavaScript — SPA Navigation + Chat Logic
 */

// ═══════════════════════════════════════════════════════════════════
// Configuration
// ═══════════════════════════════════════════════════════════════════
const API_BASE = (() => {
    const origin = window.location.origin;
    const isLocalhost = origin.includes('localhost') || origin.includes('127.0.0.1');
    if (window.location.protocol === 'file:' && isLocalhost) {
        return 'http://localhost:8000';
    }
    if (isLocalhost && window.location.port && window.location.port !== '8000') {
        return `${window.location.protocol}//${window.location.hostname}:8000`;
    }
    return origin;
})();
const TYPING_DELAY = 1200; // ms simulate typing

// ═══════════════════════════════════════════════════════════════════
// State
// ═══════════════════════════════════════════════════════════════════
let currentTab = 'home';
let isProcessing = false;
let flowStack = [];
let stationSearchState = {
    location: 'VinUni',
    resolvedLocation: 'VinUniversity, Vinhomes Ocean Park, Gia Lam, Ha Noi',
    stations: [],
};
let vehicleStatusState = {
    batteryPercent: 15,
    rangeKm: 42,
};

const flowTitles = {
    'error-e15': 'Cảnh báo E15',
    'error-e07': 'Cảnh báo E07',
    'error-w11': 'Cảnh báo W11',
    'error-w21': 'Cảnh báo W21',
    'explain': 'Giải thích',
    'actions': 'Gợi ý hành động',
    'repair-guide': 'Hướng dẫn tự sửa',
    'repair-docs': 'Tài liệu hướng dẫn',
    'garage': 'Tìm gara',
    'garage-detail': 'Chi tiết gara',
    'booking': 'Đặt lịch',
    'booking-success': 'Đặt lịch',
    'booking-detail': 'Chi tiết lịch hẹn',
    'feedback': 'Phản hồi',
};

const bookingState = {
    active: false,
    garage: 'VinFast Service — Times City',
    estimate: '2-3 giờ',
    destination: 'VinFast Service Times City',
    date: '',
    time: '',
    selectedErrors: ['e15'], // Track which errors are being fixed in this booking
};

const feedbackState = {
    source: 'self',
    stationId: null,
    useful: 'useful',
    resolved: 'yes',
    rating: 5,
};

// ═══════════════════════════════════════════════════════════════════
// Error Management State
// ═══════════════════════════════════════════════════════════════════
let currentErrorId = null; // Track which error is currently being processed

const errorsState = {
    e15: { id: 'e15', title: 'Lỗi E15 — Làm mát pin', status: 'active', scheduledAt: null },
    w11: { id: 'w11', title: 'Lỗi W11 — Áp suất lốp thấp', status: 'active', scheduledAt: null },
    e07: { id: 'e07', title: 'Lỗi E07 — Hiệu suất sạc giảm', status: 'active', scheduledAt: null },
    w21: { id: 'w21', title: 'Lỗi W21 — Cảm biến định vị', status: 'active', scheduledAt: null },
};

// ═══════════════════════════════════════════════════════════════════
// DOM Elements
// ═══════════════════════════════════════════════════════════════════
const chatMessages   = document.getElementById('chatMessages');
const chatInput      = document.getElementById('chatInput');
const chatSendBtn    = document.getElementById('chatSendBtn');
const typingIndicator = document.getElementById('typingIndicator');
const bottomNav      = document.getElementById('bottomNav');
const headerTitle    = document.querySelector('.header-title');
const headerBack     = document.getElementById('headerBack');
const chargeLocationInput = document.getElementById('chargeLocationInput');
const chargeSearchBtn = document.getElementById('chargeSearchBtn');
const stationResults = document.getElementById('stationResults');
const stationListSummary = document.getElementById('stationListSummary');
const chargeResolvedLocation = document.getElementById('chargeResolvedLocation');

// ═══════════════════════════════════════════════════════════════════
// Tab Navigation (SPA)
// ═══════════════════════════════════════════════════════════════════
function switchTab(tabName) {
    const activeTabPage = document.getElementById(`page-${tabName}`);
    const isAlreadyActive = currentTab === tabName && activeTabPage?.classList.contains('active');
    if (isAlreadyActive) return;

    flowStack = [];
    bottomNav?.classList.remove('hidden');
    
    // Remove active from all pages
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    
    // Activate new page + nav
    const page = document.getElementById(`page-${tabName}`);
    const nav  = document.querySelector(`.nav-item[data-tab="${tabName}"]`) ||
        (tabName === 'charge-map' ? document.querySelector('.nav-item[data-tab="charge"]') : null);
    
    if (page) page.classList.add('active');
    if (nav)  nav.classList.add('active');
    
    currentTab = tabName;
    updateHeaderForTab(tabName);
    
    // Auto-focus chat input when switching to support
    if (tabName === 'support') {
        setTimeout(() => chatInput?.focus(), 400);
    }
    if (tabName === 'charge') {
        setTimeout(() => chargeLocationInput?.focus(), 250);
    }
}

function updateHeaderForTab(tabName) {
    const titleMap = {
        home: 'VinFast',
        support: 'Hỗ trợ',
        charge: 'Trạm sạc',
        'charge-map': 'Trạm sạc',
        profile: 'Cá nhân',
    };

    if (headerTitle) headerTitle.textContent = titleMap[tabName] || 'VinFast';
    if (headerBack) headerBack.style.visibility = tabName === 'home' ? 'hidden' : 'visible';
}

// Nav click handlers
bottomNav?.addEventListener('click', (e) => {
    const navItem = e.target.closest('.nav-item');
    if (navItem) {
        const tab = navItem.dataset.tab;
        switchTab(tab);
    }
});

// ═══════════════════════════════════════════════════════════════════
// Navigate to Support with a pre-filled message
// ═══════════════════════════════════════════════════════════════════
function navigateToSupport(message) {
    switchTab('support');
    if (message) {
        setTimeout(() => sendMessage(message), 500);
    }
}

function calculateBatteryTrip(station) {
    const batteryPercent = vehicleStatusState.batteryPercent || 0;
    const rangeKm = vehicleStatusState.rangeKm || 0;
    const kmPerPercent = batteryPercent > 0 ? rangeKm / batteryPercent : 0;
    const requiredPercent = kmPerPercent > 0
        ? Math.max(1, Math.ceil(station.distance_km / kmPerPercent))
        : 100;
    const remainingPercent = Math.max(0, Math.round((batteryPercent - requiredPercent) * 10) / 10);

    let status = 'feasible';
    let label = 'Kha thi';
    let title = 'Du pin de den tram';
    let note = 'Ban co the toi tram va van con muc pin an toan.';

    if (requiredPercent > batteryPercent) {
        status = 'unreachable';
        label = 'Khong du pin';
        title = 'Khong du pin de toi tram';
        note = 'Quang duong uoc tinh vuot qua muc pin hien tai. Ban nen chon tram gan hon hoac goi ho tro.';
    } else if (remainingPercent <= 5) {
        status = 'risky';
        label = 'Can trong';
        title = 'Co the toi nhung pin du phong thap';
        note = 'Xe co the toi tram nhung muc pin du phong thap. Nen bat che do tiet kiem nang luong.';
    }

    return { requiredPercent, remainingPercent, status, label, title, note };
}

function renderStationResults(stations) {
    if (!stationResults) return;

    if (!stations || stations.length === 0) {
        stationResults.innerHTML = '<div class="station-empty">Khong tim thay tram sac phu hop cho khu vuc nay.</div>';
        return;
    }

    stationResults.innerHTML = stations.map((station) => {
        const iconClass = station.available > 0 ? 'station-icon' : 'station-icon full';
        const availabilityClass = station.available > 0 ? 'tag-available' : 'tag-full';
        const availabilityText = station.available > 0
            ? `${station.available}/${station.total} trong`
            : 'Day';

        return `
            <div class="station-card" onclick="openStationMap('${station.id}')">
                <div class="${iconClass}">⚡</div>
                <div class="station-info">
                    <p class="station-name">${station.name}</p>
                    <p class="station-address">${station.address}</p>
                    <div class="station-meta">
                        <span class="station-tag ${availabilityClass}">${station.available > 0 ? '🟢' : '🔴'} ${availabilityText}</span>
                        <span class="station-tag tag-distance">📍 ${station.distance_km} km</span>
                    </div>
                    <div class="station-meta" style="margin-top: 8px;">
                        <span class="station-tag tag-distance">${station.type}</span>
                        <span class="station-tag tag-distance">~${station.charge_time_min} phut</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

async function loadChargingStations(location = 'VinUni') {
    const query = location?.trim() || 'VinUni';

    if (stationListSummary) {
        stationListSummary.textContent = 'Dang tim tram sac gan ban...';
    }

    try {
        const response = await fetch(`${API_BASE}/api/charging-stations`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ location: query }),
        });

        if (!response.ok) throw new Error('Charging station API error');

        const data = await response.json();
        stationSearchState = {
            location: query,
            resolvedLocation: data.resolved_location,
            stations: data.stations || [],
        };

        if (chargeResolvedLocation) {
            chargeResolvedLocation.textContent = data.resolved_location;
        }
        if (chargeLocationInput) {
            chargeLocationInput.value = query;
        }
        if (stationListSummary) {
            stationListSummary.textContent = `${data.stations.length} tram sac gan nhat`;
        }

        renderStationResults(data.stations);
    } catch (error) {
        console.error('Charging station error:', error);
        if (stationListSummary) {
            stationListSummary.textContent = 'Khong the tai tram sac';
        }
        if (stationResults) {
            stationResults.innerHTML = '<div class="station-empty">Khong the tai du lieu tram sac. Vui long kiem tra backend.</div>';
        }
    }
}

function openChargingStations(location = 'VinUni') {
    switchTab('charge');
    fetch(`${API_BASE}/api/health`).catch(() => {});
    loadChargingStations(location);
}

function openStationMap(stationId) {
    const station = stationSearchState.stations.find((item) => item.id === stationId);
    if (!station) return;
    const batteryTrip = calculateBatteryTrip(station);
    const etaMinutes = Math.max(6, Math.round(station.distance_km * 2.8));

    const setText = (id, value) => {
        const el = document.getElementById(id);
        if (el) el.textContent = value;
    };

    stationSearchState.activeStationId = station.id;
    feedbackState.stationId = station.id;
    setText('routeOrigin', stationSearchState.resolvedLocation);
    setText('routeDestination', station.name);
    setText('routeEta', `${etaMinutes} phut`);
    setText('directionStationName', station.name);
    setText('directionStationAddress', station.address);
    setText('directionDistance', `${station.distance_km} km`);
    setText('directionType', station.type);
    setText('directionTime', `~${etaMinutes} phut`);
    setText('batteryCurrent', `${vehicleStatusState.batteryPercent}%`);
    setText('batteryNeeded', `${batteryTrip.requiredPercent}%`);
    setText('batteryRemaining', `${batteryTrip.remainingPercent}%`);
    setText('batteryCheckTitle', batteryTrip.title);
    setText('batteryCheckNote', batteryTrip.note);

    const batteryBadge = document.getElementById('batteryCheckBadge');
    if (batteryBadge) {
        batteryBadge.textContent = batteryTrip.label;
        batteryBadge.className = `battery-check-badge ${batteryTrip.status}`;
    }

    const stationMapLink = document.getElementById('stationMapLink');
    if (stationMapLink) {
        const origin = encodeURIComponent(stationSearchState.resolvedLocation || 'VinUni');
        const destination = encodeURIComponent(station.address || station.name);
        stationMapLink.href = `https://www.google.com/maps/dir/?api=1&origin=${origin}&destination=${destination}`;
    }

    switchTab('charge-map');
}

// ═══════════════════════════════════════════════════════════════════
// Error Flow Navigation
// ═══════════════════════════════════════════════════════════════════

function openErrorFlow(errorId) {
    currentErrorId = errorId;
    const flowPageId = `error-${errorId}`;
    
    // Set the default selected error in booking form
    bookingState.selectedErrors = [errorId];
    
    // Update warning cards to show checkbox for current selection
    updateWarningCardStatus();
    updateErrorCheckboxes();
    
    openFlowPage(flowPageId);
}

function updateWarningCardStatus() {
    document.querySelectorAll('.warning-card').forEach(card => {
        const errorId = card.getAttribute('data-error-id');
        const error = errorsState[errorId];
        if (error) {
            const statusElement = card.querySelector('.status-badge');
            if (statusElement) {
                statusElement.setAttribute('data-status', error.status);
                const statusTexts = {
                    'active': '⭐ Chưa xử lý',
                    'scheduled': '✅ Đã lên lịch',
                    'resolved': '✓ Đã xử lý'
                };
                statusElement.textContent = statusTexts[error.status];
            }
            card.setAttribute('data-status', error.status);
        }
    });
}

function updateErrorCheckboxes() {
    document.querySelectorAll('input[name="error-selection"]').forEach(checkbox => {
        checkbox.checked = bookingState.selectedErrors.includes(checkbox.value);
    });
}

// ═══════════════════════════════════════════════════════════════════
// Flow Navigation (non-chat diagnostic screens)
// ═══════════════════════════════════════════════════════════════════

function openFlowPage(flowId) {
    const targetId = `page-${flowId}`;
    const target = document.getElementById(targetId);
    if (!target) return;

    const current = document.querySelector('.page.active');
    if (current && current.id !== targetId) {
        flowStack.push(current.id);
    }

    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    target.classList.add('active');
    bottomNav?.classList.add('hidden');

    if (headerTitle) headerTitle.textContent = flowTitles[flowId] || 'VinFast';
    if (headerBack) headerBack.style.visibility = 'visible';
}

function closeFlowToTab(tabName) {
    flowStack = [];
    bottomNav?.classList.remove('hidden');
    switchTab(tabName);
}

function goBack() {
    if (currentTab === 'charge-map') {
        switchTab('charge');
        return;
    }
    if (flowStack.length > 0) {
        const prevId = flowStack.pop();
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
        const prev = document.getElementById(prevId);
        if (prev) prev.classList.add('active');

        const flowId = prevId.replace('page-', '');
        if (flowTitles[flowId]) {
            if (headerTitle) headerTitle.textContent = flowTitles[flowId];
            if (headerBack) headerBack.style.visibility = 'visible';
            bottomNav?.classList.add('hidden');
        } else {
            bottomNav?.classList.remove('hidden');
            updateHeaderForTab(currentTab);
        }
        return;
    }

    if (currentTab !== 'home') {
        switchTab('home');
    }
}

function formatBookingDate(dateValue) {
    if (!dateValue) return 'Hôm nay';
    const date = new Date(dateValue + 'T00:00:00');
    if (Number.isNaN(date.getTime())) return dateValue;
    return date.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' });
}

function updateBookingUI() {
    const bookingGarageName = document.getElementById('bookingGarageName');
    const bookingEstimate = document.getElementById('bookingEstimate');
    const bookingDetailGarage = document.getElementById('bookingDetailGarage');
    const bookingDetailEstimate = document.getElementById('bookingDetailEstimate');
    const bookingTitle = document.getElementById('bookingTitle');
    const bookingMapLink = document.getElementById('bookingSuccessMapLink');
    const bookingDetailMapLink = document.getElementById('bookingDetailMapLink');

    if (bookingGarageName) bookingGarageName.textContent = bookingState.garage;
    if (bookingEstimate) bookingEstimate.textContent = bookingState.estimate;
    if (bookingDetailGarage) bookingDetailGarage.textContent = bookingState.garage;
    if (bookingDetailEstimate) bookingDetailEstimate.textContent = bookingState.estimate;
    if (bookingTitle) bookingTitle.textContent = bookingState.garage;

    const destination = encodeURIComponent(bookingState.destination || bookingState.garage);
    const mapUrl = `https://www.google.com/maps/dir/?api=1&origin=VinUniversity&destination=${destination}`;
    if (bookingMapLink) bookingMapLink.href = mapUrl;
    if (bookingDetailMapLink) bookingDetailMapLink.href = mapUrl;
}

function setBookingGarage(garageName, estimate, destination, openBooking = false) {
    if (garageName) bookingState.garage = garageName;
    if (estimate) bookingState.estimate = estimate;
    if (destination) bookingState.destination = destination;

    const bookingGarageSelect = document.getElementById('bookingGarage');
    if (bookingGarageSelect) {
        const option = Array.from(bookingGarageSelect.options).find(o => o.value === bookingState.garage);
        if (option) bookingGarageSelect.value = option.value;
    }

    updateBookingUI();
    if (openBooking) openFlowPage('booking');
}

function openFeedback(source) {
    feedbackState.source = source || 'self';
    const sourceText = document.getElementById('feedbackSourceText');
    const garageSection = document.getElementById('garageFeedbackSection');
    const chargeSection = document.getElementById('chargeFeedbackSection');
    const resolvedSection = document.getElementById('resolvedSection');
    const feedbackDetail = document.getElementById('feedbackDetail');

    if (sourceText) {
        if (feedbackState.source === 'garage') {
            sourceText.textContent = 'Trải nghiệm tại gara';
        } else if (feedbackState.source === 'charge') {
            sourceText.textContent = 'Trạm sạc và bản đồ chỉ đường';
        } else {
            sourceText.textContent = 'Tự sửa tại chỗ';
        }
    }

    if (garageSection) {
        garageSection.hidden = feedbackState.source !== 'garage';
    }

    if (chargeSection) {
        chargeSection.hidden = feedbackState.source !== 'charge';
    }

    if (resolvedSection) {
        resolvedSection.hidden = feedbackState.source === 'charge';
    }

    if (feedbackDetail) {
        feedbackDetail.hidden = feedbackState.source === 'charge' || feedbackState.source === 'garage';
    }

    openFlowPage('feedback');
}

// ═══════════════════════════════════════════════════════════════════
// Chat Functions
// ═══════════════════════════════════════════════════════════════════

function getCurrentTime() {
    return new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
}

/** Add a message bubble to the chat */
function addMessage(content, isUser = false, reasoningSteps = null) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${isUser ? 'user' : 'bot'}`;
    
    const avatar = isUser ? '👤' : '🤖';
    
    // Parse markdown-lite (bold, line breaks)
    let htmlContent = content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');
    
    let reasoningHTML = '';
    if (reasoningSteps && reasoningSteps.length > 0) {
        const stepsHTML = reasoningSteps.map(s => 
            `<div class="reasoning-step">
                <span class="reasoning-step-label">${s.step}:</span>
                <span>${s.content}</span>
            </div>`
        ).join('');
        
        const uniqueId = 'reasoning-' + Date.now();
        reasoningHTML = `
            <button class="reasoning-toggle" onclick="toggleReasoning('${uniqueId}')">
                🧠 Xem suy luận ReAct ▾
            </button>
            <div class="reasoning-steps" id="${uniqueId}">
                ${stepsHTML}
            </div>
        `;
    }
    
    msgDiv.innerHTML = `
        <div class="msg-avatar">${avatar}</div>
        <div>
            <div class="msg-bubble">
                <div class="markdown-content">${htmlContent}</div>
                ${reasoningHTML}
            </div>
            <p class="msg-time">${getCurrentTime()}</p>
        </div>
    `;
    
    chatMessages.appendChild(msgDiv);
    scrollToBottom();
}

/** Toggle reasoning steps visibility */
function toggleReasoning(id) {
    const el = document.getElementById(id);
    if (el) {
        el.classList.toggle('show');
        const btn = el.previousElementSibling;
        if (btn) {
            btn.textContent = el.classList.contains('show') 
                ? '🧠 Ẩn suy luận ReAct ▴' 
                : '🧠 Xem suy luận ReAct ▾';
        }
    }
}

/** Show/hide typing indicator */
function showTyping(show) {
    typingIndicator.classList.toggle('active', show);
    if (show) scrollToBottom();
}

/** Scroll chat to bottom */
function scrollToBottom() {
    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 50);
}

/** Send a message to the backend */
async function sendMessage(text) {
    if (!text?.trim() || isProcessing) return;
    
    const message = text.trim();
    isProcessing = true;
    
    // Clear input
    chatInput.value = '';
    
    // Add user message
    addMessage(message, true);
    
    // Show typing
    showTyping(true);
    
    try {
        const response = await fetch(`${API_BASE}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, session_id: 'default' }),
        });
        
        if (!response.ok) throw new Error('API error');
        
        const data = await response.json();
        
        // Simulate typing delay for more natural feel
        await new Promise(r => setTimeout(r, TYPING_DELAY));
        
        // Hide typing, show response
        showTyping(false);
        addMessage(data.answer, false, data.reasoning_steps);
        
    } catch (error) {
        console.error('Chat error:', error);
        showTyping(false);
        addMessage(
            '⚠️ Không thể kết nối đến server.\nVui lòng kiểm tra backend đang chạy tại http://localhost:8000',
            false
        );
    }
    
    isProcessing = false;
}

/** Send from suggestion chip */
function sendSuggestion(text) {
    sendMessage(text);
}

// ═══════════════════════════════════════════════════════════════════
// Event Listeners
// ═══════════════════════════════════════════════════════════════════

// Send button
chatSendBtn?.addEventListener('click', () => {
    sendMessage(chatInput.value);
});

// Enter key
chatInput?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage(chatInput.value);
    }
});

chargeSearchBtn?.addEventListener('click', () => {
    loadChargingStations(chargeLocationInput?.value || 'VinUni');
});

chargeLocationInput?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        e.preventDefault();
        loadChargingStations(chargeLocationInput.value);
    }
});

// ═══════════════════════════════════════════════════════════════════
// Load Vehicle Data from API
// ═══════════════════════════════════════════════════════════════════
async function loadVehicleStatus() {
    try {
        const res = await fetch(`${API_BASE}/api/vehicle/status`);
        if (!res.ok) return;
        
        const data = await res.json();
        
        // Update UI
        document.getElementById('vehicleName').textContent = data.model;
        document.getElementById('vehiclePlate').textContent = data.plate;
        document.getElementById('batteryNum').textContent = data.battery_percent;
        document.getElementById('batteryRange').textContent = data.range_km;
        vehicleStatusState = {
            batteryPercent: data.battery_percent,
            rangeKm: data.range_km,
        };
        document.getElementById('odometer').textContent = data.odometer_km.toLocaleString() + ' km';
        document.getElementById('nextService').textContent = data.next_service_km.toLocaleString() + ' km';
        
        // Update battery ring
        const circumference = 2 * Math.PI * 30; // r=30
        const offset = circumference * (1 - data.battery_percent / 100);
        document.getElementById('batteryRing').style.strokeDashoffset = offset;
        
        // Update battery color based on level
        const ring = document.getElementById('batteryRing');
        if (data.battery_percent <= 20) {
            ring.style.stroke = 'var(--danger)';
        } else if (data.battery_percent <= 40) {
            ring.style.stroke = 'var(--warning)';
        } else {
            ring.style.stroke = 'var(--success)';
        }
        
        // Update badge
        const badge = document.getElementById('vehicleBadge');
        if (data.warnings.length > 0) {
            badge.className = 'vehicle-status-badge badge-warn';
            badge.textContent = `⚠ ${data.warnings.length} cảnh báo`;
        }
        
    } catch (e) {
        console.log('Vehicle API not available, using defaults');
    }
}

// ═══════════════════════════════════════════════════════════════════
// Initialize
// ═══════════════════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
    window.openChargingStations = openChargingStations;
    window.openStationMap = openStationMap;
    window.switchTab = switchTab;
    window.navigateToSupport = navigateToSupport;
    window.openErrorFlow = openErrorFlow;

    // Initialize warning card status display
    updateWarningCardStatus();
    updateErrorCheckboxes();
    
    loadVehicleStatus();
    loadChargingStations('VinUni');
    updateHeaderForTab(currentTab);

    headerBack?.addEventListener('click', goBack);

    const bookingForm = document.getElementById('bookingForm');
    const bookingGarageSelect = document.getElementById('bookingGarage');
    const bookingDate = document.getElementById('bookingDate');
    const bookingTime = document.getElementById('bookingTime');
    const bookingSuccessText = document.getElementById('bookingSuccessText');
    const bookingReminder = document.getElementById('bookingReminder');
    const bookingMeta = document.getElementById('bookingMeta');
    const bookingDetailTime = document.getElementById('bookingDetailTime');
    const feedbackSubmit = document.getElementById('feedbackSubmit');

    bookingForm?.addEventListener('submit', (e) => {
        e.preventDefault();
        
        // Collect selected errors from checkboxes
        const selectedCheckboxes = document.querySelectorAll('input[name="error-selection"]:checked');
        bookingState.selectedErrors = Array.from(selectedCheckboxes).map(cb => cb.value);
        
        // If no errors selected, use current error
        if (bookingState.selectedErrors.length === 0 && currentErrorId) {
            bookingState.selectedErrors = [currentErrorId];
        }
        
        // Mark selected errors as scheduled
        bookingState.selectedErrors.forEach(errorId => {
            if (errorsState[errorId]) {
                errorsState[errorId].status = 'scheduled';
                errorsState[errorId].scheduledAt = new Date().toISOString();
            }
        });
        
        bookingState.date = bookingDate?.value || '';
        bookingState.time = bookingTime?.value || '16:30';
        bookingState.active = true;

        const dateLabel = formatBookingDate(bookingState.date);
        const timeLabel = bookingState.time || '16:30';
        const summary = `${timeLabel} • ${dateLabel} • Ước tính ${bookingState.estimate}`;
        
        // Format list of errors for display
        const errorLabels = bookingState.selectedErrors.map(id => id.toUpperCase()).join(', ');

        if (bookingSuccessText) {
            bookingSuccessText.textContent = `Bạn đã đặt lịch tại ${bookingState.garage} lúc ${timeLabel} ngày ${dateLabel} để sửa ${errorLabels}.`;
        }
        if (bookingMeta) bookingMeta.textContent = summary;
        if (bookingDetailTime) bookingDetailTime.textContent = `${timeLabel} • ${dateLabel}`;
        
        const bookingIssues = document.getElementById('bookingIssues');
        if (bookingIssues) bookingIssues.textContent = `Sửa: ${errorLabels}`;
        
        const bookingDetailIssues = document.getElementById('bookingDetailIssues');
        if (bookingDetailIssues) bookingDetailIssues.textContent = errorLabels;
        
        bookingReminder?.classList.remove('hidden');
        updateBookingUI();
        updateWarningCardStatus();

        openFlowPage('booking-success');
    });

    bookingGarageSelect?.addEventListener('change', () => {
        const selected = bookingGarageSelect.options[bookingGarageSelect.selectedIndex];
        bookingState.garage = selected?.value || bookingState.garage;
        bookingState.estimate = selected?.dataset?.estimate || bookingState.estimate;
        bookingState.destination = selected?.dataset?.destination || bookingState.destination;
        updateBookingUI();
    });

    setBookingGarage(bookingState.garage, bookingState.estimate, bookingState.destination, false);

    const feedbackDetail = document.getElementById('feedbackDetail');
    document.querySelectorAll('input[name="resolved"]').forEach((input) => {
        input.addEventListener('change', () => {
            if (!feedbackDetail || feedbackState.source === 'charge') return;
            feedbackDetail.hidden = input.value !== 'no';
        });
    });

    document.querySelectorAll('input[name="station-resolved"]').forEach((input) => {
        input.addEventListener('change', () => {
            feedbackState.resolved = input.value;
        });
    });

    document.querySelectorAll('input[name="useful"]').forEach((input) => {
        input.addEventListener('change', () => {
            feedbackState.useful = input.value;
        });
    });


    document.querySelectorAll('.rating').forEach((ratingBlock) => {
        ratingBlock.addEventListener('click', (e) => {
            const star = e.target.closest('.star');
            if (!star) return;
            const rating = Number(star.dataset.star || 0);
            if (ratingBlock.id === 'stationFeedbackStars') {
                feedbackState.rating = rating;
            }
            ratingBlock.querySelectorAll('.star').forEach((btn) => {
                const value = Number(btn.dataset.star || 0);
                btn.classList.toggle('active', value <= rating);
            });
        });
    });

    feedbackSubmit?.addEventListener('click', () => {
        // Mark selected/scheduled errors as resolved
        if (feedbackState.source === 'garage') {
            // For garage feedback, mark the booked errors as resolved
            bookingState.selectedErrors.forEach(errorId => {
                if (errorsState[errorId]) {
                    errorsState[errorId].status = 'resolved';
                }
            });
            
            // Remove resolved error cards from warning section
            bookingState.selectedErrors.forEach(errorId => {
                const warningCard = document.querySelector(`.warning-card[data-error-id="${errorId}"]`);
                if (warningCard) {
                    warningCard.style.animation = 'fadeOut 0.3s ease-out forwards';
                    setTimeout(() => warningCard.remove(), 300);
                }
            });
            
            // Hide booking reminder
            const bookingReminder = document.getElementById('bookingReminder');
            if (bookingReminder) {
                bookingReminder.classList.add('hidden');
            }
            
            // Reset booking state
            bookingState.active = false;
            bookingState.selectedErrors = [];
        } else if (feedbackState.source === 'charge') {
            console.log('Charge feedback:', {
                stationId: feedbackState.stationId,
                useful: feedbackState.useful,
                resolved: feedbackState.resolved,
                rating: feedbackState.rating,
            });
        } else {
            // For self-repair feedback, mark current error as resolved
            if (currentErrorId && errorsState[currentErrorId]) {
                errorsState[currentErrorId].status = 'resolved';
                
                // Remove resolved warning card
                const warningCard = document.querySelector(`.warning-card[data-error-id="${currentErrorId}"]`);
                if (warningCard) {
                    warningCard.style.animation = 'fadeOut 0.3s ease-out forwards';
                    setTimeout(() => warningCard.remove(), 300);
                }
            }
        }
        
        currentErrorId = null;
        closeFlowToTab('home');
    });
    
    // Animate battery ring on load
    const ring = document.getElementById('batteryRing');
    if (ring) {
        const finalOffset = ring.style.strokeDashoffset || '52.8';
        ring.style.strokeDashoffset = '188.5'; // Start from 0%
        setTimeout(() => {
            ring.style.strokeDashoffset = finalOffset;
        }, 300);
    }
});
