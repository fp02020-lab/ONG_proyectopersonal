# -*- coding: utf-8 -*-
"""
Created on Fri Feb 27 08:36:56 2026
STREAMLIT WEBSITE script
@author: feder
"""


import streamlit as st
import pandas as pd
import datetime
import base64
from streamlit_folium import st_folium
import folium
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="my_app")


#%% Cache geocoding
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

data_general['Fecha'] = data_general['Fecha'].dt.strftime('%d/%m/%Y')

# Add coordinates countries
unique_countries = data_general['Destino'].dropna().unique()
coords_dict = {c: get_coords(c) for c in unique_countries}
data_general['coords'] = data_general['Destino'].map(coords_dict)


# 
#%% Left side bar where to enter time period of interest and location
st.sidebar.title("Filtros")

# TIME SECTION
with st.sidebar.container():
    st.markdown("### ⏱️ Período de tiempo")

    time_range = st.radio(
        "Selecciona periodo:",
        ["Todos los años", "Especifica año(s)", "Especifica periodo"])

    data_show = data_general.copy()

    if time_range == "Especifica año(s)":
        years = st.multiselect(
            "Cuales año(s)?",
            list(range(start_year, end_year+1)))
        if years: 
            data_show = data_show[data_show['Fecha'].dt.year.isin(list(map(int, years)))]
        
        
    elif time_range == "Especifica periodo": # Y - M - D
        today = datetime.datetime.today()
        first_contenedor_date = datetime.date(start_year, 1, 1) 
        
        date_range = st.date_input(
            "Rango de fechas",
            (first_contenedor_date, today),
            first_contenedor_date,
            today,
            format="MM.DD.YYYY")
        
        data_show = data_show[(data_show['Fecha'] >= pd.to_datetime(date_range[0])) & (data_show['Fecha'] <= pd.to_datetime(date_range[1]))]
       
st.sidebar.markdown("---")

# LOCATION 
with st.sidebar.container():
    st.markdown("### 🌍 Destino")

    locations = st.radio(
        "Selecciona países:",
        ["Todos los países", "Especifica país(es)"])

     
    countries = sorted(data_show["Destino"].dropna().unique())
    
    if locations == "Especifica país(es)":
        selected_countries = st.multiselect(
            "Buscar países",
            options=countries,
            default=[],
            help="Escribe para buscar") 
        if selected_countries:
            data_show = data_show[data_show['Destino'].isin(selected_countries)]
   
#%%
st.subheader('Material enviado')

# Calculate and display totals

def get_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def card(img_path, text):
    img_base64 = get_base64(img_path)

    st.markdown(f"""
        <div style="
            text-align:center;
            height:150px;
            display:flex;
            flex-direction:column;
            justify-content:center;
            align-items:center;
        ">
            <img src="data:image/png;base64,{img_base64}" height="80">
            <div style="font-size:18px; margin-top:10px; font-weight:bold;">
                {text}
            </div>
        </div>
    """, unsafe_allow_html=True)

# ---- ROW 1 (4 columns) ----
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_bicis = data_show["Bici"].sum()
    card("images/bike.png", f"{total_bicis} bicis")

with col2:
    total_pcs = data_show["Ordenadores"].sum()
    card("images/computer.png", f"{total_pcs} ordenadores")

with col3:
    total_food = data_show["Comida"].sum()
    card("images/food.png", f"{total_food/1000:.1f} ton de comida")

with col4:
    total_hospital = data_show["Hospital"].sum()  
    card("images/hospital.png", f"{total_hospital} cajas de material de hospital")


# ---- ROW 2 (4 columns) ----
col5, col6, col7, col8 = st.columns(4)

with col5:
    total_clothes = data_show["Ropa"].sum()  
    card("images/clothes.png", f"{total_clothes} cajas de ropa")

with col6:
    total_tools = data_show["Herramientas"].sum()  
    card("images/tools.png", f"{total_tools} herramientas") # measured in pallets or machines

with col7:
    total_solar = data_show["Solar"].sum()  
    card("images/tools.png", f"{total_tools} herramientas")

with col8:
    total_sewing = data_show["Costura"].sum()  
    card("images/tools.png", f"{total_tools} herramientas")
    
expander = st.expander("Otras donaciones")

with expander:

    # ---- ROW 1 ----
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_clothes = data_show["Ropa"].sum()  
        card("images/clothes.png", f"{total_clothes} cajas de ropa")

    with col2:
        total_clothes = data_show["Ropa"].sum()  
        card("images/clothes.png", f"{total_clothes} cajas de ropa")

    with col3:
        total_clothes = data_show["Ropa"].sum()  
        card("images/clothes.png", f"{total_clothes} cajas de ropa")

    with col4:
        total_clothes = data_show["Ropa"].sum()  
        card("images/clothes.png", f"{total_clothes} cajas de ropa")

    # ---- ROW 2 ----
    col5, col6, col7 = st.columns(3)

    with col5:
        total_clothes = data_show["Ropa"].sum()  
        card("images/clothes.png", f"{total_clothes} cajas de ropa")

    with col6:
        total_clothes = data_show["Ropa"].sum()  
        card("images/clothes.png", f"{total_clothes} cajas de ropa")

    with col7:
        total_clothes = data_show["Ropa"].sum()  
        card("images/clothes.png", f"{total_clothes} cajas de ropa")


#%%
st.subheader('Mapa de envios')


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

#%% Display data as table
st.subheader('Datos')
raw_data_show = data_show.copy()
st.write(raw_data_show.drop(['coords'], axis=1)) # this displays all kinds of data based on type
