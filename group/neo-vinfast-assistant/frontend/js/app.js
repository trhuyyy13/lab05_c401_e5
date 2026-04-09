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

// ═══════════════════════════════════════════════════════════════════
// DOM Elements
// ═══════════════════════════════════════════════════════════════════
const chatMessages   = document.getElementById('chatMessages');
const chatInput      = document.getElementById('chatInput');
const chatSendBtn    = document.getElementById('chatSendBtn');
const typingIndicator = document.getElementById('typingIndicator');
const bottomNav      = document.getElementById('bottomNav');

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
    
    currentTab = tabName;
    
    // Auto-focus chat input when switching to support
    if (tabName === 'support') {
        setTimeout(() => chatInput?.focus(), 400);
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
