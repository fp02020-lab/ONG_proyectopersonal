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
st.set_page_config(page_title="Home", page_icon="🏠")
st.title('Ayuda Contenedores impacto')

#%% LOAD FROM EXCEL HISTORICAL DATA
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




# data_history_contenedores = pd.read_excel("Historical_data_AC.xlsx", sheet_name= "All containers", engine="openpyxl")
# data_history_material = pd.read_excel("Historical_data_AC.xlsx", sheet_name= "Material", engine="openpyxl")

# ##### ENVIOS
# years = sorted(data_history_contenedores["Fecha"].dropna().unique())
# envios = []
# for year_i in years:
#     envios.append(sum(data_history_contenedores["Fecha"] == year_i))
# df_contenedores = pd.DataFrame(data= {"Año": years, "Envíos": envios})

# # histogram
# st.subheader('📊 Histórico de envíos por año')
# total_contenedores = df_contenedores["Envíos"].sum()
# st.metric("Total contenedores", total_contenedores)
# st.bar_chart(df_contenedores.set_index("Año"), color="#4CAF50")

# ##### MATERIAL
# material = []
# dataframes = []
# for i in np.arange(0,len(data_history_material["Material enviado"])):
#     row = data_history_material.loc[i].dropna()

#     material.append( data_history_material["Material enviado"][i] )
#     dataframes.append( pd.DataFrame(data= {"Año": [int(idx) for idx in row.index if str(idx).isdigit()], "Envíos": [row[idx] for idx in row.index if str(idx).isdigit()]}) )
    
# datasets = {}
# for name, df in zip(material, dataframes):
#     datasets[name] = df

# # More data
# st.subheader("📦 Envíos históricos de material")
# selected = st.selectbox(
#     "Selecciona categoría",
#     list(datasets.keys()))

# df_selected = datasets[selected]
# total_selected = int(df_selected["Envíos"].sum())
# if selected == "Comida":
#     st.metric(f"Total {selected}", f"{int(total_selected/1000)} ton")
# else:
#     st.metric(f"Total {selected}", total_selected)

# st.bar_chart(
#     df_selected.set_index("Año"),
#     color="#4CAF50")


