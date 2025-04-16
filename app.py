import streamlit as st
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
def show_flag(name):
    try:
        url = f"https://countryflagsapi.com/png/{name.replace(' ', '%20')}"
        img = requests.get(url).content
        st.image(Image.open(BytesIO(img)), width=100)
    except:
        st.write("No flag")

# Streamlit settings
st.set_page_config(page_title="Country Clash", layout="wide")

# Title
st.markdown("<h1 style='text-align: center;'>🌍 Country Clash</h1>", unsafe_allow_html=True)

# Audio (background music)
st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")

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

        st.success(f"🏆 **Winner: {winner}**")
        st.balloons()
