# -*- coding: utf-8 -*-
"""
Created on Fri Feb 27 08:36:56 2026
STREAMLIT WEBSITE script
@author: feder
"""

#%% IMPORT PACKAGES
import streamlit as st
import pandas as pd
import datetime
import base64
from streamlit_folium import st_folium
import folium
from folium.features import DivIcon
from geopy.geocoders import Nominatim
import numpy as np

#%% SET GRAPHICS
st.markdown("""
<style>
/* Sidebar background */
section[data-testid="stSidebar"] {
    background-color: #E8F5E9 !important;
}

/* Sidebar text */
section[data-testid="stSidebar"] * {
    color: #1B1B1B !important;
}

/* Main area stays clean white */
.stApp {
    background-color: white;
}

/* Optional: soften cards if you use them */
div[data-testid="stVerticalBlock"] {
    background-color: transparent;
}
</style>
""", unsafe_allow_html=True)


#%%
from pages import page1

st.set_page_config(page_title="Envíos historicos")

page = st.sidebar.selectbox("Go to", ["Envíos historicos", "Material enviado"])

if page == "Envíos historicos":
    st.title('Ayuda Contenedores impacto - Envíos historicos')
    # Load data
    from data_loader import load_historical_data
    df_contenedores, datasets = load_historical_data("Historical_data_AC.xlsx")

    # Histograms
    st.subheader('📊 Histórico de envíos por año')
    total_contenedores = df_contenedores["Envíos"].sum()
    st.metric("Total contenedores", total_contenedores)
    st.bar_chart(df_contenedores.set_index("Año"), color="#4CAF50")

    st.subheader("📦 Envíos históricos de material")
    selected = st.selectbox(
        "Selecciona categoría",
        list(datasets.keys()))

    df_selected = datasets[selected]
    total_selected = int(df_selected["Envíos"].sum())
    if selected == "Comida":
        st.metric(f"Total {selected}", f"{int(total_selected/1000)} ton")
    else:
        st.metric(f"Total {selected}", total_selected)

    st.bar_chart(df_selected.set_index("Año"), color="#4CAF50")

elif page == "Material enviado":
    page1.render()   




