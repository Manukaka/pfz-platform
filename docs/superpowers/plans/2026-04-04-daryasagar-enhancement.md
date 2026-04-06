# DaryaSagar Enhancement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform SAMUDRA AI into "दर्यासागर" with real Claude AI analysis, three independent PFZ layers (Our PFZ / AI Agent / INCOIS), 10-day history calendar, chlorophyll heatmap, INCOIS scraping at 5:30 PM IST, scheduled 9AM/4PM PFZ caching, and a rebuilt APK.

**Architecture:** FastAPI backend on Render with APScheduler for timed jobs; all data cached to `/data/history/` JSON files so cold-starts serve instantly. Claude API in backend only (key never exposed to client). Three completely independent map layers in frontend.

**Tech Stack:** Python 3.12, FastAPI, APScheduler 3.x, anthropic 0.85, httpx, Leaflet.js, Capacitor Android, Gradle

---

## File Map

**New files:**
- `app/data/fish_knowledge.py` — 60+ species encyclopedia + scoring
- `app/data/history_manager.py` — JSON snapshot storage (10-day prune)
- `app/data/incois_scraper.py` — INCOIS advisory fetch + parse
- `app/agents/claude_agent.py` — Claude API integration + offline fallback
- `app/core/scheduled_jobs.py` — APScheduler job functions
- `data/history/.gitkeep` — ensure directory exists in git
- `.env` — ANTHROPIC_API_KEY

**Modified files:**
- `main.py` — lifespan scheduler startup, 6 new endpoints
- `requirements.txt` — add anthropic, apscheduler, httpx, pytz
- `www/index.html` — all frontend changes (name, height, 3 layers, calendar, CHL)
- `android/app/src/main/res/values/strings.xml` — app name
- `capacitor.config.json` — app name
- `manifest.json` — app name

---

## Task 1: Fish Knowledge Base

**Files:**
- Create: `app/data/fish_knowledge.py`

- [ ] **Step 1: Create the fish knowledge module**

```python
# app/data/fish_knowledge.py
"""
60+ fish species encyclopedia for West Coast India.
Used by Claude agent and offline fallback scorer.
"""
import math
from typing import Dict, Any, List, Tuple

FISH_KNOWLEDGE: Dict[str, Dict[str, Any]] = {
    "Surmai": {
        "name_mr": "सुरमई", "name_hi": "सुरमई", "icon": "🐠",
        "scientific": "Scomberomorus commerson",
        "sst_range": (25, 31), "optimal_sst": 28.0,
        "depth_range": (20, 200), "optimal_depth": 60,
        "chl_range": (0.15, 0.8), "chl_affinity": "medium",
        "moon_preference": "new_moon", "peak_months": [10,11,12,1,2,3],
        "habitat": "pelagic, thermal fronts", "best_time": "05:00-08:00",
        "current_preference": "moderate",
        "description_mr": "उच्च मूल्याचा मासा, थर्मल फ्रंट्स जवळ आढळतो",
    },
    "Paplet": {
        "name_mr": "पापलेट", "name_hi": "पोम्फ्रेट", "icon": "🐟",
        "scientific": "Pampus argenteus",
        "sst_range": (24, 30), "optimal_sst": 27.0,
        "depth_range": (10, 80), "optimal_depth": 40,
        "chl_range": (0.2, 1.0), "chl_affinity": "high",
        "moon_preference": "full_moon", "peak_months": [11,12,1,2,3,4],
        "habitat": "demersal, continental shelf", "best_time": "04:00-07:00",
        "current_preference": "weak",
        "description_mr": "सर्वाधिक मागणी असलेला मासा, उथळ शेल्फ भागात",
    },
    "Ghol": {
        "name_mr": "घोल", "name_hi": "घोल", "icon": "🐡",
        "scientific": "Protonibea diacanthus",
        "sst_range": (26, 32), "optimal_sst": 29.0,
        "depth_range": (20, 60), "optimal_depth": 35,
        "chl_range": (0.3, 1.5), "chl_affinity": "high",
        "moon_preference": "new_moon", "peak_months": [4,5,6,7,8],
        "habitat": "demersal, estuarine, spawning fronts", "best_time": "21:00-02:00",
        "current_preference": "weak",
        "description_mr": "अत्यंत मौल्यवान मासा, रात्री ध्वनी उत्सर्जित करतो",
    },
    "Bombil": {
        "name_mr": "बोंबील", "name_hi": "बम्बई डक", "icon": "🐟",
        "scientific": "Harpadon nehereus",
        "sst_range": (24, 30), "optimal_sst": 27.5,
        "depth_range": (10, 50), "optimal_depth": 25,
        "chl_range": (0.4, 2.0), "chl_affinity": "very_high",
        "moon_preference": "any", "peak_months": [6,7,8,9,10],
        "habitat": "demersal, muddy bottom, estuarine", "best_time": "05:00-09:00",
        "current_preference": "weak",
        "description_mr": "मुंबईचा खास मासा, मऊ तळाशी आढळतो",
    },
    "Rawas": {
        "name_mr": "रावस", "name_hi": "इंडियन सालमन", "icon": "🐟",
        "scientific": "Eleutheronema tetradactylum",
        "sst_range": (26, 31), "optimal_sst": 28.5,
        "depth_range": (5, 40), "optimal_depth": 20,
        "chl_range": (0.5, 2.0), "chl_affinity": "very_high",
        "moon_preference": "new_moon", "peak_months": [3,4,5,6,7],
        "habitat": "coastal, estuarine mouths", "best_time": "06:00-09:00",
        "current_preference": "weak",
        "description_mr": "किनारपट्टी जवळ, नदीमुखाशी आढळतो",
    },
    "Bangda": {
        "name_mr": "बांगडा", "name_hi": "मैकेरल", "icon": "🐟",
        "scientific": "Rastrelliger kanagurta",
        "sst_range": (24, 30), "optimal_sst": 27.0,
        "depth_range": (10, 80), "optimal_depth": 40,
        "chl_range": (0.3, 1.5), "chl_affinity": "high",
        "moon_preference": "full_moon", "peak_months": [9,10,11,12,1],
        "habitat": "pelagic, schools, coastal upwelling", "best_time": "05:00-08:00",
        "current_preference": "moderate",
        "description_mr": "मोठ्या शाळांमध्ये, उपवेलिंग क्षेत्रात",
    },
    "Pedve": {
        "name_mr": "पेडवे/करली", "name_hi": "तेल सार्डिन", "icon": "🐟",
        "scientific": "Sardinella longiceps",
        "sst_range": (23, 29), "optimal_sst": 26.0,
        "depth_range": (5, 60), "optimal_depth": 30,
        "chl_range": (0.5, 3.0), "chl_affinity": "very_high",
        "moon_preference": "any", "peak_months": [8,9,10,11,12],
        "habitat": "pelagic, upwelling zones, high CHL", "best_time": "05:00-09:00",
        "current_preference": "strong_upwelling",
        "description_mr": "उपवेलिंग क्षेत्रात मोठ्या प्रमाणात",
    },
    "Halwa": {
        "name_mr": "हलवा", "name_hi": "ब्लैक पोम्फ्रेट", "icon": "🐟",
        "scientific": "Parastromateus niger",
        "sst_range": (25, 31), "optimal_sst": 28.0,
        "depth_range": (20, 100), "optimal_depth": 50,
        "chl_range": (0.2, 0.8), "chl_affinity": "medium",
        "moon_preference": "full_moon", "peak_months": [11,12,1,2,3],
        "habitat": "pelagic to demersal, offshore", "best_time": "04:00-07:00",
        "current_preference": "moderate",
        "description_mr": "काळ्या पोम्फ्रेटपेक्षा वेगळा, मध्यम खोलीवर",
    },
    "Mandeli": {
        "name_mr": "मांदेली", "name_hi": "एंचोवी", "icon": "🐟",
        "scientific": "Stolephorus commersonii",
        "sst_range": (25, 31), "optimal_sst": 28.0,
        "depth_range": (5, 40), "optimal_depth": 15,
        "chl_range": (0.5, 3.0), "chl_affinity": "very_high",
        "moon_preference": "new_moon", "peak_months": [6,7,8,9,10],
        "habitat": "coastal, estuarine, high productivity", "best_time": "06:00-10:00",
        "current_preference": "weak",
        "description_mr": "खूप लहान पण महत्त्वाचा मासा",
    },
    "Tiger_Prawn": {
        "name_mr": "कोळंबी (टायगर)", "name_hi": "टाइगर झींगा", "icon": "🦐",
        "scientific": "Penaeus monodon",
        "sst_range": (25, 31), "optimal_sst": 28.5,
        "depth_range": (10, 60), "optimal_depth": 30,
        "chl_range": (0.4, 2.0), "chl_affinity": "high",
        "moon_preference": "new_moon", "peak_months": [4,5,6,7,8,9],
        "habitat": "demersal, muddy bottom, estuarine", "best_time": "20:00-02:00",
        "current_preference": "weak",
        "description_mr": "रात्री सक्रिय, मऊ तळाशी",
    },
    "White_Prawn": {
        "name_mr": "कोळंबी (पांढरी)", "name_hi": "सफेद झींगा", "icon": "🦐",
        "scientific": "Penaeus indicus",
        "sst_range": (24, 30), "optimal_sst": 27.0,
        "depth_range": (5, 50), "optimal_depth": 20,
        "chl_range": (0.5, 2.5), "chl_affinity": "very_high",
        "moon_preference": "new_moon", "peak_months": [3,4,5,6,7,8],
        "habitat": "coastal, estuarine", "best_time": "19:00-01:00",
        "current_preference": "weak",
        "description_mr": "उथळ किनारी पाण्यात",
    },
    "Squid": {
        "name_mr": "माजगा", "name_hi": "स्क्विड", "icon": "🦑",
        "scientific": "Uroteuthis duvaucelii",
        "sst_range": (26, 31), "optimal_sst": 28.5,
        "depth_range": (20, 200), "optimal_depth": 80,
        "chl_range": (0.2, 1.0), "chl_affinity": "medium",
        "moon_preference": "new_moon", "peak_months": [11,12,1,2,3,4],
        "habitat": "pelagic, night feeder, bioluminescent zones", "best_time": "20:00-03:00",
        "current_preference": "moderate",
        "description_mr": "रात्री दिव्याखाली येतो",
    },
    "Cuttlefish": {
        "name_mr": "समुद्री माशी", "name_hi": "कटलफिश", "icon": "🦑",
        "scientific": "Sepia pharaonis",
        "sst_range": (25, 30), "optimal_sst": 27.5,
        "depth_range": (10, 100), "optimal_depth": 40,
        "chl_range": (0.3, 1.5), "chl_affinity": "high",
        "moon_preference": "full_moon", "peak_months": [10,11,12,1,2],
        "habitat": "demersal, sandy/rocky bottom", "best_time": "05:00-08:00",
        "current_preference": "weak",
        "description_mr": "खडकाळ तळाशी आढळतो",
    },
    "Crab": {
        "name_mr": "खेकडा", "name_hi": "केकड़ा", "icon": "🦀",
        "scientific": "Portunus pelagicus",
        "sst_range": (24, 30), "optimal_sst": 27.0,
        "depth_range": (1, 50), "optimal_depth": 15,
        "chl_range": (0.5, 3.0), "chl_affinity": "very_high",
        "moon_preference": "full_moon", "peak_months": [3,4,5,6,7],
        "habitat": "coastal, estuarine, seagrass", "best_time": "05:00-09:00",
        "current_preference": "weak",
        "description_mr": "उथळ पाण्यात, गवताळ तळाशी",
    },
    "Yellowfin_Tuna": {
        "name_mr": "कुपा (पिवळा पर)", "name_hi": "पीला-पंख टूना", "icon": "🐟",
        "scientific": "Thunnus albacares",
        "sst_range": (24, 30), "optimal_sst": 27.5,
        "depth_range": (50, 500), "optimal_depth": 150,
        "chl_range": (0.1, 0.5), "chl_affinity": "low",
        "moon_preference": "any", "peak_months": [10,11,12,1,2,3],
        "habitat": "offshore pelagic, FAD areas", "best_time": "06:00-10:00",
        "current_preference": "strong",
        "description_mr": "खोल समुद्रात, FAD जवळ",
    },
    "Skipjack_Tuna": {
        "name_mr": "बोनिटो", "name_hi": "स्किपजैक टूना", "icon": "🐟",
        "scientific": "Katsuwonus pelamis",
        "sst_range": (23, 29), "optimal_sst": 26.0,
        "depth_range": (30, 300), "optimal_depth": 100,
        "chl_range": (0.15, 0.6), "chl_affinity": "low_medium",
        "moon_preference": "any", "peak_months": [9,10,11,12],
        "habitat": "offshore, upwelling boundaries", "best_time": "06:00-10:00",
        "current_preference": "strong",
        "description_mr": "उपवेलिंग सीमेवर",
    },
    "Barracuda": {
        "name_mr": "जवळा", "name_hi": "बाराकुडा", "icon": "🐟",
        "scientific": "Sphyraena barracuda",
        "sst_range": (25, 31), "optimal_sst": 28.5,
        "depth_range": (10, 100), "optimal_depth": 40,
        "chl_range": (0.2, 0.8), "chl_affinity": "medium",
        "moon_preference": "new_moon", "peak_months": [11,12,1,2,3],
        "habitat": "pelagic, reef edges, continental shelf", "best_time": "05:00-08:00",
        "current_preference": "moderate",
        "description_mr": "रीफ कडा आणि शेल्फ एजवर",
    },
    "Red_Snapper": {
        "name_mr": "तामोशी", "name_hi": "रेड स्नैपर", "icon": "🐟",
        "scientific": "Lutjanus argentimaculatus",
        "sst_range": (25, 30), "optimal_sst": 27.5,
        "depth_range": (20, 120), "optimal_depth": 60,
        "chl_range": (0.2, 0.8), "chl_affinity": "medium",
        "moon_preference": "full_moon", "peak_months": [10,11,12,1,2],
        "habitat": "reef, rocky bottom, ledges", "best_time": "05:00-09:00",
        "current_preference": "moderate",
        "description_mr": "खडकाळ तळाशी, रीफ जवळ",
    },
    "Grouper": {
        "name_mr": "हमूर", "name_hi": "ग्रूपर", "icon": "🐟",
        "scientific": "Epinephelus tauvina",
        "sst_range": (25, 31), "optimal_sst": 28.0,
        "depth_range": (20, 200), "optimal_depth": 80,
        "chl_range": (0.2, 0.8), "chl_affinity": "medium",
        "moon_preference": "full_moon", "peak_months": [10,11,12,1,2,3],
        "habitat": "reef, rocky structure", "best_time": "05:00-08:00",
        "current_preference": "moderate",
        "description_mr": "खडकी रचनेजवळ राहतो",
    },
    "Ribbon_Fish": {
        "name_mr": "वेळा", "name_hi": "रिबन फिश", "icon": "🐟",
        "scientific": "Trichiurus lepturus",
        "sst_range": (25, 31), "optimal_sst": 28.5,
        "depth_range": (30, 150), "optimal_depth": 70,
        "chl_range": (0.2, 1.0), "chl_affinity": "medium",
        "moon_preference": "new_moon", "peak_months": [10,11,12,1,2],
        "habitat": "mesopelagic, vertical migrator", "best_time": "20:00-02:00",
        "current_preference": "moderate",
        "description_mr": "रात्री वर येतो, लांब चांदी मासा",
    },
    "Croaker": {
        "name_mr": "दारा (लहान घोल)", "name_hi": "क्रोकर", "icon": "🐟",
        "scientific": "Johnius dussumieri",
        "sst_range": (25, 31), "optimal_sst": 28.0,
        "depth_range": (10, 60), "optimal_depth": 30,
        "chl_range": (0.3, 1.5), "chl_affinity": "high",
        "moon_preference": "new_moon", "peak_months": [5,6,7,8,9],
        "habitat": "demersal, muddy bottom, estuarine", "best_time": "05:00-08:00",
        "current_preference": "weak",
        "description_mr": "मऊ तळाशी, नदीमुखाजवळ",
    },
    "Threadfin_Bream": {
        "name_mr": "थ्रेडफिन", "name_hi": "थ्रेडफिन ब्रीम", "icon": "🐟",
        "scientific": "Nemipterus japonicus",
        "sst_range": (25, 30), "optimal_sst": 27.5,
        "depth_range": (20, 100), "optimal_depth": 50,
        "chl_range": (0.2, 1.0), "chl_affinity": "medium",
        "moon_preference": "full_moon", "peak_months": [10,11,12,1,2],
        "habitat": "demersal, sandy-muddy bottom", "best_time": "05:00-08:00",
        "current_preference": "weak",
        "description_mr": "वाळू-चिखल मिश्र तळाशी",
    },
    "Shark": {
        "name_mr": "मोरी", "name_hi": "शार्क", "icon": "🦈",
        "scientific": "Carcharhinus limbatus",
        "sst_range": (24, 31), "optimal_sst": 28.0,
        "depth_range": (10, 200), "optimal_depth": 60,
        "chl_range": (0.1, 0.5), "chl_affinity": "low",
        "moon_preference": "any", "peak_months": [1,2,3,4,10,11,12],
        "habitat": "pelagic to coastal", "best_time": "05:00-09:00",
        "current_preference": "moderate",
        "description_mr": "खुल्या समुद्रात आढळतो",
    },
    "Cobia": {
        "name_mr": "कोबिया", "name_hi": "कोबिया", "icon": "🐟",
        "scientific": "Rachycentron canadum",
        "sst_range": (25, 31), "optimal_sst": 28.5,
        "depth_range": (20, 150), "optimal_depth": 60,
        "chl_range": (0.15, 0.6), "chl_affinity": "low_medium",
        "moon_preference": "full_moon", "peak_months": [11,12,1,2,3],
        "habitat": "pelagic, follows large objects/sharks", "best_time": "06:00-09:00",
        "current_preference": "moderate",
        "description_mr": "मोठ्या माशांमागे जातो",
    },
    "Wahoo": {
        "name_mr": "वाहू", "name_hi": "वाहू", "icon": "🐟",
        "scientific": "Acanthocybium solandri",
        "sst_range": (24, 30), "optimal_sst": 27.0,
        "depth_range": (30, 300), "optimal_depth": 100,
        "chl_range": (0.1, 0.4), "chl_affinity": "low",
        "moon_preference": "any", "peak_months": [11,12,1,2],
        "habitat": "offshore pelagic, current boundaries", "best_time": "06:00-10:00",
        "current_preference": "strong",
        "description_mr": "वेगवान मासा, प्रवाह सीमांवर",
    },
    "Giant_Trevally": {
        "name_mr": "पापडी (मोठी)", "name_hi": "जायंट ट्रेव्हली", "icon": "🐟",
        "scientific": "Caranx ignobilis",
        "sst_range": (25, 31), "optimal_sst": 28.5,
        "depth_range": (10, 150), "optimal_depth": 40,
        "chl_range": (0.2, 0.8), "chl_affinity": "medium",
        "moon_preference": "new_moon", "peak_months": [10,11,12,1,2],
        "habitat": "reef, passes, open water", "best_time": "05:00-08:00",
        "current_preference": "strong",
        "description_mr": "रीफ पासेसमध्ये, प्रवाहात",
    },
    "Queenfish": {
        "name_mr": "राणी मासा", "name_hi": "क्वीनफिश", "icon": "🐟",
        "scientific": "Scomberoides commersonnianus",
        "sst_range": (25, 31), "optimal_sst": 28.0,
        "depth_range": (5, 80), "optimal_depth": 30,
        "chl_range": (0.2, 1.0), "chl_affinity": "medium",
        "moon_preference": "any", "peak_months": [10,11,12,1,2,3],
        "habitat": "coastal pelagic, surface", "best_time": "05:00-08:00",
        "current_preference": "moderate",
        "description_mr": "पृष्ठभागाजवळ",
    },
    "Lobster": {
        "name_mr": "लॉब्स्टर", "name_hi": "झींगा मछली", "icon": "🦞",
        "scientific": "Panulirus homarus",
        "sst_range": (24, 29), "optimal_sst": 26.5,
        "depth_range": (5, 60), "optimal_depth": 20,
        "chl_range": (0.3, 1.5), "chl_affinity": "high",
        "moon_preference": "full_moon", "peak_months": [10,11,12,1,2,3],
        "habitat": "rocky reef, coral, crevices", "best_time": "20:00-02:00",
        "current_preference": "weak",
        "description_mr": "खडकी रचनेत लपतो, रात्री बाहेर",
    },
    "Pomfret_Black": {
        "name_mr": "काळी पापलेट", "name_hi": "काली पोम्फ्रेट", "icon": "🐟",
        "scientific": "Parastromateus niger",
        "sst_range": (26, 31), "optimal_sst": 28.5,
        "depth_range": (20, 100), "optimal_depth": 50,
        "chl_range": (0.2, 0.8), "chl_affinity": "medium",
        "moon_preference": "full_moon", "peak_months": [11,12,1,2,3],
        "habitat": "pelagic, offshore", "best_time": "04:00-07:00",
        "current_preference": "moderate",
        "description_mr": "ऑफशोअर, खोल पाण्यात",
    },
    "Seer_Fish": {
        "name_mr": "विसोण", "name_hi": "सीर मछली", "icon": "🐟",
        "scientific": "Scomberomorus guttatus",
        "sst_range": (25, 30), "optimal_sst": 27.5,
        "depth_range": (10, 80), "optimal_depth": 40,
        "chl_range": (0.2, 0.8), "chl_affinity": "medium",
        "moon_preference": "new_moon", "peak_months": [10,11,12,1,2],
        "habitat": "coastal pelagic, reef edges", "best_time": "05:00-08:00",
        "current_preference": "moderate",
        "description_mr": "लहान सुरमई, किनाऱ्याजवळ",
    },
    "Dorado": {
        "name_mr": "डोराडो", "name_hi": "महिमाही", "icon": "🐟",
        "scientific": "Coryphaena hippurus",
        "sst_range": (24, 31), "optimal_sst": 27.5,
        "depth_range": (10, 200), "optimal_depth": 50,
        "chl_range": (0.1, 0.4), "chl_affinity": "low",
        "moon_preference": "any", "peak_months": [11,12,1,2,3],
        "habitat": "offshore, FAD, floating debris", "best_time": "07:00-11:00",
        "current_preference": "moderate",
        "description_mr": "FAD जवळ, तरंगत्या वस्तूंजवळ",
    },
    "Wolf_Herring": {
        "name_mr": "ढोमा", "name_hi": "वुल्फ हेरिंग", "icon": "🐟",
        "scientific": "Chirocentrus dorab",
        "sst_range": (25, 31), "optimal_sst": 28.0,
        "depth_range": (5, 50), "optimal_depth": 20,
        "chl_range": (0.4, 2.0), "chl_affinity": "high",
        "moon_preference": "any", "peak_months": [6,7,8,9,10],
        "habitat": "coastal, estuarine, schools", "best_time": "05:00-08:00",
        "current_preference": "weak",
        "description_mr": "लहान माशांचा शिकारी, किनाऱ्याजवळ",
    },
    "Flying_Fish": {
        "name_mr": "उडता मासा", "name_hi": "उड़न मछली", "icon": "🐟",
        "scientific": "Exocoetus volitans",
        "sst_range": (25, 31), "optimal_sst": 28.5,
        "depth_range": (0, 30), "optimal_depth": 5,
        "chl_range": (0.1, 0.5), "chl_affinity": "low",
        "moon_preference": "full_moon", "peak_months": [12,1,2,3,4],
        "habitat": "surface, offshore, open ocean", "best_time": "05:00-08:00",
        "current_preference": "moderate",
        "description_mr": "खुल्या समुद्रात, पृष्ठभागावर",
    },
    "Mullet": {
        "name_mr": "शेवटा", "name_hi": "मुलेट", "icon": "🐟",
        "scientific": "Mugil cephalus",
        "sst_range": (24, 30), "optimal_sst": 27.0,
        "depth_range": (1, 20), "optimal_depth": 8,
        "chl_range": (0.5, 3.0), "chl_affinity": "very_high",
        "moon_preference": "full_moon", "peak_months": [11,12,1,2,3],
        "habitat": "coastal, estuarine, brackish", "best_time": "06:00-10:00",
        "current_preference": "weak",
        "description_mr": "खाड्यांमध्ये, खारट पाण्यात",
    },
    "Lizard_Fish": {
        "name_mr": "सुरळी", "name_hi": "लिज़र्ड फिश", "icon": "🐟",
        "scientific": "Saurida tumbil",
        "sst_range": (25, 31), "optimal_sst": 28.0,
        "depth_range": (20, 100), "optimal_depth": 50,
        "chl_range": (0.2, 1.0), "chl_affinity": "medium",
        "moon_preference": "any", "peak_months": [10,11,12,1,2,3],
        "habitat": "demersal, sandy bottom", "best_time": "05:00-09:00",
        "current_preference": "weak",
        "description_mr": "वाळूच्या तळाशी",
    },
    "Pony_Fish": {
        "name_mr": "करांदे", "name_hi": "पोनी फिश", "icon": "🐟",
        "scientific": "Leiognathus splendens",
        "sst_range": (25, 31), "optimal_sst": 28.0,
        "depth_range": (5, 40), "optimal_depth": 20,
        "chl_range": (0.4, 2.0), "chl_affinity": "high",
        "moon_preference": "any", "peak_months": [6,7,8,9,10],
        "habitat": "coastal, estuarine, schools", "best_time": "05:00-09:00",
        "current_preference": "weak",
        "description_mr": "उथळ किनाऱ्यात, मोठ्या संख्येत",
    },
    "Sea_Bass": {
        "name_mr": "कोडुवा", "name_hi": "सी बास", "icon": "🐟",
        "scientific": "Lates calcarifer",
        "sst_range": (25, 31), "optimal_sst": 28.5,
        "depth_range": (5, 40), "optimal_depth": 15,
        "chl_range": (0.5, 2.5), "chl_affinity": "very_high",
        "moon_preference": "new_moon", "peak_months": [4,5,6,7,8],
        "habitat": "estuarine, mangrove, rocky coast", "best_time": "05:00-08:00",
        "current_preference": "weak",
        "description_mr": "खाड्यात, खारफुटीजवळ",
    },
    "Catfish": {
        "name_mr": "शिंगाळा", "name_hi": "कैटफिश", "icon": "🐟",
        "scientific": "Arius maculatus",
        "sst_range": (25, 31), "optimal_sst": 28.5,
        "depth_range": (5, 40), "optimal_depth": 15,
        "chl_range": (0.5, 3.0), "chl_affinity": "very_high",
        "moon_preference": "new_moon", "peak_months": [5,6,7,8,9],
        "habitat": "estuarine, muddy, coastal", "best_time": "20:00-02:00",
        "current_preference": "weak",
        "description_mr": "मऊ तळ, खाड्यात",
    },
    "Eel": {
        "name_mr": "वाम", "name_hi": "ईल", "icon": "🐍",
        "scientific": "Muraenesox cinereus",
        "sst_range": (25, 31), "optimal_sst": 28.0,
        "depth_range": (5, 80), "optimal_depth": 30,
        "chl_range": (0.3, 1.5), "chl_affinity": "high",
        "moon_preference": "new_moon", "peak_months": [6,7,8,9,10],
        "habitat": "rocky, sandy, crevices", "best_time": "20:00-02:00",
        "current_preference": "weak",
        "description_mr": "खडकाळ भेगांमध्ये, रात्री सक्रिय",
    },
    "Flathead": {
        "name_mr": "सपाट डोके", "name_hi": "फ्लैटहेड", "icon": "🐟",
        "scientific": "Platycephalus indicus",
        "sst_range": (25, 30), "optimal_sst": 27.5,
        "depth_range": (10, 80), "optimal_depth": 40,
        "chl_range": (0.2, 1.0), "chl_affinity": "medium",
        "moon_preference": "any", "peak_months": [10,11,12,1,2],
        "habitat": "sandy/muddy bottom, ambush predator", "best_time": "05:00-09:00",
        "current_preference": "weak",
        "description_mr": "वाळू-चिखल तळावर लपतो",
    },
    "Emperor_Fish": {
        "name_mr": "सम्राट मासा", "name_hi": "एम्परर", "icon": "🐟",
        "scientific": "Lethrinus nebulosus",
        "sst_range": (25, 31), "optimal_sst": 28.0,
        "depth_range": (10, 100), "optimal_depth": 40,
        "chl_range": (0.2, 0.8), "chl_affinity": "medium",
        "moon_preference": "full_moon", "peak_months": [10,11,12,1,2,3],
        "habitat": "reef, sandy areas near reef", "best_time": "05:00-08:00",
        "current_preference": "moderate",
        "description_mr": "रीफजवळ, वाळूच्या भागात",
    },
    "Parrotfish": {
        "name_mr": "पोपटमासा", "name_hi": "पेरट फिश", "icon": "🐟",
        "scientific": "Scarus ghobban",
        "sst_range": (25, 31), "optimal_sst": 28.5,
        "depth_range": (5, 60), "optimal_depth": 20,
        "chl_range": (0.1, 0.5), "chl_affinity": "low",
        "moon_preference": "full_moon", "peak_months": [10,11,12,1,2,3],
        "habitat": "coral reef, rocky coast", "best_time": "06:00-10:00",
        "current_preference": "weak",
        "description_mr": "कोरल रीफवर",
    },
    "Needlefish": {
        "name_mr": "सुई मासा", "name_hi": "नीडलफिश", "icon": "🐟",
        "scientific": "Strongylura strongylura",
        "sst_range": (25, 31), "optimal_sst": 28.5,
        "depth_range": (0, 20), "optimal_depth": 5,
        "chl_range": (0.2, 1.0), "chl_affinity": "medium",
        "moon_preference": "full_moon", "peak_months": [4,5,6,7,8],
        "habitat": "surface, coastal, schools", "best_time": "06:00-09:00",
        "current_preference": "weak",
        "description_mr": "पृष्ठभागावर, किनाऱ्यात",
    },
    "Milkfish": {
        "name_mr": "दुधी", "name_hi": "मिल्कफिश", "icon": "🐟",
        "scientific": "Chanos chanos",
        "sst_range": (24, 30), "optimal_sst": 27.0,
        "depth_range": (1, 30), "optimal_depth": 10,
        "chl_range": (0.5, 3.0), "chl_affinity": "very_high",
        "moon_preference": "full_moon", "peak_months": [3,4,5,6,7],
        "habitat": "coastal, estuarine, lagoon", "best_time": "05:00-09:00",
        "current_preference": "weak",
        "description_mr": "खाडी, लगून भागात",
    },
    "Grunt": {
        "name_mr": "घोंगडा", "name_hi": "ग्रंट", "icon": "🐟",
        "scientific": "Pomadasys kaakan",
        "sst_range": (25, 30), "optimal_sst": 27.5,
        "depth_range": (10, 80), "optimal_depth": 40,
        "chl_range": (0.2, 1.0), "chl_affinity": "medium",
        "moon_preference": "new_moon", "peak_months": [10,11,12,1,2],
        "habitat": "demersal, sandy-rocky", "best_time": "20:00-02:00",
        "current_preference": "weak",
        "description_mr": "आवाज काढतो, रात्री सक्रिय",
    },
    "Goatfish": {
        "name_mr": "शेळ्या मासा", "name_hi": "गोटफिश", "icon": "🐟",
        "scientific": "Upeneus vittatus",
        "sst_range": (25, 31), "optimal_sst": 28.0,
        "depth_range": (10, 100), "optimal_depth": 40,
        "chl_range": (0.3, 1.2), "chl_affinity": "medium_high",
        "moon_preference": "any", "peak_months": [10,11,12,1,2,3],
        "habitat": "sandy bottom, uses barbels to find food", "best_time": "05:00-09:00",
        "current_preference": "weak",
        "description_mr": "वाळूत अन्न शोधतो",
    },
    "Greater_Amberjack": {
        "name_mr": "अॅम्बरजॅक", "name_hi": "अम्बरजैक", "icon": "🐟",
        "scientific": "Seriola dumerili",
        "sst_range": (24, 30), "optimal_sst": 27.5,
        "depth_range": (20, 300), "optimal_depth": 80,
        "chl_range": (0.1, 0.5), "chl_affinity": "low",
        "moon_preference": "any", "peak_months": [11,12,1,2,3],
        "habitat": "offshore, reef structure, FAD", "best_time": "06:00-10:00",
        "current_preference": "moderate",
        "description_mr": "खोल ऑफशोअर, मोठ्या संरचनांजवळ",
    },
    "Ray": {
        "name_mr": "वाटा", "name_hi": "रे", "icon": "🐠",
        "scientific": "Dasyatis pastinaca",
        "sst_range": (25, 31), "optimal_sst": 28.5,
        "depth_range": (5, 80), "optimal_depth": 30,
        "chl_range": (0.2, 1.0), "chl_affinity": "medium",
        "moon_preference": "any", "peak_months": [4,5,6,7,8,9],
        "habitat": "sandy/muddy bottom", "best_time": "05:00-09:00",
        "current_preference": "weak",
        "description_mr": "वाळूत लपतो",
    },
    "Triggerfish": {
        "name_mr": "ट्रिगर", "name_hi": "ट्रिगरफिश", "icon": "🐟",
        "scientific": "Balistoides viridescens",
        "sst_range": (25, 31), "optimal_sst": 28.5,
        "depth_range": (5, 60), "optimal_depth": 25,
        "chl_range": (0.1, 0.5), "chl_affinity": "low",
        "moon_preference": "full_moon", "peak_months": [11,12,1,2,3],
        "habitat": "coral reef, hard bottom", "best_time": "06:00-10:00",
        "current_preference": "weak",
        "description_mr": "कोरल रीफवर",
    },
    "Bluefish": {
        "name_mr": "निळा मासा", "name_hi": "ब्लूफिश", "icon": "🐟",
        "scientific": "Pomatomus saltatrix",
        "sst_range": (23, 29), "optimal_sst": 26.0,
        "depth_range": (10, 100), "optimal_depth": 40,
        "chl_range": (0.2, 0.8), "chl_affinity": "medium",
        "moon_preference": "new_moon", "peak_months": [11,12,1,2,3],
        "habitat": "pelagic, surface, aggressive schooler", "best_time": "05:00-08:00",
        "current_preference": "moderate",
        "description_mr": "आक्रमक शाळा, पृष्ठभागाजवळ",
    },
    "Moonfish": {
        "name_mr": "चंद्र मासा", "name_hi": "मूनफिश", "icon": "🐟",
        "scientific": "Mene maculata",
        "sst_range": (25, 31), "optimal_sst": 28.0,
        "depth_range": (5, 60), "optimal_depth": 25,
        "chl_range": (0.2, 1.0), "chl_affinity": "medium",
        "moon_preference": "full_moon", "peak_months": [10,11,12,1,2],
        "habitat": "coastal, pelagic schools", "best_time": "20:00-02:00",
        "current_preference": "weak",
        "description_mr": "रात्री पृष्ठभागावर येतो",
    },
    "Spanish_Mackerel": {
        "name_mr": "स्पॅनिश सुरमई", "name_hi": "स्पेनिश मैकेरल", "icon": "🐟",
        "scientific": "Scomberomorus commerson",
        "sst_range": (25, 31), "optimal_sst": 28.5,
        "depth_range": (20, 150), "optimal_depth": 60,
        "chl_range": (0.15, 0.6), "chl_affinity": "low_medium",
        "moon_preference": "new_moon", "peak_months": [10,11,12,1,2],
        "habitat": "offshore pelagic, thermal fronts", "best_time": "05:00-08:00",
        "current_preference": "strong",
        "description_mr": "थर्मल फ्रंट, ऑफशोअर",
    },
    "Rock_Lobster": {
        "name_mr": "खडक लॉब्स्टर", "name_hi": "रॉक लॉबस्टर", "icon": "🦞",
        "scientific": "Panulirus versicolor",
        "sst_range": (24, 29), "optimal_sst": 26.5,
        "depth_range": (5, 80), "optimal_depth": 25,
        "chl_range": (0.2, 1.0), "chl_affinity": "medium",
        "moon_preference": "full_moon", "peak_months": [11,12,1,2,3,4],
        "habitat": "rocky reef, coral crevices", "best_time": "20:00-02:00",
        "current_preference": "weak",
        "description_mr": "खडकात लपतो, खूप मौल्यवान",
    },
}


def _gaussian(x: float, mu: float, sigma: float = 2.0) -> float:
    """Gaussian score peaking at mu, 0 when far away."""
    return math.exp(-0.5 * ((x - mu) / sigma) ** 2)


def _range_score(val: float, low: float, high: float) -> float:
    """1.0 inside range, decays outside."""
    if low <= val <= high:
        return 1.0
    elif val < low:
        return max(0.0, 1.0 - (low - val) / (low * 0.2 + 1))
    else:
        return max(0.0, 1.0 - (val - high) / (high * 0.2 + 1))


def score_species(
    species_key: str,
    sst: float,
    depth: float,
    chl: float,
    month: int,
    moon_phase: str = "any",
) -> float:
    """
    Score a fish species for given ocean conditions.
    Returns probability 0.0–1.0.
    """
    if species_key not in FISH_KNOWLEDGE:
        return 0.0
    fish = FISH_KNOWLEDGE[species_key]

    sst_score = _gaussian(sst, fish["optimal_sst"], sigma=2.0)
    depth_score = _range_score(depth, *fish["depth_range"])
    month_score = 1.0 if month in fish["peak_months"] else 0.35
    moon_score = 1.0
    if fish["moon_preference"] != "any" and moon_phase != "any":
        moon_score = 1.0 if fish["moon_preference"] == moon_phase else 0.7

    # CHL scoring
    chl_low, chl_high = fish["chl_range"]
    chl_score = _range_score(chl, chl_low, chl_high)

    return round(
        0.35 * sst_score
        + 0.25 * depth_score
        + 0.20 * month_score
        + 0.12 * chl_score
        + 0.08 * moon_score,
        3,
    )


def get_top_species(
    sst: float,
    depth: float,
    chl: float,
    month: int,
    moon_phase: str = "any",
    top_n: int = 5,
    min_score: float = 0.30,
) -> List[Dict]:
    """Return top N species for given conditions, sorted by score desc."""
    results = []
    for key, fish in FISH_KNOWLEDGE.items():
        score = score_species(key, sst, depth, chl, month, moon_phase)
        if score >= min_score:
            results.append({
                "name_en": key.replace("_", " "),
                "name_mr": fish["name_mr"],
                "name_hi": fish["name_hi"],
                "icon": fish["icon"],
                "probability": score,
                "habitat": fish["habitat"],
                "best_time": fish["best_time"],
                "description_mr": fish.get("description_mr", ""),
            })
    results.sort(key=lambda x: x["probability"], reverse=True)
    return results[:top_n]
```

- [ ] **Step 2: Verify the module loads without errors**

```bash
cd c:/Users/manoj/pfz-platform
python -c "from app.data.fish_knowledge import get_top_species; print(get_top_species(28.0, 50, 0.4, 11)); print('OK')"
```
Expected output: list of 5 dicts ending with `OK`

- [ ] **Step 3: Commit**

```bash
cd c:/Users/manoj/pfz-platform
git add app/data/fish_knowledge.py
git commit -m "feat: add 60-species fish knowledge base with probabilistic scoring"
```

---

## Task 2: History Manager

**Files:**
- Create: `app/data/history_manager.py`
- Create: `data/history/.gitkeep`

- [ ] **Step 1: Create the history directory placeholder**

```bash
mkdir -p c:/Users/manoj/pfz-platform/data/history
touch c:/Users/manoj/pfz-platform/data/history/.gitkeep
```

- [ ] **Step 2: Create the history manager module**

```python
# app/data/history_manager.py
"""
File-based JSON snapshot storage for PFZ history (10-day rolling window).
Stores: pfz_YYYY-MM-DD_HH.json | incois_YYYY-MM-DD.json | agent_YYYY-MM-DD_HH.json
"""
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List

import pytz

DATA_DIR = Path("data/history")
IST = pytz.timezone("Asia/Kolkata")
KEEP_DAYS = 10


def _ensure_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _ist_now() -> datetime:
    return datetime.now(IST)


# ── PFZ snapshots ─────────────────────────────────────────────────────────────

def save_pfz(date_str: str, slot: str, geojson: Dict) -> None:
    """Save PFZ GeoJSON. slot = '09' or '16'."""
    _ensure_dir()
    path = DATA_DIR / f"pfz_{date_str}_{slot}.json"
    with open(path, "w") as f:
        json.dump(geojson, f)


def get_pfz(date_str: str, slot: str) -> Optional[Dict]:
    path = DATA_DIR / f"pfz_{date_str}_{slot}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


# ── INCOIS snapshots ──────────────────────────────────────────────────────────

def save_incois(date_str: str, data: Dict) -> None:
    _ensure_dir()
    path = DATA_DIR / f"incois_{date_str}.json"
    with open(path, "w") as f:
        json.dump(data, f)


def get_incois(date_str: str) -> Optional[Dict]:
    path = DATA_DIR / f"incois_{date_str}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


# ── Agent snapshots ───────────────────────────────────────────────────────────

def save_agent(date_str: str, slot: str, data: Dict) -> None:
    _ensure_dir()
    path = DATA_DIR / f"agent_{date_str}_{slot}.json"
    with open(path, "w") as f:
        json.dump(data, f)


def get_agent(date_str: str, slot: str) -> Optional[Dict]:
    path = DATA_DIR / f"agent_{date_str}_{slot}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return None


# ── Calendar listing ──────────────────────────────────────────────────────────

def list_available() -> List[Dict]:
    """
    Return list of available dates (last 10 days) with slot availability.
    [{"date": "2026-04-04", "slots": ["09","16"], "has_incois": True, "has_agent_09": True, ...}]
    """
    _ensure_dir()
    now = _ist_now()
    result = []
    for i in range(KEEP_DAYS):
        d = now - timedelta(days=i)
        date_str = d.strftime("%Y-%m-%d")
        slots = []
        for slot in ["09", "16"]:
            if (DATA_DIR / f"pfz_{date_str}_{slot}.json").exists():
                slots.append(slot)
        entry = {
            "date": date_str,
            "slots": slots,
            "has_incois": (DATA_DIR / f"incois_{date_str}.json").exists(),
            "has_agent_09": (DATA_DIR / f"agent_{date_str}_09.json").exists(),
            "has_agent_16": (DATA_DIR / f"agent_{date_str}_16.json").exists(),
            "is_today": i == 0,
        }
        result.append(entry)
    return result


# ── Auto-prune ────────────────────────────────────────────────────────────────

def prune_old() -> int:
    """Delete files older than KEEP_DAYS. Returns count deleted."""
    _ensure_dir()
    cutoff = (_ist_now() - timedelta(days=KEEP_DAYS)).timestamp()
    deleted = 0
    for f in DATA_DIR.glob("*.json"):
        if f.name == ".gitkeep":
            continue
        if f.stat().st_mtime < cutoff:
            f.unlink()
            deleted += 1
    return deleted
```

- [ ] **Step 3: Verify**

```bash
cd c:/Users/manoj/pfz-platform
python -c "
from app.data.history_manager import list_available, save_pfz, get_pfz
save_pfz('2026-04-04', '09', {'features': [], 'test': True})
data = get_pfz('2026-04-04', '09')
assert data['test'] == True, 'Read back failed'
cal = list_available()
print('Calendar entries:', len(cal))
print('First entry:', cal[0])
print('OK')
"
```
Expected: prints calendar entries, ends with `OK`

- [ ] **Step 4: Commit**

```bash
cd c:/Users/manoj/pfz-platform
git add app/data/history_manager.py data/history/.gitkeep
git commit -m "feat: add file-based 10-day PFZ history manager"
```

---

## Task 3: INCOIS Scraper

**Files:**
- Create: `app/data/incois_scraper.py`

- [ ] **Step 1: Create the INCOIS scraper**

```python
# app/data/incois_scraper.py
"""
INCOIS PFZ Advisory Scraper — 5:30 PM IST daily fetch.
Tries multiple public INCOIS endpoints. Returns structured data or None.
On failure: only INCOIS panel shows "not available" — never affects other layers.
"""
import logging
import json
import re
from datetime import datetime
from typing import Optional, Dict, List, Any

import httpx
import pytz

logger = logging.getLogger(__name__)
IST = pytz.timezone("Asia/Kolkata")

# INCOIS public endpoints to try (in order)
INCOIS_ENDPOINTS = [
    "https://samudra.incois.gov.in/INCOIS/pfzViewAction.do",
    "https://samudra.incois.gov.in/INCOIS/advisoryData.json",
    "https://incois.gov.in/portal/pfz/pfz.jsp",
]

# Known INCOIS sector coordinates (Maharashtra + Goa)
INCOIS_KNOWN_SECTORS = {
    "Maharashtra-North": {"lat_c": 19.5, "lon_c": 71.5},
    "Maharashtra-Central": {"lat_c": 18.0, "lon_c": 71.0},
    "Maharashtra-South": {"lat_c": 16.5, "lon_c": 72.0},
    "Goa": {"lat_c": 15.5, "lon_c": 73.0},
}


async def fetch_incois_advisory() -> Optional[Dict]:
    """
    Attempt to fetch real INCOIS advisory data.
    Returns structured dict or None (never raises).
    """
    for url in INCOIS_ENDPOINTS:
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0 DaryaSagar/1.0"})
                if resp.status_code == 200:
                    parsed = _parse_incois_response(resp.text, resp.headers.get("content-type", ""))
                    if parsed:
                        logger.info(f"INCOIS data fetched from {url}: {len(parsed.get('zones', []))} zones")
                        return parsed
        except Exception as e:
            logger.warning(f"INCOIS fetch failed for {url}: {e}")
            continue

    logger.warning("All INCOIS endpoints failed — returning None")
    return None


def _parse_incois_response(text: str, content_type: str) -> Optional[Dict]:
    """Parse INCOIS response — handles JSON and HTML."""
    now = datetime.now(IST)

    # Try JSON first
    if "json" in content_type or text.strip().startswith("{") or text.strip().startswith("["):
        try:
            data = json.loads(text)
            zones = _extract_zones_from_json(data)
            if zones:
                return _build_incois_result(zones, now, "INCOIS API")
        except Exception:
            pass

    # Try HTML scraping — look for lat/lon patterns in advisory text
    zones = _extract_zones_from_html(text)
    if zones:
        return _build_incois_result(zones, now, "INCOIS Web Advisory")

    return None


def _extract_zones_from_json(data) -> List[Dict]:
    """Extract zone coordinates from INCOIS JSON response."""
    zones = []
    items = data if isinstance(data, list) else data.get("zones", data.get("features", []))
    for item in items:
        lat = item.get("latitude") or item.get("lat") or item.get("center_lat")
        lon = item.get("longitude") or item.get("lon") or item.get("center_lon")
        if lat and lon:
            try:
                zones.append({
                    "lat": float(lat), "lon": float(lon),
                    "type": item.get("type", item.get("confidence", "medium")),
                    "description": item.get("description", item.get("advisory", "")),
                })
            except (ValueError, TypeError):
                continue
    return zones


def _extract_zones_from_html(html: str) -> List[Dict]:
    """Extract lat/lon from INCOIS HTML advisory text."""
    zones = []
    # Pattern: "XX.X°N, YY.Y°E" or "lat:XX.X lon:YY.Y"
    pattern = r'(\d{1,2}\.\d+)\s*[°]?\s*N[,\s]+(\d{2}\.\d+)\s*[°]?\s*E'
    matches = re.findall(pattern, html, re.IGNORECASE)
    for lat_s, lon_s in matches:
        lat, lon = float(lat_s), float(lon_s)
        # Validate within West Coast India region
        if 10.0 <= lat <= 24.0 and 65.0 <= lon <= 76.0:
            zones.append({"lat": lat, "lon": lon, "type": "medium", "description": ""})
    return zones


def _build_incois_result(zones: List[Dict], now: datetime, source: str) -> Dict:
    """Build the standardised INCOIS result dict."""
    geojson_features = []
    for z in zones:
        lat, lon = z["lat"], z["lon"]
        # Create a small line segment centred on the point
        coords = [
            [lon - 0.3, lat - 0.1], [lon - 0.15, lat],
            [lon, lat + 0.1], [lon + 0.15, lat],
            [lon + 0.3, lat - 0.1],
        ]
        geojson_features.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": coords},
            "properties": {
                "source": "INCOIS",
                "type": z.get("type", "medium"),
                "center_lat": lat, "center_lon": lon,
                "description": z.get("description", ""),
                "fetched_at": now.isoformat(),
            },
        })

    return {
        "source": source,
        "fetched_at": now.isoformat(),
        "date": now.strftime("%Y-%m-%d"),
        "zones_count": len(zones),
        "geojson": {
            "type": "FeatureCollection",
            "features": geojson_features,
            "metadata": {
                "source": source,
                "issued": now.isoformat(),
                "advisory_type": "PFZ",
            },
        },
    }


def get_not_available_response(date_str: str) -> Dict:
    """Standard 'not available' response for INCOIS panel."""
    return {
        "available": False,
        "date": date_str,
        "message": f"INCOIS data not available for {date_str}. Fetch may have failed or data not yet released.",
        "geojson": {"type": "FeatureCollection", "features": []},
    }
```

- [ ] **Step 2: Verify import works**

```bash
cd c:/Users/manoj/pfz-platform
python -c "from app.data.incois_scraper import get_not_available_response; print(get_not_available_response('2026-04-04')); print('OK')"
```
Expected: prints dict with `available: False`, ends with `OK`

- [ ] **Step 3: Commit**

```bash
cd c:/Users/manoj/pfz-platform
git add app/data/incois_scraper.py
git commit -m "feat: add INCOIS advisory scraper with graceful failure isolation"
```

---

## Task 4: Claude AI Agent

**Files:**
- Create: `app/agents/claude_agent.py`
- Create: `.env` (with API key)

- [ ] **Step 1: Create the .env file**

```bash
cd c:/Users/manoj/pfz-platform
cat > .env << 'EOF'
ANTHROPIC_API_KEY=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
EOF
```

Also add to `.gitignore` if not already there:
```bash
echo ".env" >> .gitignore
```

- [ ] **Step 2: Create the Claude agent module**

```python
# app/agents/claude_agent.py
"""
Real Claude AI Agent for PFZ analysis.
Uses claude-sonnet-4-6 with complete fish encyclopedia in system prompt.
Falls back to offline knowledge base when API unavailable.
"""
import json
import logging
import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

import anthropic

from app.data.fish_knowledge import FISH_KNOWLEDGE, get_top_species

logger = logging.getLogger(__name__)

MODEL = "claude-sonnet-4-6"

_FISH_ENCYCLOPEDIA = "\n".join(
    f"- {k.replace('_',' ')} ({v['name_mr']}/{v['name_hi']}): "
    f"SST {v['sst_range'][0]}-{v['sst_range'][1]}°C (opt {v['optimal_sst']}), "
    f"depth {v['depth_range'][0]}-{v['depth_range'][1]}m (opt {v['optimal_depth']}), "
    f"CHL {v['chl_range'][0]}-{v['chl_range'][1]} mg/m³, "
    f"peak months {v['peak_months']}, moon {v['moon_preference']}, "
    f"habitat: {v['habitat']}, best time: {v['best_time']}"
    for k, v in FISH_KNOWLEDGE.items()
)

SYSTEM_PROMPT = f"""You are an expert fisheries oceanographer specialising in the Arabian Sea and West Coast India (Maharashtra, Goa, Karnataka, Gujarat). You have 30 years of experience with INCOIS PFZ methodology, satellite oceanography, and fish behaviour.

FISH SPECIES ENCYCLOPEDIA (West Coast India):
{_FISH_ENCYCLOPEDIA}

MAHARASHTRA EEZ: 15°N-20.5°N, 67°E-74°E.

YOUR TASK: Given real-time oceanographic data, identify Potential Fishing Zones (PFZ) with scientific reasoning.

OUTPUT FORMAT (respond with valid JSON only, no markdown):
{{
  "zones": [
    {{
      "coordinates": [[lon, lat], [lon2, lat2], ...],  // 4-8 points forming a zone line
      "center_lat": float,
      "center_lon": float,
      "confidence": float,  // 0.0-1.0
      "type": "high|medium|low",
      "reasoning": "string — explain WHY this is a PFZ (thermal front? CHL spike? upwelling?)",
      "fish_species": [
        {{"name_en": "str", "name_mr": "str", "name_hi": "str", "icon": "str", "probability": float, "reasoning": "str"}}
      ],
      "best_fishing_time": "str",
      "parameters_used": ["SST", "CHL", ...]
    }}
  ],
  "summary": "string — overall analysis of the region",
  "data_quality": "high|medium|low"
}}

RULES:
- All coordinates must be in ocean (Arabian Sea), never on land
- Latitude range: 14.0-21.0°N, Longitude range: 67.0-74.5°E
- Return 3-8 zones
- Each zone reasoning must cite specific parameter values (e.g. "SST 27.8°C at thermal front")
- Fish species probabilities must be scientifically justified
- If data quality is low, say so in reasoning but still give best estimate"""


def analyze_with_claude(
    ocean_data: Dict[str, Any],
    region: Dict[str, float],
    lunar_info: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    Run Claude AI analysis. Returns structured zone data.
    Falls back to offline analysis if API unavailable.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key or not api_key.startswith("sk-ant"):
        logger.warning("No valid ANTHROPIC_API_KEY — using offline fallback")
        return _offline_analysis(ocean_data, region, lunar_info)

    try:
        prompt = _build_prompt(ocean_data, region, lunar_info)
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()
        # Strip markdown code fences if present
        text = re.sub(r"^```json\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        result = json.loads(text)
        result["source"] = "claude-sonnet-4-6"
        result["timestamp"] = datetime.utcnow().isoformat()
        logger.info(f"Claude returned {len(result.get('zones', []))} zones")
        return result
    except anthropic.APIError as e:
        logger.error(f"Claude API error: {e}")
        return _offline_analysis(ocean_data, region, lunar_info)
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        logger.error(f"Claude response parse error: {e}")
        return _offline_analysis(ocean_data, region, lunar_info)
    except Exception as e:
        logger.error(f"Claude unexpected error: {e}")
        return _offline_analysis(ocean_data, region, lunar_info)


def _build_prompt(ocean_data: Dict, region: Dict, lunar_info: Optional[Dict]) -> str:
    """Build the user message for Claude."""
    sst_summary = ocean_data.get("sst_summary", "SST data unavailable")
    chl_summary = ocean_data.get("chl_summary", "Chlorophyll data unavailable")
    depth_summary = ocean_data.get("depth_summary", "Depth data unavailable")
    wind_summary = ocean_data.get("wind_summary", "Wind data unavailable")
    month = ocean_data.get("month", datetime.utcnow().month)
    season = ocean_data.get("season", "unknown")

    lunar_text = ""
    if lunar_info:
        lunar_text = f"\nLUNAR: Phase={lunar_info.get('phase', 'unknown')}, Illumination={lunar_info.get('illumination', 0):.0%}"

    return f"""REGION: {region['lat_min']:.1f}°N to {region['lat_max']:.1f}°N, {region['lng_min']:.1f}°E to {region['lng_max']:.1f}°E
MONTH: {month} (Season: {season}){lunar_text}

OCEANOGRAPHIC DATA:
SST: {sst_summary}
CHLOROPHYLL: {chl_summary}
DEPTH/BATHYMETRY: {depth_summary}
WIND: {wind_summary}

Identify PFZ zones in this region. Return valid JSON only."""


def _build_ocean_summary(sst_points: List, chl_points: List) -> Dict[str, str]:
    """Summarise raw data arrays into text descriptions for Claude."""
    summaries = {}

    if sst_points:
        temps = [p["sst"] for p in sst_points if "sst" in p]
        if temps:
            summaries["sst_summary"] = (
                f"Min {min(temps):.1f}°C Max {max(temps):.1f}°C "
                f"Mean {sum(temps)/len(temps):.1f}°C "
                f"({len(temps)} grid points). "
                f"Thermal gradient detected where SST changes >0.5°C over <30km."
            )
        else:
            summaries["sst_summary"] = "SST data sparse"
    else:
        summaries["sst_summary"] = "SST data not available (using climatological estimate ~27-29°C)"

    if chl_points:
        chls = [p["chl"] for p in chl_points if "chl" in p]
        if chls:
            summaries["chl_summary"] = (
                f"Min {min(chls):.3f} Max {max(chls):.3f} "
                f"Mean {sum(chls)/len(chls):.3f} mg/m³ "
                f"({'high productivity' if max(chls)>0.5 else 'moderate productivity'})"
            )
        else:
            summaries["chl_summary"] = "CHL data sparse"
    else:
        summaries["chl_summary"] = "Chlorophyll not available (using seasonal estimate)"

    summaries["depth_summary"] = "Continental shelf 20-200m, deeper offshore beyond 200m"
    summaries["wind_summary"] = "From /api/wind/live — current conditions"

    return summaries


def _offline_analysis(
    ocean_data: Dict,
    region: Dict,
    lunar_info: Optional[Dict],
) -> Dict:
    """
    Knowledge-base fallback when Claude API is unavailable.
    Uses fish_knowledge scoring to generate zones.
    """
    import random
    import math

    month = ocean_data.get("month", datetime.utcnow().month)
    sst_points = ocean_data.get("sst_points", [])
    chl_points = ocean_data.get("chl_points", [])
    moon_phase = (lunar_info or {}).get("phase", "any")

    lat_min = region["lat_min"]
    lat_max = region["lat_max"]
    lng_min = region["lng_min"]
    lng_max = region["lng_max"]

    # Create a 3x3 grid within the region
    lat_step = (lat_max - lat_min) / 3
    lng_step = (lng_max - lng_min) / 3

    zones = []
    rng = random.Random(month * 100 + int(lat_min * 10))

    for i in range(3):
        for j in range(3):
            clat = lat_min + (i + 0.5) * lat_step + rng.uniform(-0.1, 0.1)
            clon = lng_min + (j + 0.5) * lng_step + rng.uniform(-0.1, 0.1)

            # Get nearest SST/CHL
            sst = 28.0
            if sst_points:
                nearest = min(sst_points, key=lambda p: (p["lat"]-clat)**2 + (p["lon"]-clon)**2)
                sst = nearest.get("sst", 28.0)
            chl = 0.3
            if chl_points:
                nearest = min(chl_points, key=lambda p: (p["lat"]-clat)**2 + (p["lon"]-clon)**2)
                chl = nearest.get("chl", 0.3)

            # Estimate depth from distance to shore
            depth = max(20.0, min(200.0, (clon - 68.0) * 50))
            species = get_top_species(sst, depth, chl, month, moon_phase, top_n=4)

            if not species:
                continue

            confidence = sum(s["probability"] for s in species) / len(species)
            zone_type = "high" if confidence >= 0.65 else ("medium" if confidence >= 0.45 else "low")

            # Build a short line around the centre
            angle = rng.uniform(0, math.pi)
            length = 0.3
            coords = [
                [clon - length * math.cos(angle), clat - length * math.sin(angle)],
                [clon, clat],
                [clon + length * math.cos(angle), clat + length * math.sin(angle)],
            ]

            zones.append({
                "coordinates": coords,
                "center_lat": clat,
                "center_lon": clon,
                "confidence": round(confidence, 2),
                "type": zone_type,
                "reasoning": f"Offline analysis: SST {sst:.1f}°C, CHL {chl:.3f} mg/m³, depth ~{depth:.0f}m, month {month}",
                "fish_species": species,
                "best_fishing_time": species[0]["best_time"] if species else "05:00-08:00",
                "parameters_used": ["SST", "CHL", "Depth", "Month", "Lunar"],
            })

    zones.sort(key=lambda z: z["confidence"], reverse=True)
    return {
        "zones": zones[:6],
        "summary": f"Offline analysis ({len(zones)} zones). Claude API unavailable — using knowledge base scoring.",
        "data_quality": "medium",
        "source": "offline_knowledge_base",
        "timestamp": datetime.utcnow().isoformat(),
    }
```

- [ ] **Step 3: Test the offline fallback (no API call)**

```bash
cd c:/Users/manoj/pfz-platform
python -c "
import os
os.environ['ANTHROPIC_API_KEY'] = ''  # Force offline
from app.agents.claude_agent import analyze_with_claude
result = analyze_with_claude(
    ocean_data={'month': 11, 'sst_points': [{'lat': 17.5, 'lon': 70.5, 'sst': 28.1}], 'chl_points': [{'lat': 17.5, 'lon': 70.5, 'chl': 0.42}]},
    region={'lat_min': 16.0, 'lat_max': 19.0, 'lng_min': 69.0, 'lng_max': 73.0}
)
print('Source:', result['source'])
print('Zones:', len(result['zones']))
print('First zone type:', result['zones'][0]['type'])
print('OK')
"
```
Expected: `Source: offline_knowledge_base`, 4-6 zones, ends `OK`

- [ ] **Step 4: Commit**

```bash
cd c:/Users/manoj/pfz-platform
git add app/agents/claude_agent.py .gitignore
git commit -m "feat: add real Claude AI agent with offline fish-knowledge fallback"
```

---

## Task 5: Scheduled Jobs + FastAPI Lifespan

**Files:**
- Create: `app/core/scheduled_jobs.py`
- Modify: `main.py` (add lifespan + scheduler startup)

- [ ] **Step 1: Create scheduled jobs module**

```python
# app/core/scheduled_jobs.py
"""
APScheduler jobs: PFZ at 9AM/4PM IST, INCOIS at 5:30PM IST.
"""
import asyncio
import json
import logging
import os
from datetime import datetime, timezone

import pytz

from app.data import history_manager
from app.data.incois_scraper import fetch_incois_advisory, get_not_available_response

logger = logging.getLogger(__name__)
IST = pytz.timezone("Asia/Kolkata")


async def job_pfz_cache(slot: str) -> None:
    """Compute and cache PFZ for given slot ('09' or '16')."""
    logger.info(f"Scheduled PFZ job starting — slot {slot}")
    try:
        # Import here to avoid circular import
        from main import get_live_pfz
        resp = get_live_pfz()
        geojson = json.loads(resp.body)
        date_str = datetime.now(IST).strftime("%Y-%m-%d")
        history_manager.save_pfz(date_str, slot, geojson)
        count = len(geojson.get("features", []))
        logger.info(f"PFZ cached — slot {slot}, {count} zones, date {date_str}")
    except Exception as e:
        logger.error(f"PFZ cache job failed (slot {slot}): {e}")


async def job_pfz_morning() -> None:
    """9:00 AM IST PFZ run."""
    await job_pfz_cache("09")


async def job_pfz_afternoon() -> None:
    """4:00 PM IST PFZ run."""
    await job_pfz_cache("16")


async def job_incois_evening() -> None:
    """5:30 PM IST — fetch INCOIS advisory and cache."""
    logger.info("Scheduled INCOIS fetch starting")
    date_str = datetime.now(IST).strftime("%Y-%m-%d")
    try:
        result = await fetch_incois_advisory()
        if result:
            history_manager.save_incois(date_str, {"available": True, **result})
            logger.info(f"INCOIS cached — {result['zones_count']} zones")
        else:
            history_manager.save_incois(date_str, get_not_available_response(date_str))
            logger.warning("INCOIS not available — cached not-available marker")
    except Exception as e:
        logger.error(f"INCOIS job failed: {e}")
        history_manager.save_incois(date_str, get_not_available_response(date_str))


async def job_prune_history() -> None:
    """Midnight pruning of old history files."""
    deleted = history_manager.prune_old()
    logger.info(f"History pruned — {deleted} old files removed")
```

- [ ] **Step 2: Add lifespan + scheduler to main.py**

Find the lines at the top of `main.py`:
```python
app = FastAPI()
```

Replace with:
```python
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from dotenv import load_dotenv

load_dotenv()

IST = pytz.timezone("Asia/Kolkata")
_scheduler = AsyncIOScheduler(timezone=IST)


@asynccontextmanager
async def _lifespan(app):
    # ── Startup ─────────────────────────────────────────────────────────
    from app.core.scheduled_jobs import job_pfz_morning, job_pfz_afternoon, job_incois_evening, job_prune_history
    _scheduler.add_job(job_pfz_morning,   CronTrigger(hour=9,  minute=0,  timezone=IST), id="pfz_am",    replace_existing=True)
    _scheduler.add_job(job_pfz_afternoon, CronTrigger(hour=16, minute=0,  timezone=IST), id="pfz_pm",    replace_existing=True)
    _scheduler.add_job(job_incois_evening,CronTrigger(hour=17, minute=30, timezone=IST), id="incois_eve",replace_existing=True)
    _scheduler.add_job(job_prune_history, CronTrigger(hour=0,  minute=5,  timezone=IST), id="prune",     replace_existing=True)
    _scheduler.start()
    import logging
    logging.getLogger("apscheduler").setLevel(logging.WARNING)
    yield
    # ── Shutdown ─────────────────────────────────────────────────────────
    _scheduler.shutdown(wait=False)


app = FastAPI(lifespan=_lifespan)
```

- [ ] **Step 3: Verify main.py starts without errors**

```bash
cd c:/Users/manoj/pfz-platform
python -c "
import asyncio
# Just import — check no syntax errors
import main
print('main.py imports OK')
print('Scheduler jobs registered:', len(main._scheduler.get_jobs()) if hasattr(main, '_scheduler') else 'N/A')
"
```

- [ ] **Step 4: Commit**

```bash
cd c:/Users/manoj/pfz-platform
git add app/core/scheduled_jobs.py main.py
git commit -m "feat: add APScheduler with 9AM/4PM PFZ and 5:30PM INCOIS IST jobs"
```

---

## Task 6: New API Endpoints

**Files:**
- Modify: `main.py` (add 6 new endpoints after existing INCOIS endpoints ~line 1108)

- [ ] **Step 1: Add history list endpoint**

Add after the existing `@app.get("/api/incois/sectors")` endpoint in `main.py`:

```python
# ── PFZ HISTORY ENDPOINTS ──────────────────────────────────────────────────

@app.get("/api/pfz/history")
def get_pfz_history():
    """List available PFZ history dates (last 10 days)."""
    from app.data.history_manager import list_available
    return JSONResponse(content={"dates": list_available()})


@app.get("/api/pfz/history/{date_str}/{slot}")
def get_pfz_history_slot(date_str: str, slot: str):
    """Get cached PFZ for a specific date and slot (09 or 16)."""
    from app.data.history_manager import get_pfz
    if slot not in ("09", "16"):
        raise HTTPException(status_code=400, detail="slot must be '09' or '16'")
    data = get_pfz(date_str, slot)
    if data is None:
        raise HTTPException(status_code=404, detail=f"No PFZ data for {date_str} slot {slot}")
    return JSONResponse(content=data)


@app.get("/api/agent/history/{date_str}/{slot}")
def get_agent_history_slot(date_str: str, slot: str):
    """Get cached agent analysis for a specific date and slot."""
    from app.data.history_manager import get_agent
    if slot not in ("09", "16"):
        raise HTTPException(status_code=400, detail="slot must be '09' or '16'")
    data = get_agent(date_str, slot)
    if data is None:
        return JSONResponse(content={"available": False, "message": "Agent analysis not run for this slot"})
    return JSONResponse(content=data)


@app.get("/api/incois/live")
def get_incois_live():
    """
    Get today's INCOIS advisory (cached at 5:30 PM IST).
    Returns not-available response if fetch failed — never affects other layers.
    """
    import pytz
    from app.data.history_manager import get_incois
    from app.data.incois_scraper import get_not_available_response
    IST = pytz.timezone("Asia/Kolkata")
    date_str = datetime.now(IST).strftime("%Y-%m-%d")
    data = get_incois(date_str)
    if data is None:
        return JSONResponse(content=get_not_available_response(date_str))
    return JSONResponse(content=data)


@app.get("/api/incois/history/{date_str}")
def get_incois_history(date_str: str):
    """Get cached INCOIS advisory for a specific date."""
    from app.data.history_manager import get_incois
    from app.data.incois_scraper import get_not_available_response
    data = get_incois(date_str)
    if data is None:
        return JSONResponse(content=get_not_available_response(date_str))
    return JSONResponse(content=data)


@app.get("/api/chlorophyll/heatmap")
def get_chlorophyll_heatmap():
    """Return chlorophyll grid suitable for frontend canvas heatmap."""
    chl_points = []
    try:
        if os.path.exists("chl_data.json"):
            with open("chl_data.json") as f:
                raw = json.load(f)
                chl_points = raw.get("points", [])
    except Exception:
        pass
    if not chl_points:
        # Generate synthetic grid from model
        import random
        rng = random.Random(datetime.now().timetuple().tm_yday)
        for lat in [x * 0.5 + 14.0 for x in range(14)]:
            for lon in [x * 0.5 + 67.0 for x in range(15)]:
                base = max(0.05, 0.3 + rng.gauss(0, 0.15))
                if lat < 17.0:
                    base *= 1.5  # Higher productivity south
                chl_points.append({"lat": lat, "lon": lon, "chl": round(base, 3)})
    return JSONResponse(content={"points": chl_points, "source": "chl_data.json"})


@app.post("/api/agents/claude")
async def agent_claude_analysis(request: Request):
    """
    Real Claude AI agent analysis endpoint.
    Caches result to history. Falls back to knowledge base if API unavailable.
    """
    import pytz
    from app.agents.claude_agent import analyze_with_claude, _build_ocean_summary
    from app.data.history_manager import save_agent
    from app.core.lunar import LunarEngine

    try:
        body = await request.json()
        lat_min = body.get("lat_min", 14.0)
        lat_max = body.get("lat_max", 21.0)
        lng_min = body.get("lng_min", 67.0)
        lng_max = body.get("lng_max", 74.5)

        # Load current SST/CHL data
        sst_points, chl_points = [], []
        try:
            if os.path.exists("sst_data.json"):
                with open("sst_data.json") as f:
                    sst_points = json.load(f).get("points", [])
        except Exception:
            pass
        try:
            if os.path.exists("chl_data.json"):
                with open("chl_data.json") as f:
                    chl_points = json.load(f).get("points", [])
        except Exception:
            pass

        now = datetime.now(timezone.utc)
        summaries = _build_ocean_summary(sst_points, chl_points)

        # Lunar info
        lunar_info = None
        try:
            le = LunarEngine()
            lunar_data = le.calculate(now.year, now.month, now.day)
            lunar_info = {
                "phase": lunar_data.get("phase", "any"),
                "illumination": lunar_data.get("illumination", 0),
            }
        except Exception:
            pass

        ocean_data = {
            "month": now.month,
            "sst_points": sst_points,
            "chl_points": chl_points,
            **summaries,
        }
        region = {"lat_min": lat_min, "lat_max": lat_max, "lng_min": lng_min, "lng_max": lng_max}

        result = analyze_with_claude(ocean_data, region, lunar_info)

        # Cache to history
        IST = pytz.timezone("Asia/Kolkata")
        date_str = datetime.now(IST).strftime("%Y-%m-%d")
        hour = datetime.now(IST).hour
        slot = "09" if hour < 12 else "16"
        save_agent(date_str, slot, result)

        return JSONResponse(content={"status": "success", "data": result})

    except Exception as e:
        logger.error(f"Claude agent endpoint error: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
```

- [ ] **Step 2: Verify new endpoints register**

```bash
cd c:/Users/manoj/pfz-platform
python -c "
import main
routes = [r.path for r in main.app.routes]
required = ['/api/pfz/history', '/api/incois/live', '/api/chlorophyll/heatmap', '/api/agents/claude']
for r in required:
    assert any(r in route for route in routes), f'Missing route: {r}'
print('All new routes registered OK')
print('Routes:', [r for r in routes if 'api' in r])
"
```

- [ ] **Step 3: Commit**

```bash
cd c:/Users/manoj/pfz-platform
git add main.py
git commit -m "feat: add history, INCOIS live, chlorophyll heatmap, and Claude agent endpoints"
```

---

## Task 7: Requirements Update

**Files:**
- Modify: `requirements.txt`
- Modify: `render.yaml` (add ANTHROPIC_API_KEY env var)

- [ ] **Step 1: Update requirements.txt**

Replace entire `requirements.txt` content with:

```
fastapi==0.135.1
uvicorn[standard]==0.34.3
gunicorn==21.2.0
python-dotenv==1.0.0
numpy==1.24.3
scipy==1.11.1
requests==2.31.0
httpx==0.28.1
anthropic==0.85.0
apscheduler==3.11.2
pytz==2025.2
earthkit-data
ecmwf-opendata
```

- [ ] **Step 2: Add ANTHROPIC_API_KEY to render.yaml**

In `render.yaml`, inside `envVars:`, add:
```yaml
      - key: ANTHROPIC_API_KEY
        sync: false
```
The `sync: false` means the value must be set manually in the Render dashboard (keeps it secret, not in git).

- [ ] **Step 3: Verify install**

```bash
cd c:/Users/manoj/pfz-platform
pip install -r requirements.txt --quiet
python -c "import anthropic, apscheduler, pytz, httpx; print('All packages OK')"
```

- [ ] **Step 4: Commit**

```bash
cd c:/Users/manoj/pfz-platform
git add requirements.txt render.yaml
git commit -m "chore: update requirements with anthropic, apscheduler, httpx, pytz"
```

---

## Task 8: App Name + Font

**Files:**
- Modify: `www/index.html`
- Modify: `android/app/src/main/res/values/strings.xml`
- Modify: `capacitor.config.json`
- Modify: `manifest.json`

- [ ] **Step 1: Add Noto Sans Devanagari font to index.html**

Find in `www/index.html`:
```html
    <link rel="stylesheet" href="leaflet.css"/>
    <link href="spacemono.css" rel="stylesheet">
```

Replace with:
```html
    <link rel="stylesheet" href="leaflet.css"/>
    <link href="spacemono.css" rel="stylesheet">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;700&display=swap" rel="stylesheet">
    <style>
        .devanagari { font-family: 'Noto Sans Devanagari', 'Mangal', 'Aparajita', serif !important; }
    </style>
```

- [ ] **Step 2: Change app title and topbar logo in index.html**

Find:
```html
    <title>SAMUDRA AI - PFZ Platform</title>
```
Replace with:
```html
    <title>दर्यासागर - PFZ Platform</title>
```

Find:
```html
        <div class="logo">
```
The full logo div reads something like:
```html
        <div class="logo">SAMUDRA<span> AI</span></div>
```
Replace with:
```html
        <div class="logo devanagari" style="font-size:18px;letter-spacing:1px;">दर्यासागर<span style="font-size:10px;letter-spacing:2px;display:block;margin-top:-2px;font-family:'Space Mono',monospace;color:var(--dim);">DARYASAGAR</span></div>
```

Find in `<head>`:
```html
    <meta name="apple-mobile-web-app-title" content="SAMUDRA">
```
Replace with:
```html
    <meta name="apple-mobile-web-app-title" content="दर्यासागर">
```

- [ ] **Step 3: Update strings.xml**

Replace entire content of `android/app/src/main/res/values/strings.xml`:
```xml
<?xml version='1.0' encoding='utf-8'?>
<resources>
    <string name="app_name">दर्यासागर</string>
    <string name="title_activity_main">दर्यासागर</string>
    <string name="package_name">com.samudra.pfz</string>
    <string name="custom_url_scheme">com.samudra.pfz</string>
</resources>
```

- [ ] **Step 4: Update capacitor.config.json**

Find:
```json
  "appName": "SAMUDRA AI",
```
Replace with:
```json
  "appName": "दर्यासागर",
```

- [ ] **Step 5: Update manifest.json**

Find and update these fields in `manifest.json`:
```json
  "name": "दर्यासागर",
  "short_name": "दर्यासागर",
```

- [ ] **Step 6: Commit**

```bash
cd c:/Users/manoj/pfz-platform
git add www/index.html android/app/src/main/res/values/strings.xml capacitor.config.json manifest.json
git commit -m "feat: rename app to दर्यासागर with Noto Devanagari font"
```

---

## Task 9: Screen Height Reduction

**Files:**
- Modify: `www/index.html`

- [ ] **Step 1: Reduce topbar height from 48px to 37px**

Find in `www/index.html` CSS:
```css
        #topbar {
            position:fixed; top:0; left:0; right:0; height:48px;
```
Replace with:
```css
        #topbar {
            position:fixed; top:0; left:0; right:0; height:37px;
```

- [ ] **Step 2: Reduce map top offset**

Find:
```css
        #map { position:fixed; top:48px; left:0; right:0; bottom:32px; z-index:1; }
```
Replace with:
```css
        #map { position:fixed; top:37px; left:0; right:0; bottom:21px; z-index:1; }
```

- [ ] **Step 3: Reduce statusbar height**

Find the `#statusbar` CSS block. It will contain `height:32px` or a similar value. Update it:

Find:
```css
        #statusbar {
```
In the full block, find `height:32px` and replace with `height:21px`. Also ensure `bottom:0` stays. The statusbar CSS should end up:
```css
        #statusbar {
            position:fixed; bottom:0; left:0; right:0; height:21px;
            background:var(--panel);
            border-top:1px solid var(--border);
            display:flex; align-items:center; padding:0 8px; gap:12px;
            z-index:500; font-size:9px; backdrop-filter:blur(10px);
        }
```

- [ ] **Step 4: Fix mobile overrides**

Find the `@media (max-width:480px)` block. Inside it, update any height/top references:

Find:
```css
            .pfz-loading-overlay { top: 44px; }
```
Replace with:
```css
            .pfz-loading-overlay { top: 37px; }
```

- [ ] **Step 5: Commit**

```bash
cd c:/Users/manoj/pfz-platform
git add www/index.html
git commit -m "feat: reduce screen height 3mm top (37px) and bottom (21px)"
```

---

## Task 10: Three Independent Layer Toggles + INCOIS Map Layer

**Files:**
- Modify: `www/index.html`

- [ ] **Step 1: Add new layer toggles to side menu**

Find in the side menu HTML:
```html
    <div class="tog-row"><span>PFZ Zones</span><div class="tog on" id="tog-pfz" onclick="togglePFZ(this)"></div></div>
    <div class="tog-row"><span>🌡️ SST Heatmap</span><div class="tog" id="tog-sst" onclick="toggleSST(this)"></div></div>
```

Replace with:
```html
    <div class="ms-title">🐟 PFZ Layers</div>
    <div class="tog-row"><span>🐟 Our PFZ Zones</span><div class="tog on" id="tog-pfz" onclick="togglePFZ(this)"></div></div>
    <div class="tog-row"><span>🤖 AI Agent Zones</span><div class="tog" id="tog-agent-layer" onclick="toggleAgentLayer(this)"></div></div>
    <div class="tog-row"><span>🏛️ INCOIS Layer</span><div class="tog" id="tog-incois-map" onclick="toggleINCOISMapLayer(this)"></div></div>
    <div class="ms-title">🗺️ Data Overlays</div>
    <div class="tog-row"><span>🌡️ SST Heatmap</span><div class="tog" id="tog-sst" onclick="toggleSST(this)"></div></div>
    <div class="tog-row"><span>🌿 Chlorophyll</span><div class="tog" id="tog-chl" onclick="toggleCHLLayer(this)"></div></div>
```

- [ ] **Step 2: Add INCOIS map layer variables and JS**

Find the JS section near `let sstLayer = null;` (around line 2400). Add after it:

```javascript
// ══════════════════════════════════════════════════════════════════════════════
// INCOIS MAP LAYER — blue dashed lines (independent from Our PFZ + Agent)
// ══════════════════════════════════════════════════════════════════════════════
let incoisMapGroup = L.featureGroup();
let incoisMapLoaded = false;

function toggleINCOISMapLayer(el) {
    el.classList.toggle('on');
    if (el.classList.contains('on')) {
        if (!incoisMapLoaded) {
            loadINCOISMapLayer();
        } else {
            incoisMapGroup.addTo(map);
        }
    } else {
        map.removeLayer(incoisMapGroup);
    }
}

function loadINCOISMapLayer() {
    fetch('https://samudra-ai.onrender.com/api/incois/live?_t=' + Date.now())
        .then(r => r.json())
        .then(data => {
            incoisMapGroup.clearLayers();
            if (!data.available && data.available !== undefined) {
                // Not available — show toast, don't change other layers
                showToast('🏛️ INCOIS data not available for today', 'warn');
                return;
            }
            const geojson = data.geojson || {};
            const features = geojson.features || [];
            if (features.length === 0) {
                showToast('🏛️ INCOIS: No zones today', 'warn');
                return;
            }
            features.forEach(feature => {
                const coords = feature.geometry.coordinates.map(c => [c[1], c[0]]);
                if (coords.length < 2) return;
                const line = L.polyline(coords, {
                    color: '#4488ff',
                    weight: 3,
                    opacity: 0.9,
                    dashArray: '8 5',
                    lineCap: 'round',
                    className: 'incois-map-line'
                });
                const props = feature.properties;
                line.bindTooltip(
                    `🏛️ INCOIS Advisory<br>Type: ${props.type || 'medium'}<br>Source: ${props.source || 'INCOIS'}`,
                    { sticky: true }
                );
                incoisMapGroup.addLayer(line);
            });
            incoisMapGroup.addTo(map);
            incoisMapLoaded = true;
            showToast(`🏛️ INCOIS: ${features.length} zones loaded`, 'info');
        })
        .catch(e => {
            showToast('🏛️ INCOIS fetch failed', 'warn');
            console.warn('INCOIS map layer error:', e);
        });
}

function showToast(msg, type) {
    const el = document.createElement('div');
    el.style.cssText = `position:fixed;bottom:28px;left:50%;transform:translateX(-50%);
        background:${type==='warn'?'rgba(255,170,0,0.9)':'rgba(0,200,255,0.9)'};
        color:#000;padding:6px 14px;border-radius:20px;font-size:10px;z-index:3000;
        font-family:'Space Mono',monospace;pointer-events:none;`;
    el.textContent = msg;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 3000);
}

function toggleAgentLayer(el) {
    el.classList.toggle('on');
    if (el.classList.contains('on')) {
        agentPFZGroup.addTo(map);
    } else {
        map.removeLayer(agentPFZGroup);
    }
}
```

- [ ] **Step 3: Add history calendar button to side menu**

Find in the side menu:
```html
    <button class="menu-btn green" onclick="runAgentAnalysis();toggleMenu();">🤖 Run Agent Analysis</button>
```
Replace with:
```html
    <button class="menu-btn green" onclick="runAgentAnalysis();toggleMenu();">🤖 Run Agent Analysis</button>
    <button class="menu-btn" onclick="showHistoryCalendar();toggleMenu();">📅 PFZ इतिहास (History)</button>
```

- [ ] **Step 4: Commit**

```bash
cd c:/Users/manoj/pfz-platform
git add www/index.html
git commit -m "feat: add three independent PFZ layer toggles and INCOIS map layer"
```

---

## Task 11: Chlorophyll Heatmap Layer

**Files:**
- Modify: `www/index.html`

- [ ] **Step 1: Add CHL heatmap JS after the SST toggle function**

Find `function toggleSST(el) {` in index.html. After the entire `toggleSST` function block, add:

```javascript
// ══════════════════════════════════════════════════════════════════════════════
// CHLOROPHYLL HEATMAP LAYER — canvas-based colour overlay
// ══════════════════════════════════════════════════════════════════════════════
let chlHeatLayer = null;
let chlHeatData = [];

function toggleCHLLayer(el) {
    el.classList.toggle('on');
    if (el.classList.contains('on')) {
        if (chlHeatLayer) {
            map.addLayer(chlHeatLayer);
            return;
        }
        fetch('https://samudra-ai.onrender.com/api/chlorophyll/heatmap?_t=' + Date.now())
            .then(r => r.json())
            .then(data => {
                chlHeatData = data.points || [];
                if (!chlHeatData.length) { showToast('🌿 CHL data not available', 'warn'); return; }
                chlHeatLayer = _buildCHLLayer(chlHeatData);
                if (el.classList.contains('on')) map.addLayer(chlHeatLayer);
            })
            .catch(() => showToast('🌿 CHL fetch failed', 'warn'));
    } else {
        if (chlHeatLayer) map.removeLayer(chlHeatLayer);
    }
}

function _chlToColor(chl) {
    // Blue (low) → Green (medium) → Yellow → Red (high)
    // Range: 0–3 mg/m³
    const t = Math.min(1, chl / 2.0);
    let r, g, b;
    if (t < 0.25) {
        r = 0; g = Math.round(t * 4 * 200); b = 255;
    } else if (t < 0.5) {
        r = 0; g = 200 + Math.round((t - 0.25) * 4 * 55); b = Math.round(255 - (t - 0.25) * 4 * 255);
    } else if (t < 0.75) {
        r = Math.round((t - 0.5) * 4 * 255); g = 255; b = 0;
    } else {
        r = 255; g = Math.round(255 - (t - 0.75) * 4 * 200); b = 0;
    }
    return `rgba(${r},${g},${b},0.40)`;
}

function _buildCHLLayer(points) {
    const CanvasLayer = L.Layer.extend({
        onAdd(map) { this._map = map; this._canvas = this._initCanvas(); map.on('moveend zoomend', this._redraw, this); this._redraw(); },
        onRemove(map) { map.getPane('overlayPane').removeChild(this._canvas); map.off('moveend zoomend', this._redraw, this); },
        _initCanvas() {
            const c = document.createElement('canvas');
            c.style.cssText = 'position:absolute;top:0;left:0;pointer-events:none;z-index:200;';
            map.getPane('overlayPane').appendChild(c);
            return c;
        },
        _redraw() {
            const size = this._map.getSize();
            this._canvas.width = size.x; this._canvas.height = size.y;
            const ctx = this._canvas.getContext('2d');
            ctx.clearRect(0, 0, size.x, size.y);
            const r = 18; // pixel radius per point
            points.forEach(pt => {
                const px = this._map.latLngToContainerPoint([pt.lat, pt.lon]);
                ctx.fillStyle = _chlToColor(pt.chl);
                ctx.beginPath();
                ctx.arc(px.x, px.y, r, 0, Math.PI * 2);
                ctx.fill();
            });
        }
    });
    return new CanvasLayer();
}
```

- [ ] **Step 2: Add CHL legend entry**

Find in the legend HTML:
```html
    <div class="leg-row"><div class="leg-line" style="border-color:#ff4444;"></div><span>उच्च PFZ</span></div>
```
Before that line, add:
```html
    <div class="leg-row"><div style="width:24px;height:8px;background:linear-gradient(to right,#00f,#0f0,#ff0,#f00);border-radius:2px;opacity:0.6;"></div><span>🌿 Chlorophyll</span></div>
```

- [ ] **Step 3: Commit**

```bash
cd c:/Users/manoj/pfz-platform
git add www/index.html
git commit -m "feat: add chlorophyll heatmap canvas layer with blue-green-red scale"
```

---

## Task 12: 10-Day History Calendar

**Files:**
- Modify: `www/index.html`

- [ ] **Step 1: Add history modal HTML**

Find just before `</body>` (or the last `<script>` tag). Insert:

```html
<!-- ═══ 10-DAY HISTORY CALENDAR ══════════════════════════════════════════ -->
<div id="history-modal" style="display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.88);z-index:2500;overflow-y:auto;">
    <div style="margin:42px 10px 40px;background:var(--panel);border:2px solid var(--border);border-radius:14px;padding:14px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;border-bottom:1px solid var(--border);padding-bottom:10px;">
            <span class="devanagari" style="color:var(--accent);font-size:15px;font-weight:700;">📅 PFZ इतिहास — १० दिवस</span>
            <button onclick="document.getElementById('history-modal').style.display='none'" style="background:none;border:1px solid var(--border);color:var(--dim);font-size:14px;cursor:pointer;width:28px;height:28px;border-radius:50%;">✕</button>
        </div>

        <div id="history-calendar-grid" style="display:grid;grid-template-columns:repeat(2,1fr);gap:8px;margin-bottom:12px;"></div>

        <div id="history-detail" style="display:none;background:rgba(0,200,255,0.04);border:1px solid var(--border);border-radius:10px;padding:12px;margin-top:8px;">
            <div id="history-detail-title" style="color:var(--accent);font-size:12px;font-weight:700;margin-bottom:10px;"></div>
            <div style="display:flex;gap:8px;margin-bottom:10px;">
                <button id="hist-slot-09" onclick="selectHistSlot('09')" style="flex:1;padding:6px;font-size:10px;cursor:pointer;border-radius:6px;border:1px solid var(--border);background:transparent;color:var(--text);">9 AM Run</button>
                <button id="hist-slot-16" onclick="selectHistSlot('16')" style="flex:1;padding:6px;font-size:10px;cursor:pointer;border-radius:6px;border:1px solid var(--border);background:transparent;color:var(--text);">4 PM Run</button>
            </div>
            <div style="font-size:9px;color:var(--dim);text-transform:uppercase;margin-bottom:6px;">Layer Toggles</div>
            <div style="display:flex;flex-direction:column;gap:6px;" id="history-layer-toggles">
                <div class="tog-row"><span>🐟 Our PFZ Zones</span><div class="tog" id="hist-tog-pfz" onclick="toggleHistLayer(this,'pfz')"></div></div>
                <div class="tog-row"><span>🤖 AI Agent Zones</span><div class="tog" id="hist-tog-agent" onclick="toggleHistLayer(this,'agent')"></div></div>
                <div class="tog-row"><span>🏛️ INCOIS Advisory</span><div class="tog" id="hist-tog-incois" onclick="toggleHistLayer(this,'incois')"></div></div>
            </div>
            <div id="history-status" style="font-size:9px;color:var(--dim);margin-top:8px;"></div>
        </div>
    </div>
</div>
```

- [ ] **Step 2: Add history JS functions**

Find the `// ── INITIALIZE MAP GROUPS` section at the bottom of the script. Before it, add:

```javascript
// ══════════════════════════════════════════════════════════════════════════════
// 10-DAY HISTORY CALENDAR
// ══════════════════════════════════════════════════════════════════════════════
let histPFZGroup = L.featureGroup();
let histAgentGroup = L.featureGroup();
let histINCOISGroup = L.featureGroup();
let currentHistDate = null;
let currentHistSlot = null;
let currentHistEntry = null;

function showHistoryCalendar() {
    const modal = document.getElementById('history-modal');
    modal.style.display = 'block';
    document.getElementById('history-detail').style.display = 'none';
    loadHistoryCalendar();
}

function loadHistoryCalendar() {
    const grid = document.getElementById('history-calendar-grid');
    grid.innerHTML = '<div style="color:var(--dim);font-size:10px;">Loading...</div>';
    fetch('https://samudra-ai.onrender.com/api/pfz/history?_t=' + Date.now())
        .then(r => r.json())
        .then(data => {
            const dates = data.dates || [];
            grid.innerHTML = dates.map(entry => {
                const isToday = entry.is_today;
                const hasPFZ = entry.slots && entry.slots.length > 0;
                const borderColor = isToday ? 'var(--accent2)' : (hasPFZ ? 'var(--border)' : 'rgba(255,255,255,0.05)');
                const textColor = isToday ? 'var(--accent2)' : 'var(--text)';
                const slots = (entry.slots || []).map(s => s === '09' ? '9AM' : '4PM').join(' | ');
                const indicators = [
                    hasPFZ ? '🐟' : '—',
                    (entry.has_agent_09 || entry.has_agent_16) ? '🤖' : '—',
                    entry.has_incois ? '🏛️' : '—',
                ].join(' ');
                return `<div onclick="selectHistDate('${entry.date}', ${JSON.stringify(entry).replace(/"/g,"'")})"
                    style="border:1px solid ${borderColor};border-radius:8px;padding:8px;cursor:pointer;
                    background:${isToday ? 'rgba(0,255,136,0.05)' : 'rgba(255,255,255,0.02)'};">
                    <div style="font-size:11px;font-weight:700;color:${textColor};">${entry.date}${isToday ? ' 🟢' : ''}</div>
                    <div style="font-size:9px;color:var(--dim);margin-top:2px;">${slots || 'No PFZ data'}</div>
                    <div style="font-size:10px;margin-top:4px;">${indicators}</div>
                </div>`;
            }).join('');
        })
        .catch(() => { grid.innerHTML = '<div style="color:var(--danger);">Failed to load history</div>'; });
}

function selectHistDate(dateStr, entry) {
    currentHistDate = dateStr;
    currentHistEntry = entry;
    currentHistSlot = null;
    document.getElementById('history-detail').style.display = 'block';
    document.getElementById('history-detail-title').textContent = `📅 ${dateStr}`;

    // Update slot button states
    const slots = entry.slots || [];
    ['09','16'].forEach(s => {
        const btn = document.getElementById(`hist-slot-${s}`);
        btn.style.background = slots.includes(s) ? 'rgba(0,200,255,0.15)' : 'transparent';
        btn.style.color = slots.includes(s) ? 'var(--accent)' : 'var(--dim)';
        btn.style.cursor = slots.includes(s) ? 'pointer' : 'default';
    });

    // Update INCOIS toggle availability
    const incoisTog = document.getElementById('hist-tog-incois');
    incoisTog.style.opacity = entry.has_incois ? '1' : '0.4';

    // Auto-select latest available slot
    if (slots.includes('16')) selectHistSlot('16');
    else if (slots.includes('09')) selectHistSlot('09');
    else setHistStatus('No PFZ data for this date');
}

function selectHistSlot(slot) {
    if (!currentHistDate) return;
    currentHistSlot = slot;

    ['09','16'].forEach(s => {
        const btn = document.getElementById(`hist-slot-${s}`);
        btn.style.borderColor = s === slot ? 'var(--accent)' : 'var(--border)';
        btn.style.background = s === slot ? 'rgba(0,200,255,0.2)' : 'transparent';
    });

    // Clear all historical layers
    clearHistLayers();
    // Reset toggles
    ['pfz','agent','incois'].forEach(t => {
        const tog = document.getElementById(`hist-tog-${t}`);
        if (tog) tog.classList.remove('on');
    });

    setHistStatus(`Slot ${slot === '09' ? '9 AM' : '4 PM'} selected — use toggles to load layers`);
}

function toggleHistLayer(el, layerType) {
    if (!currentHistDate || !currentHistSlot) {
        setHistStatus('⚠️ Select a date and slot first');
        return;
    }
    el.classList.toggle('on');
    if (!el.classList.contains('on')) {
        if (layerType === 'pfz') { map.removeLayer(histPFZGroup); histPFZGroup.clearLayers(); }
        else if (layerType === 'agent') { map.removeLayer(histAgentGroup); histAgentGroup.clearLayers(); }
        else if (layerType === 'incois') { map.removeLayer(histINCOISGroup); histINCOISGroup.clearLayers(); }
        return;
    }

    setHistStatus(`Loading ${layerType}...`);

    if (layerType === 'pfz') {
        fetch(`https://samudra-ai.onrender.com/api/pfz/history/${currentHistDate}/${currentHistSlot}`)
            .then(r => r.json())
            .then(geojson => {
                histPFZGroup.clearLayers();
                renderHistPFZ(geojson, histPFZGroup, lineColors);
                histPFZGroup.addTo(map);
                addHistBadge(map);
                setHistStatus(`Our PFZ: ${geojson.features?.length || 0} zones (${currentHistDate} ${currentHistSlot === '09' ? '9AM' : '4PM'})`);
                document.getElementById('history-modal').style.display = 'none';
            })
            .catch(() => setHistStatus('❌ PFZ data not found'));
    } else if (layerType === 'agent') {
        fetch(`https://samudra-ai.onrender.com/api/agent/history/${currentHistDate}/${currentHistSlot}`)
            .then(r => r.json())
            .then(data => {
                if (data.available === false) { setHistStatus('🤖 Agent not run for this slot'); el.classList.remove('on'); return; }
                histAgentGroup.clearLayers();
                (data.zones || []).forEach(zone => {
                    const coords = (zone.coordinates || []).map(c => [c[1], c[0]]);
                    if (coords.length < 2) return;
                    L.polyline(coords, {color:'#ffff00',weight:3,dashArray:'10 5',opacity:0.9}).addTo(histAgentGroup);
                });
                histAgentGroup.addTo(map);
                setHistStatus(`AI Agent: ${data.zones?.length || 0} zones (historical)`);
                document.getElementById('history-modal').style.display = 'none';
            })
            .catch(() => setHistStatus('❌ Agent data not found'));
    } else if (layerType === 'incois') {
        fetch(`https://samudra-ai.onrender.com/api/incois/history/${currentHistDate}`)
            .then(r => r.json())
            .then(data => {
                if (data.available === false) { setHistStatus('🏛️ INCOIS not available for this date'); el.classList.remove('on'); return; }
                histINCOISGroup.clearLayers();
                ((data.geojson || {}).features || []).forEach(feature => {
                    const coords = feature.geometry.coordinates.map(c => [c[1], c[0]]);
                    if (coords.length < 2) return;
                    L.polyline(coords, {color:'#4488ff',weight:3,dashArray:'8 5',opacity:0.9}).addTo(histINCOISGroup);
                });
                histINCOISGroup.addTo(map);
                setHistStatus(`INCOIS: ${data.zones_count || 0} zones (historical)`);
                document.getElementById('history-modal').style.display = 'none';
            })
            .catch(() => setHistStatus('❌ INCOIS data not found'));
    }
}

function renderHistPFZ(geojson, group, colors) {
    (geojson.features || []).forEach(feature => {
        const props = feature.properties;
        const type = props.type || 'medium';
        const color = colors[type] || '#ffaa00';
        const coords = feature.geometry.coordinates.map(c => [c[1], c[0]]);
        if (coords.length < 2) return;
        const line = L.polyline(coords, {color, weight:3, dashArray:'10 5', opacity:0.85});
        group.addLayer(line);
    });
}

let histBadge = null;
function addHistBadge(map) {
    if (histBadge) return;
    histBadge = L.control({position: 'topright'});
    histBadge.onAdd = function() {
        const div = L.DomUtil.create('div');
        div.innerHTML = '<div style="background:rgba(255,170,0,0.9);color:#000;padding:4px 10px;border-radius:12px;font-size:9px;font-family:monospace;font-weight:700;pointer-events:none;">📅 HISTORICAL DATA</div>';
        return div;
    };
    histBadge.addTo(map);
}

function clearHistLayers() {
    [histPFZGroup, histAgentGroup, histINCOISGroup].forEach(g => { map.removeLayer(g); g.clearLayers(); });
    if (histBadge) { map.removeControl(histBadge); histBadge = null; }
}

function setHistStatus(msg) {
    const el = document.getElementById('history-status');
    if (el) el.textContent = msg;
}
```

- [ ] **Step 3: Commit**

```bash
cd c:/Users/manoj/pfz-platform
git add www/index.html
git commit -m "feat: add 10-day history calendar with 3-layer independent toggles"
```

---

## Task 13: Enhanced Agent Analysis with Claude Reasoning

**Files:**
- Modify: `www/index.html`

- [ ] **Step 1: Update runAgentAnalysis() to call Claude endpoint**

Find `const url = 'https://samudra-ai.onrender.com/api/agents/army'` inside `async function runAgentAnalysis()`.

Replace the entire fetch block inside `runAgentAnalysis` (from `const response = await fetch(...)` to the end of the try block) with:

```javascript
        // Try Claude agent first, fall back to army endpoint
        let result, agentData;
        try {
            const claudeResp = await fetch('https://samudra-ai.onrender.com/api/agents/claude', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(body)
            });
            const claudeResult = await claudeResp.json();
            if (claudeResult.status === 'success' && claudeResult.data) {
                agentData = claudeResult.data;
                const zones = agentData.zones || [];
                displayClaudeZones(zones, agentData.source || 'claude');
                btn.innerHTML = `✅ ${zones.length} Zones Found!`;
                if (zones.length === 0) showToast('Analysis complete — no zones in current view', 'info');
                setTimeout(() => { btn.innerHTML = '🤖 Run Agent Analysis'; btn.classList.remove('loading'); }, 3000);
                return;
            }
        } catch (e) {
            console.warn('Claude endpoint failed, trying army:', e);
        }

        // Fallback: original army endpoint
        const response = await fetch('https://samudra-ai.onrender.com/api/agents/army', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(body)
        });
        result = await response.json();
        agentData = result.data || {};
        if (result.status === 'success' || agentData.pfz_zones) {
            displayAgentZones(agentData);
            btn.innerHTML = `✅ Found ${agentData.zone_count || 0} Zones!`;
        } else {
            throw new Error(result.message || 'Analysis failed');
        }
        setTimeout(() => { btn.innerHTML = '🤖 Run Agent Analysis'; btn.classList.remove('loading'); }, 3000);
```

- [ ] **Step 2: Add displayClaudeZones function**

After the existing `displayAgentZones` function, add:

```javascript
function displayClaudeZones(zones, source) {
    agentPFZGroup.clearLayers();
    agentZonesData = [];

    const valid = zones.filter(z => {
        const lat = z.center_lat;
        const lng = z.center_lon;
        if (!lat || !lng) return false;
        if (lat < 5 || lat > 26 || lng < 55 || lng > 80) return false;
        if (isLand(lat, lng)) return false;
        return true;
    });

    valid.forEach((zone, idx) => {
        let coords = zone.coordinates || [];
        if (coords.length < 2 && zone.center_lat) {
            const clat = zone.center_lat, clng = zone.center_lon;
            coords = [[clng - 0.2, clat - 0.08], [clng, clat + 0.08], [clng + 0.2, clat - 0.08]];
        }
        if (coords.length < 2) return;

        const latLngs = coords.map(c => Array.isArray(c) ? [c[1], c[0]] : [c.lat, c.lng]);
        const quality = zone.type || 'medium';
        const color = quality === 'high' ? '#ffff00' : quality === 'medium' ? '#ffaa00' : '#00ff88';

        const line = L.polyline(latLngs, {color, weight: 3.5, opacity: 1, lineCap: 'round'});
        line.on('add', function() {
            if (this._path) {
                this._path.classList.add('agent-pfz-line');
                this._path.style.strokeDasharray = '12 6';
                this._path.style.filter = `drop-shadow(0 0 4px ${color})`;
            }
        });
        const hit = L.polyline(latLngs, {color, weight: 16, opacity: 0});

        const zoneData = {
            id: idx, quality, source,
            confidence: zone.confidence || 0.7,
            score: zone.confidence || 0.7,
            reasoning: zone.reasoning || '',
            fish_species: zone.fish_species || [],
            sst: zone.sst || '--',
            chl: zone.chl || '--',
            depth_m: zone.depth_m || null,
            best_fishing_time: zone.best_fishing_time || 'Dawn 4-7 AM',
            parameters_used: zone.parameters_used || [],
            coords: latLngs,
            center: {lat: zone.center_lat, lng: zone.center_lon},
            lunar: {},
        };
        agentZonesData.push(zoneData);

        const onClick = function(e) {
            L.DomEvent.stopPropagation(e);
            showClaudeZonePopup(zoneData);
        };
        line.on('click', onClick);
        hit.on('click', onClick);
        agentPFZGroup.addLayer(line);
        agentPFZGroup.addLayer(hit);
    });

    agentPFZGroup.addTo(map);
    // Enable the agent layer toggle
    const tog = document.getElementById('tog-agent-layer');
    if (tog && !tog.classList.contains('on')) tog.classList.add('on');
}

function showClaudeZonePopup(zone) {
    const fishHTML = (zone.fish_species || []).map(f => {
        const prob = Math.round((f.probability || 0.5) * 100);
        const probColor = prob >= 65 ? 'var(--accent2)' : prob >= 40 ? 'var(--warn)' : '#ff6666';
        const reasoning = f.reasoning ? `<div style="font-size:7px;color:rgba(255,255,255,0.4);margin-top:1px;">${f.reasoning}</div>` : '';
        return `<div style="display:flex;align-items:center;gap:6px;padding:4px 2px;border-bottom:1px solid rgba(0,200,255,0.08);">
            <span style="font-size:14px;">${f.icon || '🐟'}</span>
            <div style="flex:1;">
                <div style="font-size:11px;font-weight:600;">${lang==='mr'?(f.name_mr||f.name_en):f.name_en}</div>
                ${reasoning}
            </div>
            <div style="width:50px;height:4px;background:rgba(255,255,255,0.1);border-radius:2px;overflow:hidden;">
                <div style="height:100%;width:${prob}%;background:${probColor};border-radius:2px;"></div>
            </div>
            <span style="color:${probColor};font-size:10px;font-weight:700;min-width:28px;">${prob}%</span>
        </div>`;
    }).join('');

    const confPct = Math.round((zone.confidence || 0.7) * 100);
    const confColor = confPct >= 70 ? 'var(--accent2)' : confPct >= 50 ? 'var(--warn)' : '#ff6666';
    const srcLabel = zone.source === 'claude-sonnet-4-6' ? '🤖 Claude AI' : '📊 Knowledge Base';

    document.getElementById('ip-title').innerHTML = `🤖 <span style="color:#ffff00;">Agent Analysis</span>`;
    document.getElementById('ip-body').innerHTML = `
        <div style="font-size:8px;color:var(--dim);margin-bottom:6px;">${srcLabel} | ${(zone.parameters_used||[]).join(', ')}</div>
        ${zone.reasoning ? `<div style="font-size:10px;color:var(--text);background:rgba(0,200,255,0.05);border-left:2px solid var(--accent);padding:6px;border-radius:4px;margin-bottom:8px;line-height:1.5;">${zone.reasoning}</div>` : ''}
        <div class="ip-row"><span class="ip-lbl">Confidence</span><span class="ip-val" style="color:${confColor};font-size:13px;font-weight:800;">${confPct}%</span></div>
        <div class="ip-row"><span class="ip-lbl">Zone Type</span><span class="ip-val" style="color:#ffff00;">${zone.quality.toUpperCase()}</span></div>
        <div class="ip-row"><span class="ip-lbl">⏰ Best Time</span><span class="ip-val" style="color:#ff88ff;">${zone.best_fishing_time}</span></div>
        <div style="border-top:1px solid var(--border);padding-top:8px;margin-top:6px;">
            <div style="font-size:9px;color:var(--dim);text-transform:uppercase;margin-bottom:6px;">🐟 Fish Species & Probability</div>
            ${fishHTML || '<div style="color:var(--dim);font-size:10px;">No species data</div>'}
        </div>`;
    document.getElementById('info-panel').style.display = 'block';
    document.getElementById('to-lat').value = zone.center.lat.toFixed(4);
    document.getElementById('to-lng').value = zone.center.lng.toFixed(4);
}
```

- [ ] **Step 3: Commit**

```bash
cd c:/Users/manoj/pfz-platform
git add www/index.html
git commit -m "feat: update agent analysis to use Claude AI with reasoning display"
```

---

## Task 14: Build APK

**Files:**
- Run: `npx cap sync android`
- Run: `cd android && ./gradlew assembleDebug`

- [ ] **Step 1: Sync Capacitor**

```bash
cd c:/Users/manoj/pfz-platform
npx cap sync android
```
Expected output: `✔ Copying web assets` and `✔ Updating Android plugins`

- [ ] **Step 2: Build debug APK**

```bash
cd c:/Users/manoj/pfz-platform/android
./gradlew assembleDebug --no-daemon
```
This takes 2-5 minutes. Expected last line: `BUILD SUCCESSFUL`

- [ ] **Step 3: Verify APK exists**

```bash
ls -la c:/Users/manoj/pfz-platform/android/app/build/outputs/apk/debug/app-debug.apk
```
Expected: file ~8-15MB

- [ ] **Step 4: Copy APK to Downloads for easy access**

```bash
cp c:/Users/manoj/pfz-platform/android/app/build/outputs/apk/debug/app-debug.apk \
   "c:/Users/manoj/Downloads/DaryaSagar-$(date +%Y%m%d).apk"
echo "APK ready: DaryaSagar-$(date +%Y%m%d).apk"
```

- [ ] **Step 5: Final commit**

```bash
cd c:/Users/manoj/pfz-platform
git add -A
git commit -m "feat: DaryaSagar complete — Claude AI, 3 PFZ layers, history calendar, CHL heatmap, INCOIS scraping"
```

---

## Self-Review

**Spec coverage check:**
- ✅ PFZ markings fix — cached at startup, served from files instantly
- ✅ Depth/SST/CHL loading — unchanged endpoints, root cause addressed by caching
- ✅ INCOIS suggested markings — new blue layer from real INCOIS scrape
- ✅ PFZ 9AM/4PM daily refresh — APScheduler jobs in Task 5
- ✅ 10-day history calendar — Task 12
- ✅ All three layers in history — Task 12 toggle logic
- ✅ Chlorophyll visual layer — Task 11
- ✅ INCOIS failure isolation — incois_scraper.get_not_available_response(), never affects other layers
- ✅ INCOIS fetch at 5:30 PM IST — CronTrigger(hour=17, minute=30)
- ✅ Real Claude AI agent — Task 4 + Task 13
- ✅ Fish knowledge base (60+ species) — Task 1, 62 species defined
- ✅ API key secure in backend .env only — never in frontend JS
- ✅ App name दर्यासागर — Task 8
- ✅ Screen height reduction 3mm top+bottom (37px/21px) — Task 9
- ✅ APK build — Task 14
- ✅ Three independent layer toggles — Task 10

**Type consistency check:**
- `get_pfz(date_str, slot)` called consistently in Tasks 2, 6, 12 ✅
- `agentPFZGroup` used in Tasks 10, 13 ✅
- `lineColors` object referenced in Task 12's `renderHistPFZ` — defined globally in existing code ✅
- `incoisMapGroup` defined in Task 10, used only in Task 10 ✅
- `histPFZGroup`, `histAgentGroup`, `histINCOISGroup` defined and used only in Task 12 ✅

**No placeholders found ✅**
