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
from folium.features import DivIcon
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
    total_bicis = data_show["Bicis"].sum()
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
st.write("") # spacing vertical
col5, col6, col7, col8 = st.columns(4)

with col5:
    total_clothes = data_show["Ropa"].sum()  
    card("images/clothes.png", f"{total_clothes} cajas de ropa")

with col6:
    total_tools = data_show["Herramientas"].sum()  
    card("images/tools.png", f"{total_tools} herramientas") # measured in pallets or machines

with col7:
    total_solar = data_show["Solar"].sum()  
    card("images/solar.png", f"{total_solar} plantas fotovoltaicas")

with col8:
    total_sewing = data_show["Costura"].sum()  
    card("images/costura.png", f"{total_sewing} maquinas de cocer")
    
expander = st.expander("Otras donaciones")

with expander:

    # ---- ROW 1 ----
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_clothes = data_show["Material de costruccion"].sum()  
        card("images/construction.png", f"{total_clothes} material de costruccion")

    with col2:
        total_housestuff = data_show["Articulos de casa"].sum()  
        card("images/house.png", f"{total_housestuff} articulos de casa")

    with col3:
        total_toys = data_show["Juegos"].sum()  
        card("images/toys.png", f"{total_toys} juegos")

    with col4:
        total_skates = data_show["Patines"].sum()  
        card("images/skates.png", f"{total_skates} patines")

    # ---- ROW 2 ----
    st.write("") # spacing vertical
    col5, col6, col7, col8 = st.columns(4)

    with col5:
        total_cleaning = data_show["Limpieza y higiene"].sum()  
        card("images/higiene.png", f"{total_cleaning} cajas de material de limpieza y higiene")

    with col6:
        total_school = data_show["Material escolar"].sum()  
        card("images/school.png", f"{total_school} cajas de material escolar")

    with col7:
        total_others = data_show["Otro"].sum()  
        card("images/others.png", f"{total_others} otro material")
    with col8:
        pass


#%% MAPA DE ENVIOS
st.subheader('Mapa de envios')

# Group data by coordinates
grouped = data_show[data_show['coords'].notna()].groupby('coords')

m = folium.Map(location=[20, 0], zoom_start=2)

for coords, group in grouped:
    count = len(group)

    # Build list of items
    items_html = "<ul>"
    details_js_array = []

    for i, (_, row) in enumerate(group.iterrows()):
        items_html += f'''
        <li>
            <a href="#" onclick="showDetail({i})">
                Contenedor {row['Numero Contenedor']}
            </a>
        </li>
        '''

        details_js_array.append(f"""
            <b>Contenedor:</b> {row['Numero Contenedor']}<br>
            <b>Destino:</b> {row['Destino']}<br>
            <b>Fecha:</b> {row['Fecha']}<br>
            <a href="{row['Enlace']}" target="_blank">Link</a>
        """)

    items_html += "</ul>"

    details_js = "[" + ",".join([f"`{d}`" for d in details_js_array]) + "]"

    popup_html = f"""
    <div id="main-menu">
        <b>Selecciona un envío:</b>
        {items_html}
    </div>

    <div id="detail-view" style="display:none;">
        <button onclick="goBack()">⬅ Volver</button>
        <div id="detail-content"></div>
    </div>

    <script>
    var details = {details_js};

    function showDetail(index) {{
        document.getElementById("main-menu").style.display = "none";
        document.getElementById("detail-view").style.display = "block";
        document.getElementById("detail-content").innerHTML = details[index];
    }}

    function goBack() {{
        document.getElementById("main-menu").style.display = "block";
        document.getElementById("detail-view").style.display = "none";
    }}
    </script>
    """

    folium.Marker(
        location=list(coords),
        popup=folium.Popup(popup_html, max_width=300),
        icon=DivIcon(
            html=f"""
            <div style="
                background-color:green;
                border-radius:50%;
                width:30px;
                height:30px;
                text-align:center;
                color:white;
                font-weight:bold;
                line-height:30px;">
                {count}
            </div>
            """
        )
    ).add_to(m)

st_folium(m, width=700, height=500)



#%% Display data as table
st.subheader('Datos')

raw_data_show = data_show.copy()
raw_data_show['Fecha'] = raw_data_show['Fecha'].dt.strftime('%d/%m/%Y')

st.write(raw_data_show.drop(['coords'], axis=1)) # this displays all kinds of data based on type
