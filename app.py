import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import joblib
import time
import requests
from PIL import Image
import re
from io import BytesIO
import pycountry
import plotly.express as px

if "match_history" not in st.session_state:
    st.session_state.match_history = []

# Load data and models
df = pd.read_csv("battle_ready_countries_final.csv")
model = joblib.load("battle_model.pkl")
scaler = joblib.load("battle_scaler.pkl")

# Helper Functions
def get_country_code(country_name):
    special_cases = {
        "Russia": "ru",
        "United Kingdom": "gb",
        "South Korea": "kr",
        "North Korea": "kp",
        "Iran": "ir",
        "Vietnam": "vn",
        "Vatican City": "va",
        "United States": "us"
        # Add more as needed
    }

    if country_name in special_cases:
        return special_cases[country_name]

    try:
        return pycountry.countries.lookup(country_name).alpha_2.lower()
    except LookupError:
        return None


def get_stats(country):
    row = df[df['Country'] == country].iloc[0]
    return {
        "gdp": row['gdp'],
        "military": row['military'],
        "literacy": row['literacy'],
        "birth": row['birth'],
        "death": row['death']
    }

def show_flag(country_name):
    code = get_country_code(country_name)
    if code:
        url = f"https://flagcdn.com/w80/{code}.png"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                st.image(Image.open(BytesIO(response.content)), width=80)
        except:
            st.write("⚠️ Error fetching flag.")

def draw_normalized_bar_chart(stats1, stats2, country1, country2):
    categories = list(stats1.keys())
    values1 = [stats1[k] for k in categories]
    values2 = [stats2[k] for k in categories]
    max_vals = [max(v1, v2) for v1, v2 in zip(values1, values2)]
    norm1 = [v / m if m != 0 else 0 for v, m in zip(values1, max_vals)]
    norm2 = [v / m if m != 0 else 0 for v, m in zip(values2, max_vals)]

    df_chart = pd.DataFrame({
        'Stat': categories * 2,
        'Normalized Value': norm1 + norm2,
        'Country': [country1] * len(categories) + [country2] * len(categories)
    })

    fig = px.bar(df_chart, x='Stat', y='Normalized Value', color='Country', barmode='group', title="📊 Stat Comparison")
    st.plotly_chart(fig, use_container_width=True)

def calculate_score(stats):
    gdp_score = stats['gdp'] / 978007000000
    military_score = stats['military'] / 30
    literacy_score = stats['literacy'] / 100
    birth_score = stats['birth'] / 46.6
    death_score = 1 - (stats['death'] / 18.6)
    return (gdp_score * 0.3 + military_score * 0.25 + literacy_score * 0.2 + birth_score * 0.15 + death_score * 0.1)

# Page Config
st.set_page_config(page_title="Country Clash", layout="wide")
# 🎵 Background music with mute/unmute toggle using JS
mute_toggle = st.checkbox("🔇 Mute Music", value=False)

components.html(f"""
    <audio id="bg-music" autoplay loop>
        <source src="https://raw.githubusercontent.com/lucixsherry06/Clash-Of-Countries/refs/heads/main/music/8-bit-loop-189494.mp3" type="audio/mp3">
    </audio>
    <script>
        document.addEventListener("DOMContentLoaded", function() {{
            const audio = document.getElementById("bg-music");
            if (audio) {{
                audio.volume = {0.0 if mute_toggle else 0.5};
            }}
        }});
    </script>
""", height=0)

#Title and Description
st.markdown("<h1 style='text-align: center;'>🌍 Country Clash</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Choose two countries to battle it out and see which one comes out on top!</p>", unsafe_allow_html=True)


# Country Selection
country_list = df['Country'].dropna().unique()
col1, col2 = st.columns(2)
with col1:
    country1 = st.selectbox("Choose Country A", country_list)
with col2:
    country2 = st.selectbox("Choose Country B", country_list)

# Flags
draw1, draw2 = st.columns(2)
with draw1:
    show_flag(country1)
with draw2:
    show_flag(country2)

# Mode Selection
mode = st.radio("Choose Battle Mode:", ["🤖 AI Model", "🧮 Formula-Based Scoring"])


# Battle Logic
if st.button("⚔️ Start the Battle"):
    if country1 == country2:
        st.warning("⚠️ Choose different countries!")
    else:
        with st.spinner("Preparing the battle..."):
            time.sleep(1)
            stats1 = get_stats(country1)
            stats2 = get_stats(country2)

        st.subheader(f"📊 {country1} Stats:")
        st.write(stats1)
        st.subheader(f"📊 {country2} Stats:")
        st.write(stats2)

        gif_col = st.empty()
        gif_col.markdown("""
        <div style="display: flex; justify-content: center; margin-top: 10px;">
            <img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNTcxamdneHkwcjFza2l4Y2JqY215MzJiemFycGR3cjY0eDQwdnZzaiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/cbJJZ0zLfNulFNBjHI/giphy.gif" style="max-width: 400px; border-radius: 10px;" />
        </div>
        """, unsafe_allow_html=True)
#Countdown 3,2,1
        countdown_text = st.empty()
        st.markdown("""
            <audio autoplay>
                <source src="https://raw.githubusercontent.com/lucixsherry06/Clash-Of-Countries/refs/heads/main/music/three-two-one-fight-deep-voice-38382.mp3" type="audio/mp3">
            </audio>
        """, unsafe_allow_html=True)
        for i in range(4, 0, -1):
            countdown_text.markdown(f"<h2 style='text-align: center;'>⏳ {i}</h2>", unsafe_allow_html=True)
            time.sleep(1)
        gif_col.empty()
        countdown_text.empty()

        draw_normalized_bar_chart(stats1, stats2, country1, country2)

        if mode == "🤖 AI Model":
            input_features = np.array([[stats1["gdp"] - stats2["gdp"],
                                        stats1["military"] - stats2["military"],
                                        stats1["literacy"] - stats2["literacy"],
                                        stats1["birth"] - stats2["birth"],
                                        stats1["death"] - stats2["death"]]])
            input_scaled = scaler.transform(input_features)
            result = model.predict(input_scaled)[0]
            winner = country1 if result == 1 else country2
        else:
            score1 = calculate_score(stats1)
            score2 = calculate_score(stats2)
            winner = country1 if score1 > score2 else country2

        st.session_state.match_history.append({
            "country1": country1,
            "country2": country2,
            "winner": winner
        })

        st.sidebar.title("🏅 Match History")
        if st.session_state.match_history:
            for i, match in enumerate(reversed(st.session_state.match_history[-5:]), 1):
                st.sidebar.write(f"**Match {i}**: {match['country1']} vs {match['country2']} → 🏆 {match['winner']}")
        else:
            st.sidebar.write("No matches yet. Start a battle!")

        st.success(f"🏆 **Winner: {winner}**")
        st.markdown("""
            <audio autoplay>
                <source src="https://raw.githubusercontent.com/lucixsherry06/Clash-Of-Countries/refs/heads/main/music/success-1-6297.mp3" type="audio/mp3">
            </audio>
        """, unsafe_allow_html=True)
        st.balloons()
