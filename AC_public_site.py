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


#%% Display histogram
st.subheader('📊 Histórico de envíos por año')
# AC historical data contenedores
d = {"Año": np.arange(2012,2026), "Envíos": [7,9,12,13,21,24,29,33,24,34,45,51,59,66]}
df_contenedores = pd.DataFrame(data=d)
total_contenedores = df_contenedores["Envíos"].sum()
st.metric("Total contenedores", total_contenedores)

st.bar_chart(
    df_contenedores.set_index("Año"),
    color="#4CAF50")

# More data
st.subheader("📦 Envíos históricos de material")
df_sillas_de_ruedas = pd.DataFrame(data= {"Año": np.arange(2022,2026), "Envíos": [116, 137, 161, 156]})
df_andadores = pd.DataFrame(data= {"Año": np.arange(2022,2026), "Envíos": [62, 20, 120, 82]})
df_bicis = pd.DataFrame(data= {"Año": np.arange(2020,2026), "Envíos": [175, 422, 630, 880, 1065, 629]})
df_ordenadores = pd.DataFrame(data= {"Año": np.arange(2022,2026), "Envíos": [179, 589, 872, 773]})
df_maquinas_coser = pd.DataFrame(data= {"Año": np.arange(2022,2026), "Envíos": [78, 85, 90, 123]})
df_comida = pd.DataFrame(data= {"Año": np.arange(2020,2026), "Envíos": [59837, 49600, 347523, 430686, 472442, 601928]})
df_porteria = pd.DataFrame(data= {"Año": np.arange(2022,2026), "Envíos": [16, 8, 10, 14]})
df_camashospital = pd.DataFrame(data= {"Año": np.arange(2021,2026), "Envíos": [31, 64, 132, 461, 813]})
df_cunasclimaticas = pd.DataFrame(data= {"Año": np.arange(2021,2026), "Envíos": [15, 35, 70, 40, 71]})

# put datasets in a dictionary
datasets = {
    "Sillas de ruedas": df_sillas_de_ruedas,
    "Andadores": df_andadores,
    "Bicis": df_bicis,
    "Ordenadores": df_ordenadores,
    "Máquinas de coser": df_maquinas_coser,
    "Comida": df_comida,
    "Portería": df_porteria,
    "Camas hospital": df_camashospital,
    "Cunas climáticas": df_cunasclimaticas}

selected = st.selectbox(
    "Selecciona categoría",
    list(datasets.keys()))

df_selected = datasets[selected]
total_selected = df_selected["Envíos"].sum()

st.metric(f"Total {selected}", total_selected)

st.bar_chart(
    df_selected.set_index("Año"),
    color="#4CAF50")






#%% ---------------------------------------------------------------------------





#%% Display histogram NEW ___ READING EXCEL
#%% LOAD FROM EXCEL HISTORICAL DATA
data_history_contenedores = pd.read_excel("Historical_data_AC.xlsx", sheet_name= "All containers", engine="openpyxl")
data_history_material = pd.read_excel("Historical_data_AC.xlsx", sheet_name= "Material", engine="openpyxl")

##### ENVIOS
years = sorted(data_history_contenedores["Fecha"].dropna().unique())
envios = []
for year_i in years:
    envios.append(sum(data_history_contenedores["Fecha"] == year_i))
df_contenedores = pd.DataFrame(data= {"Año": years, "Envíos": envios})

# histogram
st.subheader('📊 Histórico de envíos por año')
total_contenedores = df_contenedores["Envíos"].sum()
st.metric("Total contenedores", total_contenedores)
st.bar_chart(df_contenedores.set_index("Año"), color="#4CAF50")

##### MATERIAL
material = []
dataframes = []
for i in np.arange(0,len(data_history_material["Material enviado"])):
    row = data_history_material.loc[i].dropna()

    material.append( data_history_material["Material enviado"][i] )
    dataframes.append( pd.DataFrame(data= {"Año": [int(idx) for idx in row.index if str(idx).isdigit()], "Envíos": [row[idx] for idx in row.index if str(idx).isdigit()]}) )
    
datasets = {}
for name, df in zip(material, dataframes):
    datasets[name] = df

# More data
st.subheader("📦 Envíos históricos de material")
selected = st.selectbox(
    "Selecciona categoría",
    list(datasets.keys()))

df_selected = datasets[selected]
total_selected = int(df_selected["Envíos"].sum())
if selected == "Comida":
    st.metric(f"Total {selected}", f"{total_selected/1000} ton")
else:
    st.metric(f"Total {selected}", total_selected)

st.bar_chart(
    df_selected.set_index("Año"),
    color="#4CAF50")


