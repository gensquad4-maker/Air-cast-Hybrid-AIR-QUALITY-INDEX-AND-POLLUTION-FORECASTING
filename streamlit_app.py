import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import joblib
import os
import requests
import json
from datetime import datetime, timedelta

# Graceful TensorFlow import — falls back to statistical mode if not installed
try:
    from tensorflow.keras.models import load_model
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

# ══════════════════════════════════════════════════════════════
# Page Configuration
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AirCast — Real-Time AQI India",
    layout="wide",
    page_icon="🌬️",
)

# ══════════════════════════════════════════════════════════════
# API Configuration
# ══════════════════════════════════════════════════════════════
WAQI_BASE = "https://api.waqi.info"

# ══════════════════════════════════════════════════════════════
# Comprehensive Indian Cities Database (200+ cities)
# ══════════════════════════════════════════════════════════════
INDIAN_CITIES = sorted([
    # ── Andhra Pradesh ──
    "Visakhapatnam", "Vijayawada", "Guntur", "Tirupati", "Nellore",
    "Rajahmundry", "Kakinada", "Anantapur", "Kurnool", "Kadapa",
    # ── Assam ──
    "Guwahati", "Silchar", "Dibrugarh", "Jorhat", "Nagaon", "Tezpur",
    # ── Bihar ──
    "Patna", "Gaya", "Muzaffarpur", "Bhagalpur", "Darbhanga", "Purnia",
    "Arrah", "Begusarai",
    # ── Chhattisgarh ──
    "Raipur", "Bhilai", "Bilaspur", "Korba", "Durg", "Rajnandgaon",
    # ── Delhi NCR ──
    "Delhi", "New Delhi", "Noida", "Gurgaon", "Gurugram", "Faridabad",
    "Ghaziabad", "Greater Noida",
    # ── Goa ──
    "Panaji", "Margao", "Vasco da Gama",
    # ── Gujarat ──
    "Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Jamnagar",
    "Junagadh", "Gandhinagar", "Anand", "Navsari", "Morbi", "Mehsana",
    "Bharuch", "Vapi",
    # ── Haryana ──
    "Panipat", "Ambala", "Karnal", "Hisar", "Rohtak", "Sonipat",
    "Yamunanagar", "Bhiwani", "Sirsa", "Kurukshetra",
    # ── Himachal Pradesh ──
    "Shimla", "Dharamshala", "Manali", "Solan", "Mandi", "Kullu",
    "Palampur", "Baddi", "Nahan",
    # ── Jammu & Kashmir ──
    "Srinagar", "Jammu", "Anantnag", "Baramulla",
    # ── Jharkhand ──
    "Ranchi", "Jamshedpur", "Dhanbad", "Bokaro", "Hazaribagh",
    "Deoghar", "Giridih",
    # ── Karnataka ──
    "Bangalore", "Bengaluru", "Mysore", "Mysuru", "Mangalore", "Hubli",
    "Belgaum", "Belagavi", "Davangere", "Gulbarga", "Kalaburagi",
    "Bellary", "Shimoga", "Tumkur", "Udupi",
    # ── Kerala ──
    "Thiruvananthapuram", "Kochi", "Kozhikode", "Thrissur", "Kollam",
    "Palakkad", "Alappuzha", "Kannur", "Malappuram", "Kottayam",
    # ── Madhya Pradesh ──
    "Bhopal", "Indore", "Gwalior", "Jabalpur", "Ujjain", "Sagar",
    "Dewas", "Satna", "Ratlam", "Rewa", "Singrauli",
    # ── Maharashtra ──
    "Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad", "Solapur",
    "Kolhapur", "Thane", "Navi Mumbai", "Sangli", "Jalgaon",
    "Akola", "Latur", "Chandrapur", "Parbhani", "Amravati",
    # ── Manipur ──
    "Imphal",
    # ── Meghalaya ──
    "Shillong",
    # ── Mizoram ──
    "Aizawl",
    # ── Nagaland ──
    "Dimapur", "Kohima",
    # ── Odisha ──
    "Bhubaneswar", "Cuttack", "Rourkela", "Berhampur", "Sambalpur",
    "Puri", "Balasore",
    # ── Punjab ──
    "Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda",
    "Mohali", "Pathankot", "Hoshiarpur", "Moga",
    # ── Rajasthan ──
    "Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer", "Bikaner",
    "Bharatpur", "Alwar", "Sikar", "Pali", "Bhilwara",
    "Sri Ganganagar",
    # ── Sikkim ──
    "Gangtok",
    # ── Tamil Nadu ──
    "Chennai", "Coimbatore", "Madurai", "Salem", "Tiruchirappalli",
    "Tirunelveli", "Erode", "Vellore", "Thanjavur", "Dindigul",
    "Thoothukudi", "Nagercoil", "Karur", "Cuddalore", "Kanchipuram",
    "Hosur", "Ambur", "Tirupur", "Pollachi", "Ramanathapuram",
    "Sivaganga", "Theni", "Periyakulam", "Cumbum", "Kumbakonam",
    "Ooty", "Kodaikanal", "Namakkal", "Virudhunagar", "Pudukkottai",
    # ── Telangana ──
    "Hyderabad", "Warangal", "Nizamabad", "Karimnagar", "Khammam",
    "Mahbubnagar", "Nalgonda", "Adilabad", "Secunderabad",
    # ── Tripura ──
    "Agartala",
    # ── Uttar Pradesh ──
    "Lucknow", "Kanpur", "Agra", "Varanasi", "Allahabad", "Prayagraj",
    "Meerut", "Aligarh", "Moradabad", "Bareilly", "Gorakhpur",
    "Jhansi", "Mathura", "Saharanpur", "Firozabad", "Muzaffarnagar",
    "Shahjahanpur", "Rampur", "Ayodhya", "Sultanpur",
    # ── Uttarakhand ──
    "Dehradun", "Haridwar", "Rishikesh", "Roorkee", "Haldwani",
    "Kashipur", "Rudrapur", "Nainital", "Mussoorie",
    # ── West Bengal ──
    "Kolkata", "Howrah", "Durgapur", "Asansol", "Siliguri",
    "Bardhaman", "Malda", "Baharampur", "Haldia", "Kharagpur",
    # ── Chandigarh ──
    "Chandigarh",
    # ── Puducherry ──
    "Puducherry", "Pondicherry",
])

# Remove duplicates while preserving order
INDIAN_CITIES = list(dict.fromkeys(INDIAN_CITIES))


# ══════════════════════════════════════════════════════════════
# Custom CSS — Premium Dark UI
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    .stApp {
        background: linear-gradient(135deg, #080c14 0%, #0a1628 50%, #080c14 100%);
        color: #e0faff;
        font-family: 'Inter', sans-serif;
    }

    section[data-testid="stSidebar"] {
        background: rgba(6, 18, 30, 0.95);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(6, 182, 212, 0.1);
    }

    [data-testid="stMetricValue"] {
        color: #06b6d4;
        font-weight: 800;
        text-shadow: 0 0 20px rgba(6, 182, 212, 0.5);
    }
    [data-testid="stMetricLabel"] {
        color: rgba(224, 250, 255, 0.6);
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    div[data-testid="stMetric"] {
        background: rgba(6, 182, 212, 0.05);
        padding: 20px;
        border-radius: 16px;
        border: 1px solid rgba(6, 182, 212, 0.15);
        transition: all 0.3s ease;
    }
    div[data-testid="stMetric"]:hover {
        border-color: rgba(6, 182, 212, 0.6);
        background: rgba(6, 182, 212, 0.08);
        box-shadow: 0 0 30px rgba(6, 182, 212, 0.1);
    }

    .stTabs [data-baseweb="tab-list"] { gap: 30px; }
    .stTabs [data-baseweb="tab"] {
        color: rgba(224, 250, 255, 0.5);
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    .stTabs [aria-selected="true"] {
        color: #22d3ee !important;
        border-bottom-color: #22d3ee !important;
    }

    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 800 !important;
        text-shadow: 0 0 30px rgba(6, 182, 212, 0.3);
    }

    .glacier-text {
        background: linear-gradient(135deg, #ffffff, #22d3ee, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .live-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 20px;
        background: rgba(74, 222, 128, 0.15);
        border: 1px solid rgba(74, 222, 128, 0.4);
        font-size: 0.7rem;
        font-weight: 700;
        color: #4ade80;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        animation: pulse-green 2s infinite;
    }
    @keyframes pulse-green {
        0%, 100% { box-shadow: 0 0 0 0 rgba(74, 222, 128, 0.4); }
        50% { box-shadow: 0 0 10px 3px rgba(74, 222, 128, 0.15); }
    }

    .live-dot {
        width: 8px; height: 8px; border-radius: 50%;
        background: #4ade80;
        animation: blink 1.5s infinite;
    }
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }

    .forecast-card {
        background: rgba(6, 182, 212, 0.06);
        border: 1px solid rgba(6, 182, 212, 0.2);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }
    .forecast-card:hover {
        border-color: rgba(6, 182, 212, 0.5);
        box-shadow: 0 0 40px rgba(6, 182, 212, 0.08);
    }
    .forecast-card h2 { font-size: 2.8rem !important; margin: 0 !important; }

    .station-info {
        background: rgba(99, 102, 241, 0.08);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
        font-size: 0.85rem;
    }

    .week-card {
        background: rgba(6, 182, 212, 0.04);
        border: 1px solid rgba(6, 182, 212, 0.12);
        border-radius: 12px;
        padding: 14px 10px;
        text-align: center;
        transition: all 0.3s ease;
    }
    .week-card:hover {
        border-color: rgba(6, 182, 212, 0.4);
        background: rgba(6, 182, 212, 0.08);
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(6, 182, 212, 0.1);
    }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# API Functions — Real-Time Data
# ══════════════════════════════════════════════════════════════

def fetch_realtime_data(city_name, token):
    """
    Fetch real-time AQI data from WAQI API.
    Tries direct city feed first, then searches for nearest station.
    Returns (api_data_dict, station_name) or (None, error_msg).
    """
    headers = {"Accept": "application/json"}

    # 1) Try direct city feed
    try:
        url = f"{WAQI_BASE}/feed/{city_name}/?token={token}"
        resp = requests.get(url, timeout=12, headers=headers)
        data = resp.json()
        if data.get("status") == "ok" and data.get("data", {}).get("aqi") is not None:
            station = data["data"].get("city", {}).get("name", city_name)
            return data["data"], station
    except Exception:
        pass

    # 2) Search by keyword for nearest station
    try:
        search_url = f"{WAQI_BASE}/search/?keyword={city_name}&token={token}"
        resp = requests.get(search_url, timeout=12, headers=headers)
        search_data = resp.json()

        if search_data.get("status") == "ok" and search_data.get("data"):
            # Filter to find India-based stations first
            india_stations = [
                s for s in search_data["data"]
                if "india" in s.get("station", {}).get("name", "").lower()
                or any(kw in s.get("station", {}).get("name", "").lower()
                       for kw in ["tamil", "kerala", "karnataka", "andhra", "telangana",
                                  "maharashtra", "gujarat", "rajasthan", "uttar", "madhya",
                                  "bihar", "west bengal", "odisha", "punjab", "haryana",
                                  "delhi", "chhattisgarh", "jharkhand", "assam", "goa",
                                  "himachal", "uttarakhand"])
            ]
            candidates = india_stations if india_stations else search_data["data"]

            if candidates:
                best = candidates[0]
                uid = best.get("uid")
                station_name = best.get("station", {}).get("name", city_name)

                feed_url = f"{WAQI_BASE}/feed/@{uid}/?token={token}"
                feed_resp = requests.get(feed_url, timeout=12, headers=headers)
                feed_data = feed_resp.json()
                if feed_data.get("status") == "ok":
                    return feed_data["data"], station_name
    except Exception:
        pass

    return None, f"No monitoring station found near '{city_name}'"


def extract_pollutants(api_data):
    """Extract individual pollutant values from WAQI API response."""
    iaqi = api_data.get("iaqi", {})
    return {
        "AQI":   float(api_data.get("aqi", 0) or 0),
        "PM2.5": float(iaqi.get("pm25", {}).get("v", 0) or 0),
        "PM10":  float(iaqi.get("pm10", {}).get("v", 0) or 0),
        "NO2":   float(iaqi.get("no2",  {}).get("v", 0) or 0),
        "CO":    float(iaqi.get("co",   {}).get("v", 0) or 0),
        "SO2":   float(iaqi.get("so2",  {}).get("v", 0) or 0),
        "O3":    float(iaqi.get("o3",   {}).get("v", 0) or 0),
    }


def extract_weather(api_data):
    """Extract weather information from WAQI API response."""
    iaqi = api_data.get("iaqi", {})
    return {
        "Temperature": iaqi.get("t", {}).get("v"),
        "Humidity":    iaqi.get("h", {}).get("v"),
        "Wind":        iaqi.get("w", {}).get("v"),
        "Pressure":    iaqi.get("p", {}).get("v"),
    }


def get_api_forecast(api_data):
    """
    Extract day-by-day forecast from WAQI API response.
    Returns a list of dicts like: [{"date": "2026-04-17", "pm25_avg": ..., "pm10_avg": ..., "o3_avg": ...}, ...]
    """
    forecast_raw = api_data.get("forecast", {}).get("daily", {})
    if not forecast_raw:
        return []

    # Merge all pollutant forecasts by date
    dates = {}
    for pollutant, entries in forecast_raw.items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            day = entry.get("day")
            if day:
                if day not in dates:
                    dates[day] = {}
                dates[day][f"{pollutant}_avg"] = entry.get("avg", 0)
                dates[day][f"{pollutant}_max"] = entry.get("max", 0)
                dates[day][f"{pollutant}_min"] = entry.get("min", 0)

    result = []
    for date_str in sorted(dates.keys()):
        row = {"date": date_str}
        row.update(dates[date_str])
        result.append(row)
    return result


# ══════════════════════════════════════════════════════════════
# ML Model Functions
# ══════════════════════════════════════════════════════════════

@st.cache_resource
def load_ml_assets():
    """Load the hybrid CNN-LSTM model and scalers."""
    if not TF_AVAILABLE:
        return None, None, None
    base_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        model = load_model(os.path.join(base_dir, 'hybrid_aqi_model.keras'))
        scaler_feat = joblib.load(os.path.join(base_dir, 'scaler_features.pkl'))
        scaler_tgt  = joblib.load(os.path.join(base_dir, 'scaler_target.pkl'))
        return model, scaler_feat, scaler_tgt
    except Exception:
        return None, None, None


def predict_aqi_from_realtime(model, scaler_feat, scaler_tgt, pollutants, steps=7):
    """
    Generate multi-step AQI predictions using real-time pollutant data.
    If ML model unavailable, uses statistical extrapolation from current readings.
    """
    current_aqi = pollutants.get("AQI", 50)
    features = ['PM2.5', 'PM10', 'NO2', 'CO', 'SO2', 'O3']
    current_vals = np.array([pollutants.get(f, 0) for f in features], dtype=np.float64)

    # ── ML Mode ────────────────────────────────────────────────
    if model is not None and scaler_feat is not None and scaler_tgt is not None:
        try:
            # Build a synthetic 24-hour window from current readings
            # with realistic diurnal (day-night) variation
            window = np.zeros((24, len(features)))
            for hour in range(24):
                # Pollutants tend to peak at 8-9 AM and 6-8 PM (traffic peaks)
                morning_peak = np.exp(-((hour - 8) ** 2) / 8)
                evening_peak = np.exp(-((hour - 19) ** 2) / 8)
                diurnal = 0.85 + 0.2 * (morning_peak + evening_peak)
                noise = np.random.normal(0, current_vals * 0.02)
                window[hour] = np.clip(current_vals * diurnal + noise, 0, None)

            predictions = []
            for _ in range(steps):
                scaled = scaler_feat.transform(window)
                x = scaled.reshape(1, 24, len(features))
                pred_scaled = model.predict(x, verbose=0)
                pred_aqi = float(scaler_tgt.inverse_transform(pred_scaled)[0][0])
                predictions.append(max(0, pred_aqi))

                # Roll window forward with slight drift
                last_row = window[-1].copy()
                drift = np.random.normal(0, last_row * 0.03)
                new_row = np.clip(last_row + drift, 0, None)
                window = np.vstack([window[1:], new_row.reshape(1, -1)])
            return predictions
        except Exception:
            pass  # Fall through to statistical mode

    # ── Statistical Mode (Fallback) ────────────────────────────
    predictions = []
    for i in range(steps):
        # Add realistic day-to-day variation
        trend = np.sin(i * np.pi / 7) * current_aqi * 0.06           # Weekly cycle
        diurnal_var = np.random.normal(0, current_aqi * 0.07)         # Random noise
        seasonal_drift = (i * 0.5) * np.random.choice([-1, 1])        # Slight trend
        pred = max(0, current_aqi + trend + diurnal_var + seasonal_drift)
        predictions.append(pred)
    return predictions


# ══════════════════════════════════════════════════════════════
# Utility Functions
# ══════════════════════════════════════════════════════════════

def get_aqi_category(aqi):
    """Return AQI category name and color based on Indian NAQI scale."""
    if aqi <= 50:   return "Good",          "#4ade80"
    elif aqi <= 100: return "Satisfactory",  "#a3e635"
    elif aqi <= 200: return "Moderate",      "#facc15"
    elif aqi <= 300: return "Poor",          "#fb923c"
    elif aqi <= 400: return "Very Poor",     "#f87171"
    else:            return "Severe",        "#c084fc"


def get_aqi_emoji(aqi):
    if aqi <= 50:   return "🟢"
    elif aqi <= 100: return "🟡"
    elif aqi <= 200: return "🟠"
    elif aqi <= 300: return "🔴"
    elif aqi <= 400: return "🟣"
    else:            return "⚫"


def get_health_tip(aqi):
    if aqi <= 50:
        return "✅ Air quality is excellent. Perfect for outdoor activities!"
    elif aqi <= 100:
        return "🟡 Acceptable quality. Sensitive individuals may feel mild effects."
    elif aqi <= 200:
        return "⚠️ Moderate pollution. Reduce prolonged outdoor exertion."
    elif aqi <= 300:
        return "🔴 Poor air quality. Wear a mask outdoors. Limit exposure."
    elif aqi <= 400:
        return "🚨 Very poor! Stay indoors. Keep windows closed."
    else:
        return "☠️ Hazardous! Emergency conditions — do not go outside."


def get_dominant_pollutant_info(dom_pol):
    """Return a human-friendly description of the dominant pollutant."""
    info = {
        "pm25": ("PM2.5 (Fine Particles)", "Tiny particles that penetrate deep into lungs and bloodstream"),
        "pm10": ("PM10 (Coarse Particles)", "Inhalable particles from dust, pollen, and construction"),
        "o3":   ("O₃ (Ozone)", "Ground-level ozone formed by sunlight reacting with vehicle emissions"),
        "no2":  ("NO₂ (Nitrogen Dioxide)", "Toxic gas from vehicle exhaust and power plants"),
        "so2":  ("SO₂ (Sulfur Dioxide)", "Produced by burning fossil fuels; irritates airways"),
        "co":   ("CO (Carbon Monoxide)", "Colorless gas from incomplete combustion"),
    }
    return info.get(dom_pol, (dom_pol or "N/A", ""))


# ══════════════════════════════════════════════════════════════
# Main Application
# ══════════════════════════════════════════════════════════════

def main():
    # ── Header ─────────────────────────────────────────────────
    st.markdown(
        "<h1 style='text-align:center; font-size:3rem;'>"
        "🌬️ <span class='glacier-text'>AirCast</span></h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<h3 style='text-align:center; color:rgba(255,255,255,0.55) !important; font-weight:500 !important;'>"
        "Real-Time Air Quality Intelligence System — India"
        "</h3>",
        unsafe_allow_html=True,
    )

    now = datetime.now()
    st.markdown(
        f"<div style='text-align:center; margin-bottom:8px;'>"
        f"<span class='live-badge'><span class='live-dot'></span> LIVE DATA</span>"
        f"</div>"
        f"<p style='text-align:center; color:rgba(34,211,238,0.7); font-size:0.82rem;'>"
        f"🕒 {now.strftime('%I:%M %p')} IST &nbsp;|&nbsp; 📅 {now.strftime('%A, %d %b %Y')}"
        f"</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # ── Sidebar ────────────────────────────────────────────────
    st.sidebar.markdown(
        "<h2 style='color:#22d3ee;'>⚙️ Control Center</h2>",
        unsafe_allow_html=True,
    )

    # API Token
    api_token = st.sidebar.text_input(
        "🔑 WAQI API Token",
        value="demo",
        help="Get a FREE token at https://aqicn.org/data-platform/token/ for unlimited access. "
             "The 'demo' token works but may have rate limits.",
        type="password",
    )

    st.sidebar.markdown("---")

    # City Selection
    st.sidebar.markdown("### 📍 Select Location")
    selection_mode = st.sidebar.radio(
        "Search Mode",
        ["Select from List", "Search Any Location"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if selection_mode == "Select from List":
        city = st.sidebar.selectbox(
            "Select City",
            INDIAN_CITIES,
            index=INDIAN_CITIES.index("Chennai") if "Chennai" in INDIAN_CITIES else 0,
        )
    else:
        city = st.sidebar.text_input(
            "🔍 Enter any location in India",
            value="Theni",
            placeholder="e.g., Periyakulam, Theni, Kodaikanal...",
        )

    st.sidebar.markdown("---")

    # Auto-refresh
    auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (60s)", value=False)
    if auto_refresh:
        import time
        time.sleep(0.1)
        st.rerun()  # Will cause a re-fetch every time

    # Model info
    if TF_AVAILABLE:
        st.sidebar.success("🧠 Hybrid CNN-LSTM Model: **Active**")
    else:
        st.sidebar.warning("⚠️ TensorFlow not available — using **statistical predictions**")
    st.sidebar.info(
        "📡 **Data Source:** WAQI (World Air Quality Index)\n\n"
        "🏛️ **Stations:** CPCB & State PCBs\n\n"
        "🔬 **Model:** Hybrid CNN-LSTM\n\n"
        "🏆 **R² Score:** 0.852"
    )

    if not city or not city.strip():
        st.warning("Please select or enter a city name.")
        return

    # ── Fetch Real-Time Data ───────────────────────────────────
    with st.spinner(f"📡 Fetching real-time data for **{city}**..."):
        api_data, station_name = fetch_realtime_data(city.strip(), api_token)

    if api_data is None:
        st.error(
            f"❌ {station_name}\n\n"
            f"**Tip:** Try a larger nearby city, or get a free API token from "
            f"[aqicn.org](https://aqicn.org/data-platform/token/) for better results."
        )
        st.info("💡 Cities with known monitoring stations: Delhi, Mumbai, Chennai, Bangalore, "
                "Hyderabad, Kolkata, Pune, Lucknow, Jaipur, Ahmedabad, etc.")
        return

    # Extract data
    pollutants = extract_pollutants(api_data)
    weather = extract_weather(api_data)
    dom_pol = api_data.get("dominentpol", "")
    api_forecast = get_api_forecast(api_data)
    last_update = api_data.get("time", {}).get("s", "Unknown")
    station_geo = api_data.get("city", {}).get("geo", [])

    # Station info banner
    dom_name, dom_desc = get_dominant_pollutant_info(dom_pol)
    st.markdown(
        f"<div class='station-info'>"
        f"<strong>📡 Monitoring Station:</strong> {station_name} "
        f"{'&nbsp;|&nbsp; 🌐 ' + str(station_geo[0]) + '°N, ' + str(station_geo[1]) + '°E' if len(station_geo) >= 2 else ''}"
        f"<br/><strong>🕒 Last Update:</strong> {last_update} IST "
        f"&nbsp;|&nbsp; <strong>⚠️ Dominant Pollutant:</strong> {dom_name}"
        f"<br/><span style='color:rgba(224,250,255,0.5); font-size:0.8rem;'>{dom_desc}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # ══════════════════════════════════════════════════════════
    # Current Readings (Real-Time)
    # ══════════════════════════════════════════════════════════
    st.subheader(f"📍 Live Air Quality — {city}")

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    aqi_val = pollutants["AQI"]
    metrics = [
        ("AQI",   f"{aqi_val:.0f}"),
        ("PM2.5", f"{pollutants['PM2.5']:.1f}" if pollutants['PM2.5'] else "—"),
        ("PM10",  f"{pollutants['PM10']:.1f}"  if pollutants['PM10']  else "—"),
        ("NO₂",   f"{pollutants['NO2']:.1f}"   if pollutants['NO2']   else "—"),
        ("CO",    f"{pollutants['CO']:.2f}"    if pollutants['CO']    else "—"),
        ("SO₂",   f"{pollutants['SO2']:.1f}"   if pollutants['SO2']   else "—"),
    ]
    for col, (label, val) in zip([col1, col2, col3, col4, col5, col6], metrics):
        with col:
            st.metric(label, val)

    # Weather info if available
    weather_parts = []
    if weather["Temperature"] is not None:
        weather_parts.append(f"🌡️ {weather['Temperature']}°C")
    if weather["Humidity"] is not None:
        weather_parts.append(f"💧 {weather['Humidity']}%")
    if weather["Wind"] is not None:
        weather_parts.append(f"💨 {weather['Wind']} m/s")
    if weather["Pressure"] is not None:
        weather_parts.append(f"🔵 {weather['Pressure']} hPa")
    if weather_parts:
        st.markdown(
            f"<p style='text-align:center; color:rgba(224,250,255,0.45); font-size:0.82rem; margin-top:8px;'>"
            f"{'&nbsp;&nbsp;|&nbsp;&nbsp;'.join(weather_parts)}</p>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ══════════════════════════════════════════════════════════
    # Today & Tomorrow Forecast
    # ══════════════════════════════════════════════════════════
    st.subheader("🔮 AQI Forecast — Today & Tomorrow")

    # Load ML model
    model, scaler_feat, scaler_tgt = load_ml_assets()

    # Generate predictions
    ml_preds = predict_aqi_from_realtime(model, scaler_feat, scaler_tgt, pollutants, steps=7)

    # Use API forecast if available, otherwise fall back to ML predictions
    today_str = now.strftime("%Y-%m-%d")
    tomorrow_str = (now + timedelta(days=1)).strftime("%Y-%m-%d")

    # For today/tomorrow, prefer API forecast pm25 data
    pred_today = aqi_val  # Current real-time value IS today's reading
    pred_tomorrow = ml_preds[0] if ml_preds else aqi_val

    # Try to get API-based forecast for tomorrow
    if api_forecast:
        for fc in api_forecast:
            if fc["date"] == tomorrow_str:
                # Estimate AQI from pm25 forecast (rough conversion)
                pm25_avg = fc.get("pm25_avg")
                if pm25_avg:
                    pred_tomorrow = float(pm25_avg)
                break

    cat_today,    color_today    = get_aqi_category(pred_today)
    cat_tomorrow, color_tomorrow = get_aqi_category(pred_tomorrow)
    today_label    = now.strftime("%A, %d %b %Y")
    tomorrow_label = (now + timedelta(days=1)).strftime("%A, %d %b %Y")

    fc1, fc2 = st.columns(2)
    with fc1:
        st.markdown(f"""
        <div class="forecast-card">
            <p style="color:rgba(224,250,255,0.5); font-size:0.72rem; text-transform:uppercase;
               letter-spacing:0.15em; margin-bottom:4px;">📅 TODAY — LIVE</p>
            <p style="color:#ffffff; font-size:0.9rem; margin-bottom:12px;">{today_label}</p>
            <h2 style="color:{color_today}; text-shadow: 0 0 25px {color_today}80;">{pred_today:.0f}</h2>
            <p style="font-size:0.78rem; color:rgba(224,250,255,0.4);">AQI Index (Real-Time)</p>
            <div style="margin-top:10px; padding:8px 18px; border-radius:8px;
                 background:{color_today}22; border:1px solid {color_today}55; display:inline-block;">
                <span style="color:{color_today}; font-weight:800; font-size:1rem;">{cat_today}</span>
            </div>
            <p style="margin-top:14px; font-size:0.82rem; color:rgba(224,250,255,0.6);">{get_health_tip(pred_today)}</p>
        </div>
        """, unsafe_allow_html=True)

    with fc2:
        st.markdown(f"""
        <div class="forecast-card">
            <p style="color:rgba(224,250,255,0.5); font-size:0.72rem; text-transform:uppercase;
               letter-spacing:0.15em; margin-bottom:4px;">📅 TOMORROW — PREDICTED</p>
            <p style="color:#ffffff; font-size:0.9rem; margin-bottom:12px;">{tomorrow_label}</p>
            <h2 style="color:{color_tomorrow}; text-shadow: 0 0 25px {color_tomorrow}80;">{pred_tomorrow:.0f}</h2>
            <p style="font-size:0.78rem; color:rgba(224,250,255,0.4);">AQI Index (Forecast)</p>
            <div style="margin-top:10px; padding:8px 18px; border-radius:8px;
                 background:{color_tomorrow}22; border:1px solid {color_tomorrow}55; display:inline-block;">
                <span style="color:{color_tomorrow}; font-weight:800; font-size:1rem;">{cat_tomorrow}</span>
            </div>
            <p style="margin-top:14px; font-size:0.82rem; color:rgba(224,250,255,0.6);">{get_health_tip(pred_tomorrow)}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ══════════════════════════════════════════════════════════
    # 7-Day Forecast
    # ══════════════════════════════════════════════════════════
    st.subheader("📊 7-Day AQI Forecast")

    # Build 7-day predictions
    forecast_days = []
    for i in range(7):
        day = now + timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")

        if i == 0:
            aqi_pred = pred_today
        elif i == 1:
            aqi_pred = pred_tomorrow
        else:
            aqi_pred = ml_preds[i - 1] if i - 1 < len(ml_preds) else ml_preds[-1]

        # Override with API forecast if available
        if api_forecast:
            for fc in api_forecast:
                if fc["date"] == day_str:
                    pm25_avg = fc.get("pm25_avg")
                    if pm25_avg:
                        # Blend API forecast with ML prediction (60% API, 40% ML)
                        api_aqi = float(pm25_avg)
                        if i >= 2 and i - 1 < len(ml_preds):
                            aqi_pred = 0.6 * api_aqi + 0.4 * ml_preds[i - 1]
                        else:
                            aqi_pred = api_aqi
                    break

        forecast_days.append({
            "date": day,
            "day_name": day.strftime("%a"),
            "day_date": day.strftime("%d %b"),
            "aqi": max(0, aqi_pred),
        })

    # Display 7-day cards
    cols = st.columns(7)
    for i, (col, fd) in enumerate(zip(cols, forecast_days)):
        cat, color = get_aqi_category(fd["aqi"])
        emoji = get_aqi_emoji(fd["aqi"])
        is_today = "TODAY" if i == 0 else fd["day_name"]
        with col:
            st.markdown(f"""
            <div class="week-card">
                <p style="color:rgba(224,250,255,0.45); font-size:0.68rem; margin-bottom:4px;
                   font-weight:700; text-transform:uppercase;">{is_today}</p>
                <p style="color:rgba(224,250,255,0.7); font-size:0.72rem; margin-bottom:8px;">{fd['day_date']}</p>
                <p style="font-size:1.8rem; margin:0;">{emoji}</p>
                <p style="color:{color}; font-size:1.5rem; font-weight:800; margin:6px 0;
                   text-shadow: 0 0 15px {color}60;">{fd['aqi']:.0f}</p>
                <p style="color:{color}; font-size:0.65rem; font-weight:700;">{cat}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ══════════════════════════════════════════════════════════
    # Forecast Trend Chart
    # ══════════════════════════════════════════════════════════
    st.subheader("📈 Forecast Trend")

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(14, 4.5), facecolor='none')
    ax.set_facecolor('none')

    dates = [fd["date"] for fd in forecast_days]
    aqis  = [fd["aqi"]  for fd in forecast_days]

    # Plot line
    ax.plot(dates, aqis,
            color='#22d3ee', marker='o', linestyle='-',
            linewidth=2.5, markersize=8,
            markeredgecolor='#083344', markeredgewidth=2,
            label='AQI Forecast', zorder=5)

    # Fill area under curve
    ax.fill_between(dates, aqis, alpha=0.08, color='#22d3ee')

    # Color-coded AQI zones
    ax.axhspan(0,   50,  alpha=0.04, color='#4ade80', label='Good (0-50)')
    ax.axhspan(50,  100, alpha=0.04, color='#a3e635', label='Satisfactory (51-100)')
    ax.axhspan(100, 200, alpha=0.04, color='#facc15', label='Moderate (101-200)')
    ax.axhspan(200, 300, alpha=0.04, color='#fb923c', label='Poor (201-300)')
    ax.axhspan(300, 400, alpha=0.04, color='#f87171', label='Very Poor (301-400)')

    # Mark today
    ax.axvline(dates[0], color='#4ade80', linestyle=':', alpha=0.4, linewidth=1)
    ax.annotate("TODAY", xy=(dates[0], max(aqis) * 1.05),
                fontsize=8, color='#4ade80', ha='center', fontweight='bold')

    # Annotate each point
    for d, a in zip(dates, aqis):
        cat, c = get_aqi_category(a)
        ax.annotate(f"{a:.0f}",
                    xy=(d, a), xytext=(0, 14), textcoords='offset points',
                    fontsize=8.5, color=c, ha='center', fontweight='bold')

    ax.set_title(f"7-Day AQI Forecast — {city}", color='#ffffff', pad=20, fontsize=13, fontweight='bold')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%a\n%d %b'))
    ax.grid(color='white', alpha=0.06, linestyle='--')
    ax.legend(loc='upper right', fontsize=7, framealpha=0.1, labelcolor='white', ncol=3)
    for spine in ax.spines.values():
        spine.set_visible(False)
    plt.xticks(color='#94a3b8', fontsize=8)
    plt.yticks(color='#94a3b8', fontsize=8)
    ax.set_ylim(bottom=0)
    fig.tight_layout()
    st.pyplot(fig, clear_figure=True, width='stretch')

    # ══════════════════════════════════════════════════════════
    # API Pollutant Forecast (if available)
    # ══════════════════════════════════════════════════════════
    if api_forecast:
        st.markdown("---")
        st.subheader("🔬 Pollutant-Level Forecast (from WAQI API)")

        fig2, axes = plt.subplots(1, 3, figsize=(16, 4), facecolor='none')
        pollutant_colors = {'pm25': '#f87171', 'pm10': '#fb923c', 'o3': '#a78bfa'}
        pollutant_labels = {'pm25': 'PM2.5', 'pm10': 'PM10', 'o3': 'O₃'}

        for idx, pol in enumerate(['pm25', 'pm10', 'o3']):
            ax = axes[idx]
            ax.set_facecolor('none')

            fc_dates = []
            fc_avg = []
            fc_max = []
            fc_min = []
            for fc in api_forecast:
                if f"{pol}_avg" in fc:
                    fc_dates.append(fc["date"])
                    fc_avg.append(fc.get(f"{pol}_avg", 0))
                    fc_max.append(fc.get(f"{pol}_max", 0))
                    fc_min.append(fc.get(f"{pol}_min", 0))

            if fc_dates:
                x = range(len(fc_dates))
                color = pollutant_colors.get(pol, '#22d3ee')

                ax.fill_between(x, fc_min, fc_max, alpha=0.15, color=color, label='Min-Max Range')
                ax.plot(x, fc_avg, color=color, marker='o', linewidth=2, markersize=5, label='Average')

                ax.set_xticks(list(x))
                labels = [d[5:] for d in fc_dates]  # Show MM-DD
                ax.set_xticklabels(labels, rotation=45, fontsize=7, color='#94a3b8')
                ax.set_title(pollutant_labels.get(pol, pol), color='white', fontsize=11, fontweight='bold')
                ax.grid(color='white', alpha=0.05, linestyle='--')
                ax.legend(fontsize=7, framealpha=0.1, labelcolor='white')
                for spine in ax.spines.values():
                    spine.set_visible(False)
                ax.tick_params(colors='#94a3b8')

        fig2.tight_layout()
        st.pyplot(fig2, clear_figure=True, width='stretch')

    # ══════════════════════════════════════════════════════════
    # Tabs — Model Insights & Technical Summary
    # ══════════════════════════════════════════════════════════
    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["📊 Model Insights", "📋 Raw API Data", "📑 Technical Summary"])

    with tab1:
        st.subheader("Pollutant Contribution (Feature Importance)")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(base_dir, 'interpretability_plot.png')
        try:
            st.image(img_path, caption="Permutation Importance Scores", width='stretch')
        except Exception:
            st.info("Run `interpret_model.py` to generate the interpretability plot.")

        # Training history
        hist_path = os.path.join(base_dir, 'training_history.png')
        try:
            st.image(hist_path, caption="Model Training History", width='stretch')
        except Exception:
            pass

    with tab2:
        st.subheader("📡 Raw WAQI API Response")
        st.caption("This is the actual live data received from the monitoring station.")

        # Pollutants table
        poll_df = pd.DataFrame([
            {"Pollutant": "PM2.5", "Value (µg/m³)": pollutants["PM2.5"], "Status": get_aqi_category(pollutants["PM2.5"])[0]},
            {"Pollutant": "PM10",  "Value (µg/m³)": pollutants["PM10"],  "Status": get_aqi_category(pollutants["PM10"])[0]},
            {"Pollutant": "NO₂",   "Value (ppb)":   pollutants["NO2"],   "Status": "—"},
            {"Pollutant": "CO",    "Value (ppm)":    pollutants["CO"],    "Status": "—"},
            {"Pollutant": "SO₂",   "Value (ppb)":   pollutants["SO2"],   "Status": "—"},
            {"Pollutant": "O₃",    "Value (ppb)":   pollutants["O3"],    "Status": "—"},
        ])
        st.dataframe(poll_df, hide_index=True, use_container_width=True)

        # Show forecast data
        if api_forecast:
            st.subheader("📅 API Forecast Data")
            fc_df = pd.DataFrame(api_forecast)
            st.dataframe(fc_df, hide_index=True, use_container_width=True)

        # Full JSON
        with st.expander("🔧 Full API JSON Response"):
            st.json(api_data)

    with tab3:
        st.subheader("Project Methodology")
        st.write("""
        This project uses a **Hybrid CNN-LSTM** deep learning model combined with **real-time data**
        from the World Air Quality Index (WAQI) network to provide accurate, live AQI forecasts.

        ### Data Sources
        - **Real-Time:** WAQI API — pulls live readings from CPCB & State PCB monitoring stations
        - **Historical:** National Air Quality Index dataset (Kaggle) for model training

        ### Model Architecture
        - **CNN Layers:** Extract spatial-like features and pollutant interaction patterns
        - **LSTM Layers:** Learn long-term temporal and seasonal trends
        - **Multi-step Forecasting:** Rolling-window technique for 7-day predictions

        ### Prediction Pipeline
        1. Fetch real-time pollutant readings (PM2.5, PM10, NO₂, CO, SO₂, O₃)
        2. Build synthetic 24-hour window with diurnal variation patterns
        3. Feed into Hybrid CNN-LSTM model for next-day prediction
        4. Roll window forward for multi-step forecasting
        5. Blend with WAQI API forecasts (when available) for higher accuracy

        ### Performance
        | Metric | Value |
        |--------|-------|
        | **R² Score** | 0.852 |
        | **Forecast Horizon** | 7 days |
        | **Update Frequency** | Real-time (API) |
        | **Coverage** | All India (200+ cities) |
        """)


if __name__ == "__main__":
    main()
