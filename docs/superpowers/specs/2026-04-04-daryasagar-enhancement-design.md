# DaryaSagar Enhancement Design
**Date:** 2026-04-04  
**Project:** pfz-platform (Capacitor Android APK + FastAPI backend)  
**Status:** Approved

---

## Overview

Complete enhancement of the SAMUDRA AI fishing app, renamed to "दर्यासागर" (DaryaSagar). Fixes broken data pipeline, adds three independent PFZ layers with 10-day history, real Claude AI agent analysis, chlorophyll heatmap, INCOIS live advisory scraping, and rebuilds the APK.

---

## Section 1: Architecture & Data Pipeline

### Root Cause of Missing Data
Render free tier cold-starts (30–60s) cause all fetch calls to timeout before data arrives. Every data type needs a local file cache that serves instantly on startup.

### Scheduler (APScheduler in main.py)
```
9:00 AM IST  → compute_and_cache_pfz()  → /data/history/pfz_YYYY-MM-DD_09.json
4:00 PM IST  → compute_and_cache_pfz()  → /data/history/pfz_YYYY-MM-DD_16.json
5:30 PM IST  → fetch_incois_advisory()  → /data/history/incois_YYYY-MM-DD.json
```

### History Storage
- Directory: `/data/history/`
- Auto-pruned: files older than 10 days deleted automatically
- File naming: `pfz_YYYY-MM-DD_HH.json`, `incois_YYYY-MM-DD.json`, `agent_YYYY-MM-DD_HH.json`

### New API Endpoints
| Endpoint | Description |
|---|---|
| `GET /api/pfz/history` | List of available dates and slots (last 10 days) |
| `GET /api/pfz/history/{date}/{slot}` | PFZ data for specific date (slot: 09 or 16) |
| `GET /api/agent/history/{date}/{slot}` | Agent analysis for specific date/slot |
| `GET /api/incois/live` | Today's INCOIS markings (map-ready GeoJSON) |
| `GET /api/incois/history/{date}` | Historical INCOIS advisory for a date |
| `GET /api/chlorophyll/heatmap` | Chlorophyll grid for visual heatmap layer |

### INCOIS Data Source
- Fetch from `samudra.incois.gov.in` public portal at 5:30 PM IST daily
- Parse GeoJSON/advisory response and store as local cache
- **If fetch fails:** Only INCOIS panel shows "INCOIS data not available for today"
- **Never affects Our PFZ or AI Agent layers**

---

## Section 2: Three Independent PFZ Layers

Three completely separate layers, each with its own toggle, color scheme, and data source:

| Layer | Color | Source | Failure Behavior |
|---|---|---|---|
| **Our PFZ** | Red/Orange/Green dashed lines | Algorithm (9AM + 4PM IST) | Serve cached last run |
| **AI Agent PFZ** | Yellow dashed lines | Claude API analysis | Show "AI unavailable" badge |
| **INCOIS Advisory** | Blue/Purple dashed lines | INCOIS scrape at 5:30 PM IST | Show "INCOIS data not available today" — no map effect |

All three toggles visible in side menu independently.

---

## Section 3: Claude AI Agent (Real Intelligence)

### System Prompt Contents
- Complete fish species encyclopedia: 60+ species with habitat depth, temperature range, seasonal migration, feeding behavior, moon phase preference, current affinity
- Maharashtra/Goa/Gujarat/Karnataka fisheries context
- Current region's SST, chlorophyll, depth, wind, wave, current data
- Lunar phase, tidal data, season, time of day IST

### Claude API Call Flow
```
User clicks "Run Agent Analysis"
  → Backend collects: SST grid, CHL grid, depth, wind, wave, lunar, season
  → Sends to claude-sonnet-4-6 with fish encyclopedia system prompt
  → Claude returns: zone coordinates + species probabilities + reasoning
  → Response cached to /data/history/agent_YYYY-MM-DD_HH.json
  → Frontend renders yellow dashed zone lines with rich popup
```

### Agent Response Format
```json
{
  "zones": [
    {
      "coordinates": [[lon, lat], ...],
      "confidence": 0.84,
      "reasoning": "Strong thermal front at 28.1°C matches Surmai feeding threshold...",
      "fish_species": [
        {"name_en": "Surmai", "name_mr": "सुरमई", "probability": 0.84, "reasoning": "..."},
        {"name_en": "Pomfret", "name_mr": "पापलेट", "probability": 0.61, "reasoning": "..."}
      ],
      "best_time": "4:00 AM - 7:00 AM",
      "parameters_used": ["SST", "CHL", "depth", "lunar", "currents"]
    }
  ],
  "summary": "3 high-confidence zones found. Upwelling event detected near 17.8°N...",
  "data_quality": "high"
}
```

### Offline Fallback (Knowledge Base)
Python dict with 60+ species. Used when Claude API unavailable. Provides instant results without internet based on rule-based scoring against current parameters.

### Security
API key stored in Render environment variable `ANTHROPIC_API_KEY`. Never sent to frontend or included in APK.

---

## Section 4: Frontend Changes

### App Name
- **New name:** दर्यासागर (DaryaSagar in Marathi/Devanagari)
- Font: Noto Sans Devanagari (bundled locally in `www/` for offline support)
- Files updated: `capacitor.config.json`, `android/app/src/main/res/values/strings.xml`, `manifest.json`, topbar in `index.html`

### Screen Height Reduction
- 3mm ≈ 11px at 160dpi
- Topbar: `48px → 37px`
- Statusbar: `32px → 21px`
- Map area: `top: 48px → top: 37px`, `bottom: 32px → bottom: 21px`

### Chlorophyll Heatmap Layer
- Canvas-based overlay on Leaflet map (no extra library)
- Color scale: Blue (0–0.1 mg/m³) → Green (0.1–0.5) → Yellow (0.5–1.0) → Red (>1.0)
- Opacity: 40% (map tiles visible underneath)
- Toggle in side menu: "🌿 Chlorophyll Heatmap"
- Data from `/api/chlorophyll/heatmap` endpoint

### 10-Day History Calendar
- Button in side menu: "📅 PFZ इतिहास (History)"
- Calendar grid showing last 10 days
- Each date shows: AM slot (9AM) and PM slot (4PM)
- On date selection, shows panel with three independent layer toggles:
  ```
  📅 April 3, 2026 — 4:00 PM
  ┌─────────────────────────────────┐
  │  🐟 Our PFZ Zones      [ON/OFF] │
  │  🤖 AI Agent Zones     [ON/OFF] │
  │  🏛️ INCOIS Advisory    [ON/OFF] │
  │                                 │
  │  [9 AM Run]  [4 PM Run]         │
  └─────────────────────────────────┘
  ```
- INCOIS shows "not available" badge if that day's fetch failed
- AI Agent shows "not run" badge if analysis was not triggered
- Switching dates clears all previous historical layers
- Live (today) highlighted in green

### INCOIS Map Layer
- Blue dashed polylines on map (distinct from our red/orange/green)
- Existing INCOIS panel upgraded to show actual fetched advisory zones
- If no data: panel shows "INCOIS data not available for today"
- Independent toggle: does not affect other layers

---

## Section 5: APK Build

### Build Steps
1. Apply all frontend changes to `www/index.html`
2. Update app name in config files
3. `npx cap sync android`
4. `cd android && ./gradlew assembleRelease`
5. Output: `android/app/build/outputs/apk/release/app-release-unsigned.apk`

### Files Changed
**Backend:**
- `main.py` — add APScheduler, new endpoints, Claude API integration, INCOIS scraper
- `scheduler.py` — enhanced with IST-scheduled jobs
- `app/agents/` — new `claude_agent.py` with real API calls
- `requirements.txt` — add `anthropic`, `apscheduler`, `httpx`

**Frontend:**
- `www/index.html` — all UI changes (name, height, 3 layers, calendar, CHL layer)
- `www/` — add Noto Sans Devanagari font files

**Android:**
- `android/app/src/main/res/values/strings.xml` — app name
- `capacitor.config.json` — app name
- `manifest.json` — app name

---

## Fish Species Knowledge Base (Sample)

```python
FISH_KNOWLEDGE = {
  "Surmai": {
    "name_mr": "सुरमई", "name_hi": "सुरमई",
    "sst_range": (26, 30), "optimal_sst": 28,
    "depth_range": (30, 120), "optimal_depth": 60,
    "chl_affinity": "medium",  # 0.2-0.8 mg/m³
    "moon_preference": "new_moon",
    "seasons": [10, 11, 12, 1, 2],  # Oct-Feb peak
    "current_preference": "moderate",
    "habitat": "pelagic, open ocean, thermal fronts"
  },
  # ... 59 more species
}
```

---

## Constraints & Rules

1. INCOIS failure NEVER affects Our PFZ or AI Agent layers
2. API key stays in backend environment only
3. History auto-pruned at 10 days
4. All three layers independently toggleable in both live and historical views
5. If backend cold-starts, cached files serve instantly
6. App works offline for map viewing; data layers require connectivity
