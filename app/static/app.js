/**
 * SAMUDRA AI — Frontend Application
 * वेब एप्लिकेशन - यूज़र इंटरफेस
 *
 * Handles tab navigation, API communication, and data visualization
 */

// Configuration
const API_BASE = '';
const REGION_DEFAULT = {
    lat_min: 14.0,
    lat_max: 21.0,
    lng_min: 67.0,
    lng_max: 74.5
};
const REFRESH_INTERVAL_MS = 3 * 60 * 60 * 1000; // 3 hours

// State
let currentTab = 'pfz-zones';
let lastUpdate = new Date();

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeTabs();
    initializeEventListeners();
    checkSystemStatus();
    updateDateTime();
    setInterval(updateDateTime, 1000);
    initializeAutoRefresh();
    registerServiceWorker();
});

// ============================================================================
// SERVICE WORKER (PWA Support for Android)
// ============================================================================

function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('/static/service-worker.js')
                .then(reg => console.log('Service Worker registered for Android support'))
                .catch(err => console.log('Service Worker registration failed:', err));
        });
    }
}

// ============================================================================
// TAB NAVIGATION
// ============================================================================

function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabPanes = document.querySelectorAll('.tab-pane');

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });

    // Remove active from all buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    const selectedPane = document.getElementById(tabName);
    if (selectedPane) {
        selectedPane.classList.add('active');
    }

    // Mark button as active
    const selectedButton = document.querySelector(`[data-tab="${tabName}"]`);
    if (selectedButton) {
        selectedButton.classList.add('active');
    }

    currentTab = tabName;

    // Load tab-specific data
    loadTabData(tabName);
}

function loadTabData(tabName) {
    switch(tabName) {
        case 'pfz-zones':
            initPFZMap();
            break;
        case 'ghol-special':
            analyzeGholLocation();
            break;
        case 'ocean-layers':
            loadOceanData();
            break;
        case 'astronomical':
            loadLunarData();
            break;
        case 'economics':
            loadEconomicData();
            break;
        case 'safety':
            loadSafetyData();
            break;
    }
}

// ============================================================================
// EVENT LISTENERS
// ============================================================================

function initializeEventListeners() {
    // PFZ Zones — now powered by agents
    document.getElementById('run-agents-btn')?.addEventListener('click', runAgentAnalysis);
    document.getElementById('zone-filter')?.addEventListener('change', applyZoneFilterFromLastRun);

    // GHOL Analysis
    document.getElementById('ghol-analyze-btn')?.addEventListener('click', analyzeGholLocation);
    document.getElementById('generate-trip-btn')?.addEventListener('click', generateTripPlan);

    // Economics
    document.getElementById('calculate-roi-btn')?.addEventListener('click', calculateROI);

    // Set today's date in date inputs
    const todayDate = new Date().toISOString().split('T')[0];
    const dateInput = document.getElementById('ghol-date');
    if (dateInput) {
        dateInput.value = todayDate;
    }
}

// ============================================================================
// SYSTEM STATUS
// ============================================================================

async function checkSystemStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/health`);
        const data = await response.json();

        if (response.ok) {
            updateStatusIndicator('operational', '✅ System Operational');
            document.getElementById('api-status').textContent = 'Connected';
        } else {
            updateStatusIndicator('error', '❌ System Error');
            document.getElementById('api-status').textContent = 'Error';
        }
    } catch (error) {
        console.error('Status check failed:', error);
        updateStatusIndicator('error', '⚠️ Connection Failed');
        document.getElementById('api-status').textContent = 'Disconnected';
    }
}

function updateStatusIndicator(status, text) {
    const indicator = document.getElementById('system-status');
    const dot = indicator.querySelector('.status-dot');
    const statusText = document.getElementById('status-text');

    if (status === 'operational') {
        dot.style.background = '#06a77d';
    } else {
        dot.style.background = '#d63230';
    }

    statusText.textContent = text;
}

function updateDateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    const dateString = now.toLocaleDateString();
    document.getElementById('last-update').textContent = `${dateString} ${timeString}`;
}

// ============================================================================
// PFZ ZONES TAB — AI AGENT MAP
// ============================================================================

let pfzMap = null;
let pfzZoneLayer = null;
let pfzPulseLayer = null;
let agentsRunning = false;
let lastAgentFeatures = [];
let lastLunarContext = null;
let lastExecutionTime = 0;

// Agent display names & phases
const AGENT_PHASES = {
    data:     ['cmems_agent', 'nasa_agent', 'ecmwf_agent', 'gebco_agent'],
    analysis: ['ghol_agent', 'thermal_agent', 'wind_agent', 'lunar_agent', 'productivity_agent'],
    decision: ['recommendation_agent'],
};

function initPFZMap() {
    if (pfzMap) return; // Already initialised

    pfzMap = L.map('pfz-map', { zoomControl: true }).setView([17.5, 71.0], 6);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://openstreetmap.org">OpenStreetMap</a>',
        maxZoom: 14,
    }).addTo(pfzMap);

    pfzPulseLayer = L.layerGroup().addTo(pfzMap);
    pfzZoneLayer  = L.layerGroup().addTo(pfzMap);

    // Draw target region rectangle
    drawRegionBounds();
}

function drawRegionBounds() {
    if (!pfzMap) return;
    const latMin = parseFloat(document.getElementById('lat-min').value) || 14.0;
    const latMax = parseFloat(document.getElementById('lat-max').value) || 21.0;
    const lngMin = parseFloat(document.getElementById('lng-min').value) || 67.0;
    const lngMax = parseFloat(document.getElementById('lng-max').value) || 74.5;

    if (pfzMap._regionRect) pfzMap.removeLayer(pfzMap._regionRect);
    pfzMap._regionRect = L.rectangle([[latMin, lngMin], [latMax, lngMax]], {
        color: '#0066cc', weight: 1.5, fill: false, dashArray: '6 4', opacity: 0.5,
    }).addTo(pfzMap);
}

// ── Animate agent pipeline UI ────────────────────────────────────────────────

function setAgentState(agentId, state, confidence) {
    const el = document.querySelector(`.agent-item[data-agent="${agentId}"]`);
    if (!el) return;
    el.className = 'agent-item ' + state;
    const confEl = el.querySelector('.agent-conf');
    if (confEl && confidence !== undefined) {
        confEl.textContent = state === 'completed' ? `${Math.round(confidence * 100)}%` : state === 'running' ? '…' : '--';
    }
}

function resetAgentPipeline() {
    document.querySelectorAll('.agent-item').forEach(el => {
        el.className = 'agent-item';
        const conf = el.querySelector('.agent-conf');
        if (conf) conf.textContent = '--';
    });
    document.getElementById('pipeline-status').textContent = 'Running…';
    document.getElementById('pipeline-status').className = 'pipeline-status-bar running';
}

async function animatePhase(phase, delayMs, agentStatus) {
    const agents = AGENT_PHASES[phase] || [];

    // Mark all as running
    agents.forEach(id => setAgentState(id, 'running'));
    await sleep(delayMs * 0.4);

    // Mark each as completed with its real confidence
    for (const id of agents) {
        const info = agentStatus[id];
        const conf = info ? info.confidence : 0.5;
        setAgentState(id, 'completed', conf);
        await sleep(120);
    }
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

async function fetchJsonWithRetry(url, options = {}, retries = 2, baseDelayMs = 900) {
    let lastError = null;
    for (let attempt = 0; attempt <= retries; attempt++) {
        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            lastError = error;
            if (attempt < retries) {
                const delay = baseDelayMs * (attempt + 1);
                await sleep(delay);
            }
        }
    }
    throw lastError || new Error('Request failed');
}

function showRefreshToast(message, tone = 'info') {
    const toast = document.createElement('div');
    const bg = tone === 'ok' ? '#1f7a58' : (tone === 'warn' ? '#b06b2d' : '#1f3d72');
    toast.style.cssText = [
        'position:fixed',
        'right:16px',
        'bottom:16px',
        'z-index:9999',
        'padding:10px 14px',
        'border-radius:10px',
        'background:' + bg,
        'color:#fff',
        'font-size:12px',
        'font-weight:600',
        'box-shadow:0 10px 28px rgba(0,0,0,0.25)',
        'opacity:0',
        'transform:translateY(8px)',
        'transition:opacity 220ms ease, transform 220ms ease',
    ].join(';');
    toast.textContent = message;
    document.body.appendChild(toast);

    requestAnimationFrame(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateY(0)';
    });

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(8px)';
        setTimeout(() => toast.remove(), 250);
    }, 2800);
}

function initializeAutoRefresh() {
    setInterval(() => {
        refreshAllDataWithRecovery().catch(err => {
            console.error('Scheduled refresh failed:', err);
        });
    }, REFRESH_INTERVAL_MS);
}

async function refreshAllDataWithRecovery() {
    const endpoints = [
        '/api/health',
        '/api/data/sources',
        '/api/lunar/phase',
        '/api/lunar/forecast',
        '/api/lunar/spawning-windows',
        '/api/economics/market-prices',
    ];

    let failures = 0;
    for (const path of endpoints) {
        try {
            await fetchJsonWithRetry(`${API_BASE}${path}`, {}, 2, 900);
        } catch (e) {
            failures += 1;
            console.warn('Refresh retry exhausted for', path, e);
        }
    }

    // Repaint currently active views after warm-up fetches.
    try {
        await loadTabData(currentTab);
    } catch (e) {
        failures += 1;
    }

    if (failures > 0) {
        await checkSystemStatus();
        showRefreshToast(`Auto-refresh partial failure (${failures}) - retries applied`, 'warn');
    } else {
        lastUpdate = new Date();
        showRefreshToast('All data refreshed (3h cycle)', 'ok');
    }
}

function getZoneFilterMode() {
    return document.getElementById('zone-filter')?.value || 'high';
}

function getZoneFilterLabel(mode) {
    if (mode === 'adaptive') return 'Adaptive Smart';
    if (mode === 'high-medium') return 'High + Medium';
    if (mode === 'all') return 'All';
    return 'High only';
}

function filterFeaturesByConfidence(features, mode) {
    if (mode === 'adaptive') {
        const ranked = [...features].sort((a, b) => {
            const as = Number(a?.properties?.pfz_score || 0);
            const bs = Number(b?.properties?.pfz_score || 0);
            return bs - as;
        });

        const high = ranked.filter(feature => {
            const confidence = String(feature?.properties?.confidence || '').toUpperCase();
            const score = Number(feature?.properties?.pfz_score || 0);
            return confidence === 'HIGH' || score >= 0.7;
        });

        // Real-data adaptive rule: keep all HIGH, and if too sparse include top MEDIUM
        // until at least 4 zones or 35% of detected set are shown.
        const minTarget = Math.min(ranked.length, Math.max(4, Math.ceil(ranked.length * 0.35)));
        if (high.length >= minTarget) return high;

        const selectedIds = new Set(high.map(f => `${f.geometry?.coordinates?.[0]}:${f.geometry?.coordinates?.[1]}:${f.properties?.zone_id}`));
        const result = [...high];
        for (const feature of ranked) {
            const key = `${feature.geometry?.coordinates?.[0]}:${feature.geometry?.coordinates?.[1]}:${feature.properties?.zone_id}`;
            if (selectedIds.has(key)) continue;
            const confidence = String(feature?.properties?.confidence || '').toUpperCase();
            if (confidence === 'MEDIUM') {
                result.push(feature);
                selectedIds.add(key);
            }
            if (result.length >= minTarget) break;
        }

        // If still sparse (e.g. all LOW), include top LOW zones by real score.
        if (result.length < minTarget) {
            for (const feature of ranked) {
                const key = `${feature.geometry?.coordinates?.[0]}:${feature.geometry?.coordinates?.[1]}:${feature.properties?.zone_id}`;
                if (selectedIds.has(key)) continue;
                result.push(feature);
                selectedIds.add(key);
                if (result.length >= minTarget) break;
            }
        }
        return result;
    }

    if (mode === 'all') return features;

    if (mode === 'high-medium') {
        return features.filter(feature => {
            const confidence = String(feature?.properties?.confidence || '').toUpperCase();
            return confidence === 'HIGH' || confidence === 'MEDIUM';
        });
    }

    // Strict high-confidence filter backed by real consensus score.
    return features.filter(feature => {
        const confidence = String(feature?.properties?.confidence || '').toUpperCase();
        const score = Number(feature?.properties?.pfz_score || 0);
        return confidence === 'HIGH' && score >= 0.7;
    });
}

function applyZoneFilterFromLastRun() {
    if (!lastAgentFeatures.length) return;

    const mode = getZoneFilterMode();
    const filtered = filterFeaturesByConfidence(lastAgentFeatures, mode);
    const shownCount = filtered.length;
    const totalCount = lastAgentFeatures.length;

    const statusBar = document.getElementById('pipeline-status');
    statusBar.textContent = `✅ Showing ${shownCount}/${totalCount} zones (${getZoneFilterLabel(mode)}) — ${lastExecutionTime}s`;
    statusBar.className = 'pipeline-status-bar done';

    renderZonesOnMap(filtered);
    renderZoneList(filtered, lastLunarContext);

    document.getElementById('zone-count-badge').textContent = shownCount;
    const filterBadge = document.getElementById('zone-filter-badge');
    if (filterBadge) filterBadge.textContent = getZoneFilterLabel(mode);
}

// ── Main agent analysis runner ───────────────────────────────────────────────

async function runAgentAnalysis() {
    if (agentsRunning) return;
    agentsRunning = true;

    const btn = document.getElementById('run-agents-btn');
    btn.disabled = true;
    btn.innerHTML = '<span class="btn-icon spinning">⚙️</span> Agents running…';

    // Ensure map is ready
    initPFZMap();
    drawRegionBounds();

    // Clear previous zones
    pfzPulseLayer.clearLayers();
    pfzZoneLayer.clearLayers();
    document.getElementById('zone-list').innerHTML = '<p class="zone-list-empty">⏳ Agents working…</p>';
    document.getElementById('zone-count-badge').textContent = '0';

    resetAgentPipeline();

    const lat_min = parseFloat(document.getElementById('lat-min').value) || 14.0;
    const lat_max = parseFloat(document.getElementById('lat-max').value) || 21.0;
    const lng_min = parseFloat(document.getElementById('lng-min').value) || 67.0;
    const lng_max = parseFloat(document.getElementById('lng-max').value) || 74.5;

    // Mark data agents as running immediately
    AGENT_PHASES.data.forEach(id => setAgentState(id, 'running'));

    let data;
    try {
        data = await fetchJsonWithRetry(`${API_BASE}/api/pfz/agent-analysis`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lat_min, lat_max, lng_min, lng_max }),
        }, 2, 1000);
    } catch (err) {
        document.getElementById('pipeline-status').textContent = '❌ Connection failed';
        document.getElementById('pipeline-status').className = 'pipeline-status-bar error';
        document.getElementById('zone-list').innerHTML = `<p class="zone-list-empty">⚠️ API error: ${err.message}</p>`;
        btn.disabled = false;
        btn.innerHTML = '<span class="btn-icon">🤖</span> Run AI Agents';
        agentsRunning = false;
        return;
    }

    const agentStatus = data?.data?.agent_status || {};
    const geojson     = data?.data?.geojson || { features: [] };
    const execTime    = data?.data?.execution_time_seconds || 0;

    // Animate pipeline with real results
    await animatePhase('data',     600, agentStatus);
    await animatePhase('analysis', 800, agentStatus);
    await animatePhase('decision', 300, agentStatus);
    setAgentState('recommendation_agent', 'completed', 0.9);

    // Keep raw real-data output and apply selected confidence filter.
    lastAgentFeatures = Array.isArray(geojson.features) ? geojson.features : [];
    lastLunarContext = data?.data?.lunar_context || null;
    lastExecutionTime = execTime;
    const mode = getZoneFilterMode();
    const filteredFeatures = filterFeaturesByConfidence(lastAgentFeatures, mode);

    // Update status bar
    const zoneCount = filteredFeatures.length;
    const totalCount = lastAgentFeatures.length;
    const statusBar = document.getElementById('pipeline-status');
    statusBar.textContent = `✅ Showing ${zoneCount}/${totalCount} zones (${getZoneFilterLabel(mode)}) — ${execTime}s`;
    statusBar.className = 'pipeline-status-bar done';

    // Render zones on map
    renderZonesOnMap(filteredFeatures);
    renderZoneList(filteredFeatures, lastLunarContext);

    document.getElementById('zone-count-badge').textContent = zoneCount;
    const filterBadge = document.getElementById('zone-filter-badge');
    if (filterBadge) filterBadge.textContent = getZoneFilterLabel(mode);

    btn.disabled = false;
    btn.innerHTML = '<span class="btn-icon">🤖</span> Run AI Agents';
    agentsRunning = false;
}

// ── Map zone rendering ───────────────────────────────────────────────────────

const ZONE_COLORS = { HIGH: '#d63230', MEDIUM: '#d68a3d', LOW: '#0066cc' };
const ZONE_RADIUS = { HIGH: 20, MEDIUM: 14, LOW: 9 };

function renderZonesOnMap(features) {
    pfzPulseLayer.clearLayers();
    pfzZoneLayer.clearLayers();

    features.forEach(feature => {
        const [lng, lat] = feature.geometry.coordinates;
        const props = feature.properties;
        const color  = ZONE_COLORS[props.confidence] || '#888';
        const radius = ZONE_RADIUS[props.confidence]  || 10;

        // Outer pulse ring for HIGH confidence zones
        if (props.confidence === 'HIGH') {
            L.circle([lat, lng], {
                radius: radius * 2200,
                color: color, weight: 1,
                fill: true, fillColor: color, fillOpacity: 0.08,
                className: 'pfz-pulse-ring',
            }).addTo(pfzPulseLayer);
        }

        // Main marker
        const marker = L.circleMarker([lat, lng], {
            radius,
            color: '#fff', weight: 1.5,
            fillColor: color, fillOpacity: 0.85,
        });

        const agents = (props.supporting_agents || []).join(', ') || 'N/A';
        const sst    = props.sst    ? `${props.sst.toFixed(1)}°C`   : 'N/A';
        const depth  = props.depth  ? `${props.depth}m`             : 'N/A';
        const chl    = props.chlorophyll ? `${props.chlorophyll.toFixed(2)} mg/m³` : 'N/A';
        const ghol   = props.ghol_suitability ? `${Math.round(props.ghol_suitability * 100)}%` : 'N/A';

        marker.bindPopup(`
            <div class="zone-popup">
                <div class="popup-header">
                    <strong>Zone #${props.zone_id}</strong>
                    <span class="popup-badge popup-${props.confidence.toLowerCase()}">${props.confidence}</span>
                </div>
                <table class="popup-table">
                    <tr><td>PFZ Score</td><td><strong>${props.pfz_score}</strong></td></tr>
                    <tr><td>Agent Votes</td><td><strong>${props.agent_votes}</strong></td></tr>
                    <tr><td>SST</td><td>${sst}</td></tr>
                    <tr><td>Depth</td><td>${depth}</td></tr>
                    <tr><td>Chlorophyll</td><td>${chl}</td></tr>
                    <tr><td>GHOL Score</td><td>${ghol}</td></tr>
                    <tr><td colspan="2" style="font-size:0.78rem;color:#666;padding-top:4px">${agents}</td></tr>
                </table>
            </div>
        `, { maxWidth: 260 });

        marker.addTo(pfzZoneLayer);
    });

    // Fit map to zones if any exist
    if (features.length > 0) {
        const coords = features.map(f => [f.geometry.coordinates[1], f.geometry.coordinates[0]]);
        pfzMap.fitBounds(L.latLngBounds(coords).pad(0.2));
    }
}

// ── Zone list rendering ──────────────────────────────────────────────────────

function renderZoneList(features, lunarContext) {
    const listEl = document.getElementById('zone-list');

    if (features.length === 0) {
        listEl.innerHTML = '<p class="zone-list-empty">No zones detected in this region.</p>';
        return;
    }

    let html = '';

    // Lunar banner if spawning window
    if (lunarContext && lunarContext.spawning_window) {
        html += `<div class="lunar-banner">🌑 Spawning window active — ${lunarContext.phase?.replace(/_/g,' ')} (${lunarContext.illumination_percent?.toFixed(0)}% illumination)</div>`;
    }

    features.forEach(f => {
        const p = f.properties;
        const [lng, lat] = f.geometry.coordinates;
        const color = ZONE_COLORS[p.confidence] || '#888';
        html += `
            <div class="zone-list-item" onclick="flyToZone(${lat},${lng},${p.zone_id})">
                <div class="zli-header">
                    <span class="zli-id">Zone #${p.zone_id}</span>
                    <span class="zli-badge" style="background:${color}">${p.confidence}</span>
                    <span class="zli-score">${p.pfz_score}</span>
                </div>
                <div class="zli-coords">${lat.toFixed(3)}°N  ${lng.toFixed(3)}°E</div>
                <div class="zli-agents">${(p.supporting_agents || []).join(' · ') || '—'}</div>
            </div>
        `;
    });

    listEl.innerHTML = html;
}

function flyToZone(lat, lng, zoneId) {
    if (!pfzMap) return;
    pfzMap.flyTo([lat, lng], 9, { duration: 1.0 });
    // Open the popup for that marker
    pfzZoneLayer.eachLayer(layer => {
        if (layer.getLatLng && Math.abs(layer.getLatLng().lat - lat) < 0.01) {
            setTimeout(() => layer.openPopup(), 1100);
        }
    });
}

// Keep old function name alive so any other callers don't break
function analyzePFZZones() { initPFZMap(); }

// ============================================================================
// GHOL SPECIALIST TAB
// ============================================================================

async function analyzeGholLocation() {
    const lat = parseFloat(document.getElementById('ghol-lat').value) || 17.5;
    const lng = parseFloat(document.getElementById('ghol-lng').value) || 71.0;
    const date = document.getElementById('ghol-date').value || new Date().toISOString().split('T')[0];

    // Update spawning probability
    try {
        const data = await fetchJsonWithRetry(`${API_BASE}/api/ghol/spawning-probability`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ lat, lng, date })
        }, 2, 900);

        if (data.data) {
            const result = data.data;
            document.getElementById('spawning-prob').textContent =
                `${(result.spawning_probability * 100).toFixed(0)}%`;
            document.getElementById('spawning-phase').textContent =
                `Lunar Phase: ${result.lunar_phase}`;
            document.getElementById('acoustic-prob').textContent =
                `${(result.acoustic_detection * 100).toFixed(0)}%`;
            document.getElementById('habitat-hsi').textContent =
                `${(result.habitat_suitability * 100).toFixed(0)}%`;
            document.getElementById('effort-percent').textContent =
                `${Math.round(result.spawning_probability * 100)}%`;
            document.getElementById('effort-action').textContent =
                `${result.interpretation}`;
        }
    } catch (error) {
        console.error('Error fetching spawning data:', error);
    }

    // Display additional details
    const resultsDiv = document.getElementById('ghol-results');
    resultsDiv.innerHTML = `
        <div class="alert-card info">
            <p><strong>Location:</strong> ${lat.toFixed(2)}°N, ${lng.toFixed(2)}°E</p>
            <p><strong>Analysis Date:</strong> ${date}</p>
            <p>🔄 Fetching detailed GHOL analysis...</p>
        </div>
    `;
}

async function generateTripPlan() {
    const lat = parseFloat(document.getElementById('ghol-lat').value) || 17.5;
    const lng = parseFloat(document.getElementById('ghol-lng').value) || 71.0;
    const boatType = document.getElementById('boat-type').value || 'medium_boat';
    const crewCount = parseInt(document.getElementById('crew-count').value) || 4;

    const resultsDiv = document.getElementById('trip-results');
    resultsDiv.innerHTML = '<div class="loading">📋 Generating trip plan...</div>';

    try {
        const response = await fetch(`${API_BASE}/api/ghol/trip-plan`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                lat,
                lng,
                boat_type: boatType,
                crew_count: crewCount
            })
        });

        const data = await response.json();
        if (response.ok && data.data) {
            displayTripPlan(data.data);
        } else {
            resultsDiv.innerHTML = `<div class="alert-card warning"><p>Unable to generate trip plan</p></div>`;
        }
    } catch (error) {
        console.error('Error:', error);
        resultsDiv.innerHTML = `<div class="alert-card warning"><p>Failed to generate trip plan</p></div>`;
    }
}

function displayTripPlan(tripData) {
    const resultsDiv = document.getElementById('trip-results');
    const plan = tripData.trip_plan || {};

    let html = `
        <div class="alert-card success">
            <h4>✅ ${plan.trip_recommendation || 'Trip Plan Generated'}</h4>
            <div class="forecast-details">
                <div class="detail-item">
                    <strong>Distance from Port:</strong> ${plan.distance_km || 'N/A'} km
                </div>
                <div class="detail-item">
                    <strong>Estimated Duration:</strong> ${plan.trip_duration_hours || 'N/A'} hours
                </div>
                <div class="detail-item">
                    <strong>Best Departure:</strong> ${plan.recommended_departure_time || 'Morning/Evening'}
                </div>
                <div class="detail-item">
                    <strong>Lunar Phase:</strong> ${plan.lunar_phase || 'N/A'}
                </div>
                <div class="detail-item">
                    <strong>Catch Estimate:</strong> ${plan.estimated_catch_kg || 'N/A'} kg Ghol
                </div>
            </div>
        </div>
    `;

    if (tripData.optimization_tips && tripData.optimization_tips.length > 0) {
        html += '<div class="alert-card info"><h4>💡 Optimization Tips</h4><ul style="list-style: none; padding-left: 0;">';
        tripData.optimization_tips.forEach(tip => {
            html += `<li style="padding: 0.5rem 0; border-bottom: 1px solid #eee;">${tip}</li>`;
        });
        html += '</ul></div>';
    }

    resultsDiv.innerHTML = html;
}

// ============================================================================
// OCEAN LAYERS TAB
// ============================================================================

async function loadOceanData() {
    try {
        const data = await fetchJsonWithRetry(`${API_BASE}/api/data/sources`, {}, 2, 900);

        if (data.data) {
            displayDataSources(data.data);
        }
    } catch (error) {
        console.error('Error loading ocean data:', error);
    }
}

function displayDataSources(data) {
    const sourcesList = document.getElementById('sources-status');
    const sources = data.data_sources || {};

    let html = '';
    for (const [source, status] of Object.entries(sources)) {
        const statusClass = status.status === 'active' ? 'success' : 'warning';
        html += `
            <div class="source-item">
                <strong>${source}</strong>
                <span class="alert-${statusClass}">${status.status?.toUpperCase() || 'UNKNOWN'}</span>
                <p>${status.description || ''}</p>
            </div>
        `;
    }

    sourcesList.innerHTML = html || '<p>Loading data sources...</p>';
}

// ============================================================================
// ASTRONOMICAL TAB
// ============================================================================

async function loadLunarData() {
    try {
        // Get current lunar phase
        const phaseData = await fetchJsonWithRetry(`${API_BASE}/api/lunar/phase`, {}, 2, 900);

        if (phaseData.data) {
            displayLunarPhase(phaseData.data);
        }

        // Get lunar forecast
        const forecastData = await fetchJsonWithRetry(`${API_BASE}/api/lunar/forecast`, {}, 2, 900);

        if (forecastData.data) {
            displayLunarForecast(forecastData.data);
        }

        // Get spawning windows
        const windowsData = await fetchJsonWithRetry(`${API_BASE}/api/lunar/spawning-windows`, {}, 2, 900);

        if (windowsData.data) {
            displaySpawningWindows(windowsData.data);
        }
    } catch (error) {
        console.error('Error loading lunar data:', error);
    }
}

function displayLunarPhase(data) {
    const phaseEmoji = {
        'new_moon': '🌑',
        'waxing_crescent': '🌒',
        'first_quarter': '🌓',
        'waxing_gibbous': '🌔',
        'full_moon': '🌕',
        'waning_gibbous': '🌖',
        'last_quarter': '🌗',
        'waning_crescent': '🌘'
    };

    const emoji = phaseEmoji[data.lunar_phase] || '🌙';
    document.getElementById('lunar-phase').textContent = `${emoji} ${data.lunar_phase?.replace('_', ' ').toUpperCase() || 'Unknown'}`;
    document.getElementById('illumination-text').textContent =
        `${data.illumination_percent?.toFixed(1) || 0}% illumination`;
    document.getElementById('fishing-impact').textContent = data.fishing_impact || 'Loading...';

    // Update moon graphic
    const moonGraphic = document.getElementById('moon-graphic');
    const illumination = (data.illumination_percent || 0) / 100;
    moonGraphic.style.background = `conic-gradient(white ${illumination * 360}deg, #333 0deg)`;
}

function displayLunarForecast(data) {
    const forecastList = document.getElementById('lunar-forecast');
    const forecast = data.forecast || [];

    let html = '';
    forecast.slice(0, 7).forEach(day => {
        const isSpawning = day.spawning_window ? '✓' : '';
        html += `
            <div class="forecast-item">
                <h4>${day.date}</h4>
                <div class="forecast-details">
                    <div class="detail-item">
                        <strong>Phase:</strong> ${day.phase?.replace('_', ' ').toUpperCase()}
                    </div>
                    <div class="detail-item">
                        <strong>Illumination:</strong> ${day.illumination_percent?.toFixed(1)}%
                    </div>
                    <div class="detail-item">
                        <strong>Spawning Window:</strong> ${isSpawning || '✗'}
                    </div>
                </div>
            </div>
        `;
    });

    forecastList.innerHTML = html || '<p>No forecast data available</p>';
}

function displaySpawningWindows(data) {
    const windowsList = document.getElementById('spawning-windows-list');
    const windows = data.spawning_windows || [];

    let html = '';
    windows.forEach(window => {
        html += `
            <div class="spawning-item">
                <h4>${window.date} - ${window.intensity}</h4>
                <div class="spawning-details">
                    <div class="detail-item">
                        <strong>Species:</strong> ${window.species?.join(', ').toUpperCase() || 'Multiple'}
                    </div>
                    <div class="detail-item">
                        <strong>Type:</strong> ${window.description}
                    </div>
                </div>
            </div>
        `;
    });

    windowsList.innerHTML = html || '<p>No spawning windows detected</p>';
}

// ============================================================================
// ECONOMICS TAB
// ============================================================================

async function loadEconomicData() {
    try {
        const data = await fetchJsonWithRetry(`${API_BASE}/api/economics/market-prices`, {}, 2, 900);

        if (data.data) {
            displayMarketPrices(data.data);
        }
    } catch (error) {
        console.error('Error loading economic data:', error);
    }
}

function displayMarketPrices(data) {
    const priceList = document.getElementById('price-list');
    const prices = data.market_prices || {};

    let html = '';
    for (const [species, info] of Object.entries(prices)) {
        html += `
            <div class="price-item">
                <h4>${species.toUpperCase()}</h4>
                <div class="forecast-details">
                    <div class="detail-item">
                        <strong>Price:</strong> ₹${info.price_per_kg?.toLocaleString() || 'N/A'}/kg
                    </div>
                    <div class="detail-item">
                        <strong>Category:</strong> ${info.value_category}
                    </div>
                </div>
            </div>
        `;
    }

    if (data.premium_value) {
        html += `
            <div class="alert-card success">
                <strong>🏆 Premium Value:</strong> ${data.premium_value}
            </div>
        `;
    }

    priceList.innerHTML = html || '<p>No price data available</p>';
}

async function calculateROI() {
    const catchGhol = parseFloat(document.getElementById('catch-ghol').value) || 0;
    const catchOther = parseFloat(document.getElementById('catch-other').value) || 0;
    const distance = parseFloat(document.getElementById('trip-distance').value) || 0;
    const boatType = document.getElementById('roi-boat-type').value;
    const crew = parseInt(document.getElementById('roi-crew').value) || 1;
    const days = parseFloat(document.getElementById('trip-days').value) || 0.75;

    const resultsDiv = document.getElementById('roi-results');
    resultsDiv.innerHTML = '<div class="loading">📊 Calculating ROI...</div>';

    try {
        const response = await fetch(`${API_BASE}/api/economics/trip-roi`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                catch_composition: { ghol: catchGhol, papalet: catchOther },
                distance_km: distance,
                boat_type: boatType,
                crew_count: crew,
                trip_days: days
            })
        });

        const data = await response.json();
        if (response.ok && data.data) {
            displayROIResults(data.data);
        } else {
            resultsDiv.innerHTML = '<p>Unable to calculate ROI</p>';
        }
    } catch (error) {
        console.error('Error:', error);
        resultsDiv.innerHTML = '<p>Failed to calculate ROI</p>';
    }
}

function displayROIResults(data) {
    const resultsDiv = document.getElementById('roi-results');
    const trip = data.trip || {};

    let html = `
        <div class="alert-card ${data.profitability_rating?.includes('EXCELLENT') ? 'success' :
                               data.profitability_rating?.includes('GOOD') ? 'info' : 'warning'}">
            <h4>💹 ${data.profitability_rating}</h4>
            <div style="margin-top: 1rem;">
                <div class="forecast-details">
                    <div class="detail-item">
                        <strong>Gross Revenue:</strong> ₹${trip.revenue?.toLocaleString() || 'N/A'}
                    </div>
                    <div class="detail-item">
                        <strong>Total Costs:</strong> ₹${trip.costs?.toLocaleString() || 'N/A'}
                    </div>
                    <div class="detail-item">
                        <strong>Net Profit:</strong> ₹${trip.profit?.net_profit?.toLocaleString() || 'N/A'}
                    </div>
                    <div class="detail-item">
                        <strong>ROI %:</strong> ${trip.profit?.roi_percentage?.toFixed(1) || 0}%
                    </div>
                </div>
            </div>
        </div>
    `;

    resultsDiv.innerHTML = html;
}

// ============================================================================
// SAFETY TAB
// ============================================================================

function loadSafetyData() {
    // Safety data is mostly static, just ensure it's displayed
    const weatherAlerts = document.getElementById('weather-alerts');
    if (weatherAlerts && !weatherAlerts.textContent.includes('Recent')) {
        weatherAlerts.innerHTML = `
            <div class="alert-item">
                <strong>✅ All Clear:</strong> No significant weather alerts for Arabian Sea
            </div>
            <div class="alert-item">
                <strong>⚠️ Advisories:</strong> Monitor monsoon season (Jun-Sep) for heavy seas
            </div>
        `;
    }
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function formatCurrency(value) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(value);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN');
}

console.log('SAMUDRA AI Frontend v2.0 loaded');
