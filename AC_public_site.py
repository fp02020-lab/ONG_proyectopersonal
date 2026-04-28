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
import numpy as np

geolocator = Nominatim(user_agent="my_app")

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

#%% Cache geocoding
@st.cache_data
def get_coords(country):
    location = geolocator.geocode(country)
    return [location.latitude, location.longitude] if location else None


#%%
st.title('Ayuda Contenedores impacto')
#%%
# Load datas
data_general = pd.read_excel("tabla_publica__TEST.xlsx", engine="openpyxl")
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
    
    # st.markdown("<div style='margin-top:30px'></div>", unsafe_allow_html=True)

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
    
        start_date = st.sidebar.date_input(
            "Fecha inicio",
            first_contenedor_date)
        
        end_date = st.sidebar.date_input(
            "Fecha fin",
            today)
        
        data_show = data_show[
            (data_show["Fecha"] >= pd.to_datetime(start_date)) &
            (data_show["Fecha"] <= pd.to_datetime(end_date)) ]
    
        # date_range = st.date_input(
        #     "Rango de fechas",
        #     (first_contenedor_date, today),
        #     first_contenedor_date,
        #     today,
        #     format="MM.DD.YYYY")
        # data_show = data_show[(data_show['Fecha'] >= pd.to_datetime(date_range[0])) & (data_show['Fecha'] <= pd.to_datetime(date_range[1]))]
        
        
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

def card(img_path, text, info):
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
                <details style="display:inline;">
                        <summary style="
                            display:inline;
                            cursor:pointer;
                            margin-left:5px;
                            font-size:12px;
                            background:#eee;
                            border-radius:50%;
                            padding:2px 6px;
                        ">?</summary>
                        <div style="font-size:12px; margin-top:5px;">
                            {info}
                        </div>
                    </details>
                </div>
            </div>
        """, unsafe_allow_html=True)

# ---- ROW 1 (4 columns) ----
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_bicis = data_show["Bicis [-]"].sum()
    # card("images/bike.png", f"{total_bicis} bicis")
    card("images/bike.png",
         f"{total_bicis} bicis",
         "Número de bicicletas enviadas, no incluye las piezas de repuesto.")

with col2:
    total_pcs = data_show["Ordenadores [-]"].sum()
    card("images/computer.png", f"{total_pcs} ordenadores",
         "Número de ordenadores enviados, no incluye otros dispositivos electrónicos.")

with col3:
    total_food = data_show["Comida [tons]"].sum()
    card("images/food.png", f"{total_food/1000:.1f} ton de comida", 
         "Toneladas de alimentos enviadas.")

with col4:
    total_clothes = data_show["Ropa [-]"].sum()  
    card("images/clothes.png", f"{total_clothes} cajas de ropa", 
         "Incluye ropa, bolsas, zapatos, ropa de seguridad y complementos.")
    
    
    
#### MISSING SILLAS DE RUEDAS, CAMAS DE HOSPITAL, PORTERIAS ###########
######TO ADD!!!!!!!!!!!!!!!!!

# ---- ROW 2 (4 columns) ----
st.write("") # spacing vertical
col5, col6, col7, col8 = st.columns(4)

with col5:
    total_hospital = data_show["Hospital [-]"].sum()  
    card("images/hospital.png", f"{total_hospital} cajas de material de hospital",
         "Incluye cajas de material sanitario y equipos médicos (por ejemplo, máquinas médicas y andadores).")

with col6:
    total_sillas = data_show["Sillas de ruedas [-]"].sum()  
    card("images/sillas.png", f"{total_sillas} sillas de ruedas",
         "Número de sillas de ruedas enviadas.")

with col7:
    total_camas = data_show["Camas de hospital [-]"].sum()  
    card("images/camas.png", f"{total_camas} camas de hospital",
         "Número de camas de hospital enviadas.")
     
with col8:
    total_sewing = data_show["Maquinas de coser [-]"].sum()  
    card("images/costura.png", f"{total_sewing} máquinas de coser", 
         "Número de máquinas de coser enviadas, no incluye tela y otro material de costura.")
    
expander = st.expander("Otras donaciones")

with expander:

    # ---- ROW 1 ----
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_tools = data_show["Herramientas [-]"].sum()  
        card("images/tools.png", f"{total_tools} herramientas", 
             "Incluye cajas de herramientas y máquinas.") # measured in pallets or machines
             
    with col2:
        total_construction = data_show["Material de costruccion [-]"].sum()  
        card("images/construction.png", f"{total_construction} material de costrucción", 
             "Incluye materiales para la construcción como andamios, kits de iluminación, puertas y ventanas.")  

    with col3:
        total_solar = data_show["Solar [-]"].sum()  
        card("images/solar.png", f"{total_solar} instalaciónes fotovoltaicas", 
             "Número de instalaciónes fotovoltaicas enviadas, no encluye placas solares sueltas.")

    with col4:
        total_housestuff = data_show["Articulos de casa [-]"].sum()  
        card("images/house.png", f"{total_housestuff} articulos de casa", 
             "Incluye muebles, articulos de casa, electrodomesticos y otros.")
       

    # ---- ROW 2 ----
    st.write("") # spacing vertical
    col5, col6, col7, col8 = st.columns(4)

    with col5:
        total_toys = data_show["Juegos [-]"].sum()  
        card("images/toys.png", f"{total_toys} juegos", 
             "Incluye juegos, material deportivo y parques infantiles.")

    with col6:
        total_skates = data_show["Patines [-]"].sum()  
        card("images/skates.png", f"{total_skates} patines", 
             "Número de patines enviados.")

    with col7:
        total_porterias = data_show["Porterias de futbol [-]"].sum()  
        card("images/porterias.png", f"{total_porterias} porterias de futbol", 
             "Número de porterias de futbol enviadas.")
        
    with col8:
        total_school = data_show["Material escolar [-]"].sum()  
        card("images/school.png", f"{total_school} cajas de material escolar", 
             "Incluye libros, pupitres, sillas, pizarras y otro material.")
    
    # ---- ROW 3 ----
    st.write("") # spacing vertical
    col9, col10, col11, col12 = st.columns(4)
    with col9:
        total_cleaning = data_show["Limpieza y higiene [-]"].sum()  
        card("images/higiene.png", f"{total_cleaning} cajas de material de limpieza y higiene", 
             "Incluye pallets y cajas de material de limpieza y higiene.")

    with col10:
        total_others = data_show["Otro [-]"].sum()  
        card("images/others.png", f"{total_others} otro material", 
             "Incluye placas solares suelta, tela, equipos electrónicos, piezas de repuesto y todas las donacciones que no caben en una categoria especifica.")        

    with col11:
        pass
    with col12:
        pass



#%% MAPA DE ENVIOS
st.subheader('Mapa de envios')

# Group data by coordinates
data_show = data_show.copy()
data_show = data_show[data_show['coords'].notna()]
data_show['coords'] = data_show['coords'].apply(
    lambda x: tuple(x) if isinstance(x, list) else x)
grouped = data_show.groupby('coords')

# Plot map
m = folium.Map(location=[20, 0], zoom_start=2)

for coords, group in grouped:
    count = len(group)

    popup_lines = ""

    if count > 1:
        popup_lines = '<div style="font-size:12px;"><ul style="padding-left:15px; margin:0;">'
    
        for _, row in group.iterrows():
            popup_lines += f"""
            <li style="margin-bottom:5px;">
                <a href="{row['Enlace']}" target="_blank"
                   style="text-decoration:none; font-weight:bold;">
                    Contenedor {row['Numero Contenedor']}
                </a> a {row['Destino']} {str(row['Fecha'])[:10]}
            </li>
            """
    
        popup_lines += "</ul></div>"
    
    else:
        # single item → no bullet list
        row = group.iloc[0]
    
        popup_lines = f"""
        <div style="font-size:12px;">
            <a href="{row['Enlace']}" target="_blank"
               style="text-decoration:none; font-weight:bold;">
                Contenedor {row['Numero Contenedor']}
            </a> a {row['Destino']} {str(row['Fecha'])[:10]}
        </div>
        """
    # for _, row in group.iterrows():
    #     popup_lines += f"""
    #     <a href="{row['Enlace']}" target="_blank">
    #         Contenedor {row['Numero Contenedor']}
    #     </a> a {row['Destino']}<br>
    #     {str(row['Fecha'])[:10]}<br><br>
    #     """

    folium.Marker(
        location=list(coords),  # convert back to list for folium
        popup=folium.Popup(popup_lines, max_width=300),
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




#%% Display raw data as table
st.subheader('Datos')

raw_data_show = data_show.copy()
raw_data_show['Fecha'] = raw_data_show['Fecha'].dt.strftime('%d/%m/%Y')

st.write(raw_data_show.drop(['coords'], axis=1)) # this displays all kinds of data based on type
