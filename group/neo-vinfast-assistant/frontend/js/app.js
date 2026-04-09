/**
 * NEO — VinFast AI Assistant
 * Frontend JavaScript — SPA Navigation + Chat Logic
 */

// ═══════════════════════════════════════════════════════════════════
// Configuration
// ═══════════════════════════════════════════════════════════════════
const API_BASE = window.location.origin;
const TYPING_DELAY = 1200; // ms simulate typing

// ═══════════════════════════════════════════════════════════════════
// State
// ═══════════════════════════════════════════════════════════════════
let currentTab = 'home';
let isProcessing = false;
let stationSearchState = {
    location: 'VinUni',
    resolvedLocation: 'VinUniversity, Vinhomes Ocean Park, Gia Lâm, Hà Nội',
    stations: [],
};
let vehicleStatusState = {
    batteryPercent: 15,
    rangeKm: 42,
};

// ═══════════════════════════════════════════════════════════════════
// DOM Elements
// ═══════════════════════════════════════════════════════════════════
const chatMessages   = document.getElementById('chatMessages');
const chatInput      = document.getElementById('chatInput');
const chatSendBtn    = document.getElementById('chatSendBtn');
const typingIndicator = document.getElementById('typingIndicator');
const bottomNav      = document.getElementById('bottomNav');
const headerBack     = document.getElementById('headerBack');
const chargeLocationInput = document.getElementById('chargeLocationInput');
const chargeSearchBtn = document.getElementById('chargeSearchBtn');
const stationResults = document.getElementById('stationResults');
const stationListSummary = document.getElementById('stationListSummary');
const chargeResolvedLocation = document.getElementById('chargeResolvedLocation');

function calculateBatteryTrip(station) {
    const batteryPercent = vehicleStatusState.batteryPercent || 0;
    const rangeKm = vehicleStatusState.rangeKm || 0;
    const kmPerPercent = batteryPercent > 0 ? rangeKm / batteryPercent : 0;
    const requiredPercent = kmPerPercent > 0 ? Math.max(1, Math.ceil(station.distance_km / kmPerPercent)) : 100;
    const remainingPercent = Math.max(0, Math.round((batteryPercent - requiredPercent) * 10) / 10);

    let status = 'feasible';
    let label = 'Khả thi';
    let title = 'Đủ pin để đến trạm';
    let note = 'Bạn có thể tới trạm và vẫn còn mức pin an toàn.';

    if (requiredPercent > batteryPercent) {
        status = 'unreachable';
        label = 'Không đủ pin';
        title = 'Không đủ pin để tới trạm';
        note = 'Quãng đường ước tính vượt quá mức pin hiện tại. Bạn nên chọn trạm gần hơn hoặc gọi hỗ trợ.';
    } else if (remainingPercent <= 5) {
        status = 'risky';
        label = 'Cẩn trọng';
        title = 'Có thể tới nhưng pin dự phòng thấp';
        note = 'Xe có thể tới trạm nhưng mức pin dự phòng thấp. Nên bật chế độ tiết kiệm năng lượng.';
    }

    return { requiredPercent, remainingPercent, status, label, title, note };
}

// ═══════════════════════════════════════════════════════════════════
// Tab Navigation (SPA)
// ═══════════════════════════════════════════════════════════════════
function switchTab(tabName) {
    if (currentTab === tabName) return;
    
    // Remove active from all pages
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    
    // Activate new page + nav
    const page = document.getElementById(`page-${tabName}`);
    const nav  = document.querySelector(`.nav-item[data-tab="${tabName}"]`);
    
    if (page) page.classList.add('active');
    if (nav)  nav.classList.add('active');
    if (!nav && tabName === 'charge-map') {
        document.querySelector(`.nav-item[data-tab="charge"]`)?.classList.add('active');
    }
    
    currentTab = tabName;
    
    // Auto-focus chat input when switching to support
    if (tabName === 'support') {
        setTimeout(() => chatInput?.focus(), 400);
    }
    if (tabName === 'charge') {
        setTimeout(() => chargeLocationInput?.focus(), 250);
    }
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

function renderStationResults(stations) {
    if (!stationResults) return;

    if (!stations || stations.length === 0) {
        stationResults.innerHTML = '<div class="station-empty">Không tìm thấy trạm sạc phù hợp cho khu vực này.</div>';
        return;
    }

    stationResults.innerHTML = stations.map((station) => {
        const iconClass = station.available > 0 ? 'station-icon' : 'station-icon full';
        const availabilityClass = station.available > 0 ? 'tag-available' : 'tag-full';
        const availabilityText = station.available > 0
            ? `${station.available}/${station.total} trống`
            : 'Đầy';

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
                        <span class="station-tag tag-distance">~${station.charge_time_min} phút</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

async function loadChargingStations(location = 'VinUni') {
    const query = location?.trim() || 'VinUni';

    if (stationListSummary) {
        stationListSummary.textContent = 'Đang tìm trạm sạc gần bạn...';
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
            stationListSummary.textContent = `${data.stations.length} trạm sạc gần nhất`;
        }

        renderStationResults(data.stations);
    } catch (error) {
        console.error('Charging station error:', error);
        if (stationListSummary) {
            stationListSummary.textContent = 'Không thể tải trạm sạc';
        }
        if (stationResults) {
            stationResults.innerHTML = '<div class="station-empty">Không thể tải dữ liệu trạm sạc. Vui lòng kiểm tra backend.</div>';
        }
    }
}

function openChargingStations(location = 'VinUni') {
    switchTab('charge');
    loadChargingStations(location);
}

function openStationMap(stationId) {
    const station = stationSearchState.stations.find((item) => item.id === stationId);
    if (!station) return;
    const batteryTrip = calculateBatteryTrip(station);
    const etaMinutes = Math.max(6, Math.round(station.distance_km * 2.8));

    document.getElementById('routeOrigin').textContent = stationSearchState.resolvedLocation;
    document.getElementById('routeDestination').textContent = station.name;
    document.getElementById('routeEta').textContent = `${etaMinutes} phút`;
    document.getElementById('directionStationName').textContent = station.name;
    document.getElementById('directionStationAddress').textContent = station.address;
    document.getElementById('directionDistance').textContent = `${station.distance_km} km`;
    document.getElementById('directionType').textContent = station.type;
    document.getElementById('directionTime').textContent = `~${etaMinutes} phút`;
    document.getElementById('batteryCurrent').textContent = `${vehicleStatusState.batteryPercent}%`;
    document.getElementById('batteryNeeded').textContent = `${batteryTrip.requiredPercent}%`;
    document.getElementById('batteryRemaining').textContent = `${batteryTrip.remainingPercent}%`;
    document.getElementById('batteryCheckTitle').textContent = batteryTrip.title;
    document.getElementById('batteryCheckNote').textContent = batteryTrip.note;
    const batteryBadge = document.getElementById('batteryCheckBadge');
    batteryBadge.textContent = batteryTrip.label;
    batteryBadge.className = `battery-check-badge ${batteryTrip.status}`;

    switchTab('charge-map');
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

headerBack?.addEventListener('click', () => {
    if (currentTab === 'charge-map') {
        switchTab('charge');
        return;
    }
    if (currentTab !== 'home') {
        switchTab('home');
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
    loadVehicleStatus();
    loadChargingStations('VinUni');
    
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
