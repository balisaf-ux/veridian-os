# modules/logistics/constants.py

DIESEL_PRICE = 24.50  # National blended wholesale estimate

# =========================================================
# OPERATIONAL MULTIPLIERS
# =========================================================

# Risk label -> numeric multiplier
RISK_MAP = {
    "Low": 0.04,
    "Medium": 0.08,
    "High": 0.12,
}

# Road condition -> cost/time inflation
# ✅ This is the correct name expected by services.py
ROAD_QUALITY_FACTORS = {
    "Good": 1.00,
    "Fair": 1.05,
    "Poor": 1.12,
}

# Crime exposure -> insurance/risk loading
CRIME_MAP = {
    "Low": 0.00,
    "Medium": 0.03,
    "High": 0.06,
}

# =========================================================
# CORRIDOR INTELLIGENCE LAYER
# =========================================================

CORRIDORS = {
    # N3 CORRIDOR (KZN <-> GAUTENG)
    "N3: Durban Port -> JHB City Deep": {
        "dist": 570, "tolls": 2850, "risk": "Medium",
        "corridor_type": "Port", "road": "Good", "crime": "Medium",
        "preferred_trailer": "Interlink",
    },
    "N3: Durban Port -> Pretoria": {
        "dist": 610, "tolls": 2950, "risk": "Medium",
        "corridor_type": "Port", "road": "Good", "crime": "Medium",
        "preferred_trailer": "Interlink",
    },
    "N3: Durban -> Harrismith": {
        "dist": 310, "tolls": 1650, "risk": "Medium",
        "corridor_type": "Transit", "road": "Good", "crime": "Medium",
        "preferred_trailer": "Interlink",
    },
    "N3: Pietermaritzburg -> JHB": {
        "dist": 520, "tolls": 2600, "risk": "Medium",
        "corridor_type": "Port", "road": "Good", "crime": "Medium",
        "preferred_trailer": "Interlink",
    },

    # N1 CORRIDOR (CAPE <-> GAUTENG <-> LIMPOPO)
    "N1: Cape Town -> JHB": {
        "dist": 1400, "tolls": 1900, "risk": "Low",
        "corridor_type": "Long Haul", "road": "Good", "crime": "Low",
        "preferred_trailer": "Tautliner",
    },
    "N1: JHB -> Polokwane": {
        "dist": 330, "tolls": 280, "risk": "Low",
        "corridor_type": "FMCG", "road": "Good", "crime": "Low",
        "preferred_trailer": "Tautliner",
    },
    "N1: JHB -> Musina (Beitbridge Border)": {
        "dist": 520, "tolls": 1450, "risk": "Medium",
        "corridor_type": "Border", "road": "Fair", "crime": "High",
        "preferred_trailer": "Flat Deck",
    },
    "N1: Bloemfontein -> JHB": {
        "dist": 400, "tolls": 600, "risk": "Low",
        "corridor_type": "Transit", "road": "Good", "crime": "Low",
        "preferred_trailer": "Tautliner",
    },

    # N2 CORRIDOR (CAPE <-> KZN <-> EASTERN CAPE)
    "N2: Cape Town -> Gqeberha": {
        "dist": 740, "tolls": 0, "risk": "Medium",
        "corridor_type": "Coastal", "road": "Fair", "crime": "Medium",
        "preferred_trailer": "Tautliner",
    },
    "N2: Gqeberha -> Durban": {
        "dist": 910, "tolls": 0, "risk": "High",
        "corridor_type": "Coastal", "road": "Poor", "crime": "High",
        "preferred_trailer": "Interlink",
    },
    "N2: Richards Bay -> Durban": {
        "dist": 170, "tolls": 0, "risk": "Low",
        "corridor_type": "Industrial", "road": "Good", "crime": "Low",
        "preferred_trailer": "Tautliner",
    },
    "N2: East London -> Durban": {
        "dist": 660, "tolls": 0, "risk": "High",
        "corridor_type": "Coastal", "road": "Poor", "crime": "High",
        "preferred_trailer": "Interlink",
    },

    # N4 CORRIDOR (MAPUTO <-> MPUMALANGA <-> GAUTENG)
    "N4: Maputo -> Witbank": {
        "dist": 380, "tolls": 1200, "risk": "High",
        "corridor_type": "Border", "road": "Fair", "crime": "High",
        "preferred_trailer": "Flat Deck",
    },
    "N4: Witbank -> Pretoria": {
        "dist": 110, "tolls": 90, "risk": "Low",
        "corridor_type": "Industrial", "road": "Good", "crime": "Low",
        "preferred_trailer": "Tautliner",
    },
    "N4: Pretoria -> Rustenburg": {
        "dist": 140, "tolls": 90, "risk": "Medium",
        "corridor_type": "Mining", "road": "Fair", "crime": "Medium",
        "preferred_trailer": "Side Tipper",
    },
    "N4: Rustenburg -> Botswana Border": {
        "dist": 210, "tolls": 0, "risk": "Low",
        "corridor_type": "Border", "road": "Good", "crime": "Low",
        "preferred_trailer": "Flat Deck",
    },
}

# =========================================================
# BACKWARDS COMPATIBILITY (CRITICAL)
# =========================================================

# Old code expecting ROAD_MAP (route list) gets CORRIDORS
ROAD_MAP = CORRIDORS

# Old code expecting ROAD_QUALITY_MAP gets ROAD_QUALITY_FACTORS
ROAD_QUALITY_MAP = ROAD_QUALITY_FACTORS
