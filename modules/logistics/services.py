import datetime
from io import BytesIO
from fpdf import FPDF

# ==========================================================
# ROBUST IMPORTS (MATCHES constants.py EXACTLY)
# ==========================================================
try:
    from modules.logistics.constants import (
        CORRIDORS,
        DIESEL_PRICE,
        RISK_MAP,
        CRIME_MAP,
        ROAD_QUALITY_FACTORS,   # ✅ Correct name
    )
except ImportError:
    # Fallback for local/relative execution
    from .constants import (
        CORRIDORS,
        DIESEL_PRICE,
        RISK_MAP,
        CRIME_MAP,
        ROAD_QUALITY_FACTORS,
    )


# ==========================================================
# 1. PHYSICS / CAPABILITY CHECK (DISPATCH)
# ==========================================================

def validate_physics_handshake(order_row, truck_reg, suitable_df):
    """
    Ensures the selected truck can safely carry the requested load.
    """
    if suitable_df is None or suitable_df.empty:
        return False

    if "max_tons" not in suitable_df.columns:
        return False

    # Safe extraction of volume
    vol = order_row.get("volume") or order_row.get("tons", 0)
    load_tons = float(vol or 0)

    if load_tons <= 0:
        return True

    row = suitable_df[suitable_df["reg_number"] == truck_reg]
    if row.empty:
        return False

    max_tons = float(row.iloc[0].get("max_tons", 0) or 0)

    return load_tons <= max_tons


# ==========================================================
# 2. ROUTE ECONOMICS ENGINE (INTELLIGENT)
# ==========================================================

def calculate_route_economics(route_name, truck_efficiency, tons=28, asset_profile=None):
    """
    Intelligent cost engine using corridor metadata, diesel index,
    payload sensitivity, congestion, and trailer suitability.
    """

    # Corridor lookup with safe fallback
    c = CORRIDORS.get(route_name, {
        "dist": 0,
        "tolls": 0,
        "risk": "Unknown",
        "road": "Good",
        "crime": "Low",
        "corridor_type": "General",
        "preferred_trailer": None,
    })

    dist = c["dist"]
    tolls = c["tolls"]

    # -----------------------------
    # 1. Road Condition + Congestion
    # -----------------------------
    road_factor = ROAD_QUALITY_FACTORS.get(c.get("road", "Good"), 1.00)

    congestion_factor = 1.00
    if c.get("corridor_type") in ["Port", "Border"]:
        congestion_factor = 1.10

    effective_distance = dist * road_factor * congestion_factor

    # -----------------------------
    # 2. Fuel Consumption
    # -----------------------------
    liters_used = (effective_distance / 100) * truck_efficiency
    fuel_cost = liters_used * DIESEL_PRICE

    # -----------------------------
    # 3. Base Ops Cost
    # -----------------------------
    base_ops_per_km = 12.0
    ops_cost = base_ops_per_km * dist

    # -----------------------------
    # 4. Risk Loading
    # -----------------------------
    risk_val = c.get("risk", "Medium")
    risk_key = risk_val.split()[0] if isinstance(risk_val, str) else "Medium"

    risk_factor = RISK_MAP.get(risk_key, 0.06)
    crime_factor = CRIME_MAP.get(c.get("crime", "Low"), 0.00)

    risk_loading = (fuel_cost + ops_cost) * (risk_factor + crime_factor)

    # -----------------------------
    # 5. Payload Sensitivity
    # -----------------------------
    payload_factor = 1.0 + (0.005 * max(0, tons - 28))

    # -----------------------------
    # 6. Trailer Suitability Penalty
    # -----------------------------
    trailer_penalty = 0
    if asset_profile:
        preferred = c.get("preferred_trailer")
        actual = asset_profile.get("trailer_type")
        if preferred and actual and preferred != actual:
            trailer_penalty = 0.03

    # -----------------------------
    # 7. Total Operational Cost
    # -----------------------------
    total_ops_cost = (fuel_cost + ops_cost + risk_loading)
    total_ops_cost *= payload_factor
    total_ops_cost *= (1 + trailer_penalty)

    # -----------------------------
    # 8. Suggested Rate (Margin)
    # -----------------------------
    suggested_rate = total_ops_cost * 1.15

    return {
        "distance_km": dist,
        "effective_distance_km": round(effective_distance, 2),
        "fuel_cost": round(fuel_cost, 2),
        "toll_cost": round(tolls, 2),
        "risk_loading": round(risk_loading, 2),
        "payload_factor": round(payload_factor, 3),
        "trailer_penalty": trailer_penalty,
        "total_ops_cost": round(total_ops_cost, 2),
        "suggested_rate": round(suggested_rate, 2),
        "risk": c.get("risk", "Unknown"),
        "road": c.get("road", "Good"),
        "crime": c.get("crime", "Low"),
        "corridor_type": c.get("corridor_type", "General"),
    }


# ==========================================================
# 3. DOCUMENTATION FACTORY (PDF)
# ==========================================================

def generate_dispatch_docs(trip_data):
    """
    Generates a Dispatch Pack PDF with safe encoding.
    """
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "SOVEREIGN LOGISTICS | TRIP AUTHORITY", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"TRIP ID: {trip_data.get('trip_id', 'N/A')}", ln=True)
    pdf.cell(0, 8, f"DATE: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)

    truck = trip_data.get("truck_reg", "Unknown")
    driver = trip_data.get("driver", "Unassigned")
    pdf.cell(0, 8, f"ASSET: {truck} ({driver})", ln=True)

    ref = trip_data.get("rfq_ref", "N/A")
    pdf.cell(0, 8, f"ROUTE / RFQ REF: {ref}", ln=True)
    pdf.ln(5)

    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "OFFICIAL WEIGHT CERTIFICATE", 1, 1, "C", True)

    pdf.set_font("Arial", "", 11)
    pdf.cell(50, 10, "TICKET NO:", 1)
    pdf.cell(140, 10, f"{trip_data.get('ticket_no', 'Pending')}", 1, 1)

    gross = trip_data.get("gross_weight")
    pdf.cell(50, 10, "GROSS MASS:", 1)
    pdf.cell(140, 10, f"{gross} kg" if gross else "Pending", 1, 1)

    tare = trip_data.get("tare_weight")
    pdf.cell(50, 10, "TARE MASS:", 1)
    pdf.cell(140, 10, f"{tare} kg" if tare else "Pending", 1, 1)

    net = trip_data.get("net_weight")
    pdf.set_font("Arial", "B", 12)
    pdf.cell(50, 12, "NET PAYLOAD:", 1)
    pdf.cell(140, 12, f"{net} kg" if net else "Pending", 1, 1)

    pdf.ln(10)
    pdf.set_font("Arial", "I", 8)
    pdf.cell(0, 10, "System Generated by Veridian Sovereign OS.", ln=True, align="C")

    # Safe encoding for Streamlit
    try:
        pdf_bytes = pdf.output(dest="S").encode("latin-1")
    except Exception:
        pdf_bytes = pdf.output(dest="S").encode("utf-8")

    return BytesIO(pdf_bytes)


# ==========================================================
# 4. FLEET PREDICTION ENGINE
# ==========================================================

def calculate_asset_availability(status):
    if status == "Idle":
        return "✅ IMMEDIATELY"
    if status == "Active":
        return "🕒 +4 Hours"
    if status == "En Route":
        return "🕒 +6 Hours"
    if status == "Delayed":
        return "⚠️ +12 Hours"
    if status == "Maintenance":
        return "❌ INDEFINITE"
    return "Unknown"
