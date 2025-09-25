import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import pytz
import os

st.set_page_config(page_title="Giza Weather", page_icon="☀️", layout="centered")

# ----------------- CSS / STYLE -----------------
st.markdown(
    """
    <style>
    :root {
        --bg1: #0b2a4a; /* top */
        --bg2: #5b3b63; /* bottom */
        --card: rgba(255,255,255,0.04);
        --muted: rgba(230,230,255,0.6);
        --pink: #ff7ab6;
        --orange: #ff9a4d;
    }
    .stApp {
        background: linear-gradient(180deg, var(--bg1) 0%, var(--bg2) 100%);
        color: #eef6ff;
    }
    .card {
        background: var(--card);
        border-radius: 16px;
        padding: 12px;
        margin-bottom: 12px;
        box-shadow: 0 8px 30px rgba(2,6,23,0.5);
    }
    .header-city { font-size:34px; font-weight:700; margin:0; }
    .header-sub { color:var(--muted); margin-top:4px; }
    .big-temp { font-size:48px; font-weight:800; margin:6px 0 0; color: #fff; }
    .hour-block { text-align:center; font-size:14px; color:var(--muted); padding:6px; }
    .hour-temp { font-size:18px; margin-top:6px; font-weight:700; color:#fff; }
    .tiny-muted { color:var(--muted); font-size:13px; }
    .day-row { display:flex; align-items:center; justify-content:space-between; gap:12px; padding:8px 0; }
    .progress-track { background: rgba(255,255,255,0.03); border-radius:8px; height:10px; position:relative; overflow:hidden; }
    .progress-fill { position:absolute; height:100%; border-radius:8px; background: linear-gradient(90deg,var(--orange),var(--pink)); }
    </style>
    """, unsafe_allow_html=True
)

# ----------------- Load data (or generate demo) -----------------
# You can change these paths to your CSVs (Drive paths if in Colab)
DAILY_PATH = "/content/drive/MyDrive/Hackathon/cairo_daily_weather.csv"
HOURLY_PATH = "/content/drive/MyDrive/Hackathon/cairo_hourly_weather.csv"

def load_or_demo():
    if os.path.exists(DAILY_PATH):
        daily = pd.read_csv(DAILY_PATH, parse_dates=["date"])
    else:
        # demo daily 14 days
        rng = pd.date_range(end=datetime.today(), periods=14, freq="D")
        daily = pd.DataFrame({
            "date": rng,
            "T2M_min": np.round(np.random.uniform(16,22,len(rng)),1),
            "T2M_max": np.round(np.random.uniform(28,34,len(rng)),1),
        })
        daily["T2M_mean"] = ((daily["T2M_min"] + daily["T2M_max"]) / 2).round(1)
        daily["wind_speed_mean"] = np.round(np.random.uniform(1,6,len(rng)),1)
        daily["QV2M_mean"] = np.round(np.random.uniform(0.2,0.6,len(rng)),2)

    if os.path.exists(HOURLY_PATH):
        hourly = pd.read_csv(HOURLY_PATH, parse_dates=["time"])
    else:
        last_mean = daily.iloc[-1]["T2M_mean"]
        hrs = pd.date_range(end=datetime.now(), periods=8, freq="H")
        hourly = pd.DataFrame({
            "time": hrs,
            "T2M": np.round(np.linspace(last_mean-2, daily.iloc[-1]["T2M_max"], len(hrs)),1),
            "icon": ["☀️"]*len(hrs)
        })
    return daily, hourly

daily, hourly = load_or_demo()

# ----------------- Header (city, now, summary) -----------------
tz = pytz.timezone("Africa/Cairo")
now_local = datetime.now(tz).strftime("%I:%M %p")

with st.container():
    st.markdown("<div class='card' style='display:flex; align-items:center; justify-content:space-between;'>", unsafe_allow_html=True)
    cols = st.columns([1,2])
    with cols[0]:
        st.markdown(f"<div style='padding:8px 0 8px 8px'>"
                    f"<div class='tiny-muted'>HOME</div>"
                    f"<div class='header-city'>Giza</div>"
                    f"<div class='header-sub'>{daily.iloc[-1]['T2M_mean']}° | Sunny</div>"
                    f"</div>", unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"<div style='text-align:right; padding-right:12px;'>"
                    f"<div class='tiny-muted'>Local time: {now_local}</div>"
                    f"<div class='big-temp'>{daily.iloc[-1]['T2M_mean']}°</div>"
                    f"<div class='tiny-muted'>Partly cloudy conditions expected around 3PM. Wind gusts up to 10 km/h.</div>"
                    f"</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>")

# ----------------- Hourly strip (Now + next hours) -----------------
st.markdown("<div class='card'><strong>Now / Hourly</strong></div>", unsafe_allow_html=True)
hours = hourly.copy().reset_index(drop=True)
cols = st.columns(len(hours))
for i, row in hours.iterrows():
    with cols[i]:
        st.markdown(f"<div class='hour-block'>{row['time'].strftime('%I %p')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center; font-size:22px'>{row.get('icon','☀️')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='hour-temp'>{row['T2M']}°</div>", unsafe_allow_html=True)

st.markdown("<br>")

# ----------------- 10-day Forecast -----------------
st.markdown("<div class='card'><strong>10-Day Forecast</strong></div>", unsafe_allow_html=True)
forecast_days = daily.tail(10).copy().reset_index(drop=True)
global_min = daily["T2M_min"].min()
global_max = daily["T2M_max"].max()
span = (global_max - global_min) if (global_max - global_min)!=0 else 1

for idx, r in forecast_days.iterrows():
    dayname = r["date"].strftime("%a")
    tmin = r["T2M_min"]
    tmax = r["T2M_max"]
    left_pct = int((tmin - global_min)/span * 100)
    right_pct = int((tmax - global_min)/span * 100)
    fill_left = max(0, min(100, left_pct))
    fill_width = max(2, right_pct - fill_left)

    st.markdown(f"""
    <div class='card'>
      <div class='day-row'>
        <div style='display:flex; align-items:center; gap:12px; width:160px;'>
          <div style='font-weight:600'>{dayname}</div>
          <div style='font-size:18px'>☀️</div>
          <div class='tiny-muted'>{tmin}°</div>
        </div>

        <div style='flex:1; padding:0 12px;'>
          <div class='progress-track'>
            <div class='progress-fill' style='left:{fill_left}%; width:{fill_width}%;'></div>
          </div>
        </div>

        <div style='width:60px; text-align:right; font-weight:700'>{tmax}°</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ----------------- Today details -----------------
st.markdown("<br>")
st.markdown("<div class='card'><strong>Details (Today)</strong></div>", unsafe_allow_html=True)
today = forecast_days.iloc[-1]
c1,c2,c3,c4 = st.columns(4)
c1.metric("Temp (avg)", f"{today.get('T2M_mean', round((today['T2M_min']+today['T2M_max'])/2,1))} °C")
c2.metric("Wind", f"{today.get('wind_speed_mean', 'N/A')} m/s")
c3.metric("Humidity", f"{int(today.get('QV2M_mean',0)*100)} %")
c4.metric("Pressure", f"{int(today.get('PS_mean', today.get('PS',101325)))} Pa")

st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
st.markdown("<div class='tiny-muted'>Customize icons/colors/data-paths to match your dataset.</div>", unsafe_allow_html=True)
