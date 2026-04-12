# -*- coding: utf-8 -*-
"""
Created on Fri Feb 27 08:36:56 2026
STREAMLIT WEBSITE script
@author: feder
"""


import streamlit as st
import pandas as pd
import numpy as np
import datetime
import base64
from streamlit_folium import st_folium
import folium

from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="my_app")


#%% Cache
@st.cache_data
def get_coords(country):
    location = geolocator.geocode(country)
    return [location.latitude, location.longitude] if location else None


#%%
st.title('Ayuda Contenedores impacto')
#%%
# Load datas
data_general = pd.read_excel("testfile.xlsx", engine="openpyxl")
# fix reading dates 
data_general['Fecha'] = pd.to_datetime(data_general['Fecha'], dayfirst=True, errors="coerce")
start_year = data_general['Fecha'].min().year #.strftime("%Y")
end_year = data_general['Fecha'].max().year #.strftime("%Y")

# Add coordinates countries
data_general['coords'] = data_general['Destino'].apply(get_coords)


# data_bici = pd.read_excel("ejemplo - excel publico.xlsx", sheet_name="Estadisticas bici")
# data_ordenadores = pd.read_excel("ejemplo - excel publico.xlsx", sheet_name="Estadisticas ordenadores")
# data_comida = pd.read_excel("ejemplo - excel publico.xlsx", sheet_name="Estadisticas comida")


# Left side bar where to enter time period of interest
#%%
time_range = st.sidebar.radio(
    "Selecciona periodo",
    ["Todos los años", "Especifica año(s)", "Especifica periodo"]
)

if time_range == "Especifica año(s)":
    years = st.sidebar.multiselect(
        "Cuales año(s)?",
        list(range(start_year, end_year+1))
    )
    if years: 
        data_show = data_general[data_general['Fecha'].dt.year.isin(list(map(int, years)))]
    
    
elif time_range == "Especifica periodo": # Y - M - D
    today = datetime.datetime.now()
    first_contenedor_date = datetime.date(start_year, 1, 1) 
    
    date_range = st.date_input(
        "Select your vacation for next year",
        (first_contenedor_date, today),
        first_contenedor_date,
        today,
        format="MM.DD.YYYY",
    )
    
    data_show = data_general[(data_general['Fecha'] >= pd.to_datetime(date_range[0])) & (data_general['Fecha'] <= pd.to_datetime(date_range[1]))]
    
    
else:
    pass
    #take all df
    
    
#%% Display data as table
st.subheader('Raw data')
st.write(data_show) # this displays all kinds of data based on type
   
#%%
st.subheader('Statistics')

# Calculate and display totals

def get_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def card(img_path, label, value):
    img_base64 = get_base64(img_path)

    st.markdown(f"""
        <div style="text-align:center;">
            <img src="data:image/png;base64,{img_base64}" width="60">
            <div style="font-size:16px; margin-top:10px;">{label}</div>
        </div>
    """, unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    total_bicis = sum(data_show["Bici"])
    card("images/bike.png", f"{total_bicis} bikes")

with col2:
    total_pcs = sum(data_show["Ordenadores"])
    card("images/computer.png", f"{total_pcs} computers")

with col3:
    total_food = sum(data_show["Comida"])
    card("images/comida.png", f"{total_food} kg of food")


#%%
st.subheader('Map of all pickups')


m = folium.Map(location=[20, 0], zoom_start=2) #world view

for _, row in data_show.iterrows():
    if row['coords'] is not None:
        folium.Marker(
            location=row['coords'],
            popup=f"""
                Contenedor numero {row['Numero Contenedor']} a {row['Destino']}<br>
                Fecha: {row['Fecha']}<br>
                <a href="{row['Enlace']}" target="_blank">Link</a>
            """,
            icon=folium.Icon(color="red")
        ).add_to(m)

st_folium(m, width=700, height=500)

