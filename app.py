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




# Load dataset and model
df = pd.read_csv("cleaned_countries.csv")
model = joblib.load("battle_model.pkl")

# Extract stats from a country row

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

# Show flag using API
def show_flag(country_name):
    code = get_country_code(country_name)
    if code:
        url = f"https://flagcdn.com/w80/{code}.png"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                st.image(Image.open(BytesIO(response.content)), width=80)
            else:
                st.write("Flag not available.")
        except:
            st.write("Error fetching the flag.")
    else:
        st.write("Invalid country name.")

# Streamlit settings
st.set_page_config(page_title="Country Clash", layout="wide")

# Title
st.markdown("<h1 style='text-align: center;'>🌍 Country Clash</h1>", unsafe_allow_html=True)

# Audio (background music)
# This adds intro sound once when app is loaded
st.markdown("""
    <audio autoplay>
        <source src="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3" type="audio/mp3">
    </audio>
""", unsafe_allow_html=True)


# Country selectors
country_list = df['Country'].dropna().unique()
col1, col2 = st.columns(2)
with col1:
    country1 = st.selectbox("Choose Country A", country_list)
with col2:
    country2 = st.selectbox("Choose Country B", country_list)

# Show flags
col1, col2 = st.columns(2)
with col1:
    show_flag(country1)
with col2:
    show_flag(country2)


# This adds a click sound when the button is pressed
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

# Battle button
if st.button("⚔️ Start the Battle"):
    if country1 == country2:
        st.warning("Choose different countries!")
    else:
        st.spinner("Preparing the battle...")
        time.sleep(1)
        
        stats1 = get_stats(country1)
        stats2 = get_stats(country2)

        st.subheader(f"{country1} Stats:")
        st.write(stats1)
        st.subheader(f"{country2} Stats:")
        st.write(stats2)

        input_features = np.array([[stats1["gdp"] - stats2["gdp"],
                                    stats1["military"] - stats2["military"],
                                    stats1["literacy"] - stats2["literacy"],
                                    stats1["birth"] - stats2["birth"],
                                    stats1["death"] - stats2["death"]]])

        result = model.predict(input_features)[0]
        winner = country1 if result == 1 else country2
        
        #Gif for battle result
        st.markdown("### 🏴‍☠️ Flag Battle Result")
        st.image("https://media.giphy.com/media/3o7bu3XilJ5BOiSGic/giphy.gif", use_column_width=True)


        st.success(f"🏆 **Winner: {winner}**")
        #Result Sound (e.g., Victory or Defeat trumpet)
        st.markdown("""
    <audio autoplay>
        <source src="https://www.fesliyanstudios.com/play-mp3/6671" type="audio/mp3">
    </audio>
""", unsafe_allow_html=True)

        st.balloons()
