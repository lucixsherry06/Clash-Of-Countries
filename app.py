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

# ========== Load Data ==========
df = pd.read_csv("cleaned_countries.csv")
model = joblib.load("battle_model.pkl")

# ========== Helper Functions ==========

def get_country_code(country_name):
    try:
        return pycountry.countries.lookup(country_name).alpha_2.lower()
    except LookupError:
        return None

def get_stats(country):
    row = df[df['Country'] == country].iloc[0]
    def num(val):
        if pd.isna(val): return 0.0
        match = re.search(r"[\d,.]+", str(val))
        return float(match.group().replace(",", "")) if match else 0.0
    return {
        "gdp": num(row['Economy: Real GDP (purchasing power parity)']),
        "military": num(row['Military and Security: Military expenditures']),
        "literacy": num(row['People and Society: Literacy - total population']),
        "birth": num(row['People and Society: Birth rate']),
        "death": num(row['People and Society: Death rate']),
    }

def show_flag(country_name):
    code = get_country_code(country_name)
    if code:
        url = f"https://flagcdn.com/w80/{code}.png"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                st.image(Image.open(BytesIO(response.content)), width=80)
            else:
                st.write("⚠️ Flag not available.")
        except:
            st.write("⚠️ Error fetching flag.")
    else:
        st.write("⚠️ Invalid country name.")

# ========== Page Settings ==========
st.set_page_config(page_title="Country Clash", layout="wide")
st.markdown("<h1 style='text-align: center;'>🌍 Country Clash</h1>", unsafe_allow_html=True)

# ========== Intro Music (Autoplay) ==========
st.markdown("""
<audio autoplay>
  <source src="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3" type="audio/mp3">
</audio>
""", unsafe_allow_html=True)

# ========== Country Selection ==========
country_list = df['Country'].dropna().unique()
col1, col2 = st.columns(2)
with col1:
    country1 = st.selectbox("Choose Country A", country_list)
with col2:
    country2 = st.selectbox("Choose Country B", country_list)

# ========== Display Flags ==========
col1, col2 = st.columns(2)
with col1:
    show_flag(country1)
with col2:
    show_flag(country2)

# ========== Click Sound Effect ==========
components.html(
    """
    <script>
    function playClickSound() {
        var audio = new Audio("https://www.fesliyanstudios.com/play-mp3/387");
        audio.play();
    }
    </script>
    <button onclick="playClickSound()" style="display:none">Play</button>
    """, height=0
)

# ========== Battle Button ==========
if st.button("⚔️ Start the Battle"):
    if country1 == country2:
        st.warning("⚠️ Choose different countries!")
    else:
        with st.spinner("Preparing the battle..."):
            time.sleep(1)
            stats1 = get_stats(country1)
            stats2 = get_stats(country2)

        # Show Stats
        st.subheader(f"📊 {country1} Stats:")
        st.write(stats1)
        st.subheader(f"📊 {country2} Stats:")
        st.write(stats2)

        # Show Pre-Battle Animation
        st.markdown("### ⚔️ Battle Starts In...")
        gif_col = st.empty()
        gif_col.markdown("""
            <div style="display: flex; justify-content: center; margin-top: 10px;">
                <img src="https://media.giphy.com/media/3o7bu3XilJ5BOiSGic/giphy.gif" style="max-width: 400px; border-radius: 10px;" />
            </div>
        """, unsafe_allow_html=True)

        # Countdown timer
        countdown_text = st.empty()
        for i in range(5, 0, -1):
            countdown_text.markdown(f"<h2 style='text-align: center;'>⏳ {i}</h2>", unsafe_allow_html=True)
            time.sleep(1)

        # Clear GIF and countdown
        gif_col.empty()
        countdown_text.empty()

        # Predict winner
        input_features = np.array([[stats1["gdp"] - stats2["gdp"],
                                    stats1["military"] - stats2["military"],
                                    stats1["literacy"] - stats2["literacy"],
                                    stats1["birth"] - stats2["birth"],
                                    stats1["death"] - stats2["death"]]])
        result = model.predict(input_features)[0]
        winner = country1 if result == 1 else country2

        # Show result after delay
        st.success(f"🏆 **Winner: {winner}**")

        # Result Sound
        st.markdown("""
            <audio autoplay>
                <source src="https://www.fesliyanstudios.com/play-mp3/6671" type="audio/mp3">
            </audio>
        """, unsafe_allow_html=True)

        # Celebration 🎈
        st.balloons()
