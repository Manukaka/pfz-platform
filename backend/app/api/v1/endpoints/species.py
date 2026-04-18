from fastapi import APIRouter, Query
from typing import Optional

from ....core.constants import WEST_COAST_STATES, STATE_SPECIES
from ....core.redis_client import get_redis

router = APIRouter(prefix="/species", tags=["Species"])

# Full species database with multi-lingual names and habitat data
SPECIES_DB = {
    "bangda_mackerel": {
        "id": "bangda_mackerel",
        "names": {"mr": "बांगडा", "gu": "બાંગડો", "hi": "बांगडा", "kn": "ಬಾಂಗ್ಡ", "ml": "അയല", "en": "Indian Mackerel", "kok": "बांगडो"},
        "scientific": "Rastrelliger kanagurta",
        "family": "Scombridae",
        "habitat": {"sst_range": [26, 30], "depth_range": [20, 200], "chlorophyll_min": 0.5},
        "seasonality": {"maharashtra": ["Aug-Mar"], "goa": ["Jul-Feb"], "karnataka": ["Jul-Feb"], "kerala": ["Year-round"]},
        "moon_preference": ["new_moon", "first_quarter"],
        "catch_time": ["early_morning", "dusk"],
        "sustainable_limit_kg_per_day": 200,
        "states": ["gujarat", "maharashtra", "goa", "karnataka", "kerala"],
        "typical_catch_range_kg": [40, 120],
    },
    "pomfret": {
        "id": "pomfret",
        "names": {"mr": "पापलेट", "gu": "પાપ્ ‍लेट", "hi": "पापलेट", "kn": "ಅವೋಲಿ", "ml": "ആവോലി", "en": "Pomfret", "kok": "पापलेट"},
        "scientific": "Pampus argenteus",
        "family": "Stromateidae",
        "habitat": {"sst_range": [24, 28], "depth_range": [10, 100]},
        "seasonality": {"gujarat": ["Oct-Feb"], "maharashtra": ["Sep-Mar"]},
        "sustainable_limit_kg_per_day": 80,
        "states": ["gujarat", "maharashtra"],
        "typical_catch_range_kg": [15, 50],
    },
    "bombay_duck": {
        "id": "bombay_duck",
        "names": {"mr": "बोंबील", "gu": "બોંbil", "hi": "बांबिल", "kn": "ಬೊಂಬಿಲ", "ml": "ബോംബ്", "en": "Bombay Duck", "kok": "बोंबिल"},
        "scientific": "Harpadon nehereus",
        "family": "Synodontidae",
        "habitat": {"sst_range": [26, 29], "depth_range": [5, 50], "substrate": "muddy"},
        "seasonality": {"gujarat": ["Jun-Dec"], "maharashtra": ["Jun-Nov"]},
        "sustainable_limit_kg_per_day": 150,
        "states": ["gujarat", "maharashtra"],
        "typical_catch_range_kg": [30, 80],
    },
    "sardine": {
        "id": "sardine",
        "names": {"mr": "तारली", "gu": "sardin", "hi": "सार्डीन", "kn": "ಭೂತಾಯಿ", "ml": "മത്തി", "en": "Indian Sardine", "kok": "ताएरलो"},
        "scientific": "Sardinella longiceps",
        "family": "Clupeidae",
        "habitat": {"sst_range": [27, 30], "depth_range": [5, 80], "chlorophyll_min": 0.8},
        "seasonality": {"karnataka": ["Jun-Nov"], "kerala": ["Year-round, peak Jun-Nov"]},
        "sustainable_limit_kg_per_day": 300,
        "states": ["karnataka", "kerala", "goa"],
        "typical_catch_range_kg": [50, 200],
    },
    "seer_surmai": {
        "id": "seer_surmai",
        "names": {"mr": "सुरमई", "gu": "surmai", "hi": "सुरमई", "kn": "ಈಸ್", "ml": "നെയ്‌മ‌ín", "en": "Seer Fish", "kok": "सुरमयो"},
        "scientific": "Scomberomorus commerson",
        "family": "Scombridae",
        "habitat": {"sst_range": [25, 29], "depth_range": [30, 300]},
        "seasonality": {"all": ["Year-round, peak Oct-Apr"]},
        "sustainable_limit_kg_per_day": 100,
        "states": ["gujarat", "maharashtra", "goa", "karnataka", "kerala"],
        "typical_catch_range_kg": [20, 60],
    },
    "hilsa": {
        "id": "hilsa",
        "names": {"mr": "पाल्वा", "gu": "hilsa", "hi": "हिल्सा", "kn": "ಪಾಲ್ವ", "ml": "palva", "en": "Hilsa", "kok": "पाल्वो"},
        "scientific": "Tenualosa ilisha",
        "family": "Clupeidae",
        "habitat": {"sst_range": [26, 30], "depth_range": [10, 100], "migratory": True},
        "seasonality": {"gujarat": ["Jun-Sep"], "maharashtra": ["Jun-Aug"]},
        "sustainable_limit_kg_per_day": 50,
        "states": ["gujarat", "maharashtra"],
        "typical_catch_range_kg": [20, 60],
    },
    "prawn": {
        "id": "prawn",
        "names": {"mr": "कोळंबी", "gu": "kolmbi", "hi": "झींगा", "kn": "ಸೀಗಡಿ", "ml": "ചെമ്മീൻ", "en": "Indian Prawn", "kok": "सुगटी"},
        "scientific": "Penaeus indicus",
        "family": "Penaeidae",
        "habitat": {"sst_range": [26, 30], "depth_range": [1, 50], "substrate": "estuarine"},
        "seasonality": {"all": ["Year-round, peak post-monsoon"]},
        "sustainable_limit_kg_per_day": 100,
        "states": ["gujarat", "maharashtra", "goa", "karnataka", "kerala"],
        "typical_catch_range_kg": [10, 40],
    },
    "tuna": {
        "id": "tuna",
        "names": {"mr": "चुरा", "gu": "tuna", "hi": "टूना", "kn": "ಚೂರ", "ml": "ചൂര", "en": "Yellowfin Tuna", "kok": "चुरो"},
        "scientific": "Thunnus albacares",
        "family": "Scombridae",
        "habitat": {"sst_range": [24, 30], "depth_range": [100, 500], "offshore": True},
        "seasonality": {"kerala": ["Oct-Mar"], "karnataka": ["Nov-Feb"]},
        "sustainable_limit_kg_per_day": 80,
        "states": ["kerala", "karnataka"],
        "typical_catch_range_kg": [30, 100],
    },
    "kingfish": {
        "id": "kingfish",
        "names": {"mr": "विसोन", "gu": "kingfish", "hi": "विसन", "kn": "ಅಂಜಲ", "ml": "ആഞ്ജൽ", "en": "Kingfish", "kok": "विसोन"},
        "scientific": "Scomberomorus guttatus",
        "family": "Scombridae",
        "habitat": {"sst_range": [26, 30], "depth_range": [20, 100]},
        "seasonality": {"goa": ["Oct-Mar"], "maharashtra": ["Oct-Feb"]},
        "sustainable_limit_kg_per_day": 80,
        "states": ["goa", "maharashtra", "karnataka"],
        "typical_catch_range_kg": [20, 60],
    },
}


@router.get("")
async def list_species(
    state: Optional[str] = Query(None, description="Filter by state"),
    language: str = Query("en", description="Language for names"),
    search: Optional[str] = Query(None, description="Search by name"),
):
    """List all fish species, optionally filtered by state."""
    results = list(SPECIES_DB.values())

    if state:
        results = [s for s in results if state in s.get("states", [])]

    if search:
        search_lower = search.lower()
        results = [
            s for s in results
            if search_lower in s["names"].get(language, s["names"]["en"]).lower()
            or search_lower in s["names"]["en"].lower()
            or search_lower in s["scientific"].lower()
        ]

    # Add display name in requested language
    for s in results:
        s["display_name"] = s["names"].get(language, s["names"]["en"])

    return {"species": results, "count": len(results)}


@router.get("/state/{state}/season")
async def get_seasonal_species(state: str, language: str = Query("en")):
    """Get species in season for a state right now."""
    from datetime import datetime
    month = datetime.now().month
    month_abbr = datetime.now().strftime("%b")

    all_species = [s for s in SPECIES_DB.values() if state in s.get("states", [])]

    in_season = []
    for sp in all_species:
        seasonality = sp.get("seasonality", {})
        state_season = seasonality.get(state) or seasonality.get("all", [])
        for season_str in state_season:
            if "Year-round" in season_str or month_abbr in season_str:
                in_season.append({**sp, "display_name": sp["names"].get(language, sp["names"]["en"])})
                break

    return {
        "state": state,
        "month": month,
        "in_season_species": in_season,
        "count": len(in_season),
    }


@router.get("/{species_id}")
async def get_species(species_id: str, language: str = Query("en")):
    """Get detailed info for a specific species."""
    sp = SPECIES_DB.get(species_id)
    if not sp:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Species '{species_id}' not found")
    return {**sp, "display_name": sp["names"].get(language, sp["names"]["en"])}


@router.get("/state/{state}/top")
async def get_top_species_for_state(
    state: str,
    language: str = Query("en"),
    limit: int = Query(5),
):
    """Get top predicted species for a state right now based on season + conditions."""
    from datetime import datetime
    month = datetime.now().month
    month_abbr = datetime.now().strftime("%b")

    all_species = [s for s in SPECIES_DB.values() if state in s.get("states", [])]
    scored = []
    for sp in all_species:
        score = 0.5  # base
        seasonality = sp.get("seasonality", {})
        state_season = seasonality.get(state) or seasonality.get("all", [])
        for s in state_season:
            if "Year-round" in s:
                score += 0.2
            elif month_abbr in s:
                score += 0.35
        scored.append({
            **sp,
            "display_name": sp["names"].get(language, sp["names"]["en"]),
            "season_score": round(score, 2),
        })

    scored.sort(key=lambda x: x["season_score"], reverse=True)
    return {"state": state, "top_species": scored[:limit]}
