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



#%% GEOCACHE MANUALLY
geolocator = Nominatim(user_agent="my_app")

coords_cache = {}

def get_coords(country):
    if country in coords_cache:
        return coords_cache[country]

    try:
        location = geolocator.geocode(country)

        if location:
            coords_cache[country] = [location.latitude, location.longitude]
        else:
            coords_cache[country] = None

    except:
        coords_cache[country] = None

    return coords_cache[country]

#%%
from pages import page1
from data_loader import load_historical_data

st.set_page_config(page_title="Envíos historicos")

page = st.sidebar.selectbox("Go to", ["Envíos historicos", "Material enviado"])

if page == "Envíos historicos":
    st.title('Ayuda Contenedores impacto')
    # Load data
    df_contenedores, datasets, data_map = load_historical_data()

    # Envios por año - histogramma y mapa
    st.subheader('📊 Histórico de envíos por año')
    total_contenedores = df_contenedores["Envíos"].sum()
    st.metric("Total contenedores", total_contenedores)
    st.bar_chart(df_contenedores.set_index("Año"), color="#4CAF50")



    # Plot map
    data_show_map = data_map.copy()
    data_show_map = data_show_map[data_show_map['coords'].notna()]
    data_show_map['coords'] = data_show_map['coords'].apply(
        lambda x: tuple(x) if isinstance(x, list) else x)
    grouped = data_show_map.groupby('coords')
    
    # Plot map
    m = folium.Map(location=[20, 0], zoom_start=2)
    for coords, group in grouped:
        total = group["Numero Contenedores"].sum() #total contenedores in a region
        
        
        ###### fix from here popup
        count = len(group)
    
        popup_lines = '<div style="font-size:12px;"><ul style="padding-left:15px; margin:0;">'
    
        for _, row in group.iterrows():
            popup_lines += f"""
            <li style="margin-bottom:5px;">
                <a href="{row['Enlace']}" target="_blank"
                   style="text-decoration:none; font-weight:bold;">
                    Contenedor {row['Numero Contenedor']}
                </a> a {row['Destino']} {str(row['Fecha'])}
            </li>
            """
    
        popup_lines += "</ul></div>"
    
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
            ) ).add_to(m)
    
    st_folium(m, width=700, height=500)
    
    
    
    
    # # ADD COORDINATES
    # unique_countries = data_map["Destino"].dropna().unique()

    # coords_dict = {
    #     country: get_coords(country)
    #     for country in unique_countries  }

    # data_map["coords"] = data_map["Destino"].map(coords_dict)

    # # remove missing coords
    # data_map = data_map.dropna(subset=["coords"])
    # #################
    
    
    # grouped = data_map.groupby("Destino")

    # m = folium.Map(location=[20, 0], zoom_start=2)

    # for destino, group in grouped:

    #     coords = group["coords"].iloc[0]
    #     total = group["Numero Contenedores"].sum()

    #     popup_lines = '<div style="font-size:12px;"><ul style="padding-left:15px; margin:0;">'

    #     for _, row in group.iterrows():
    #         popup_lines += f"""
    #         <li>
    #             {row['Numero Contenedores']} contenedores en {int(row['Fecha'])}
    #         </li>
    #         """

    #     popup_lines += "</ul></div>"

    #     folium.Marker(
    #         location=coords,
    #         popup=folium.Popup(popup_lines, max_width=300),
    #         icon=DivIcon(
    #             html=f"""
    #             <div style="
    #                 background-color:green;
    #                 border-radius:50%;
    #                 width:30px;
    #                 height:30px;
    #                 text-align:center;
    #                 color:white;
    #                 font-weight:bold;
    #                 line-height:30px;">
    #                 {total}
    #             </div>
    #             """
    #         )
    #     ).add_to(m)
    
    # st_folium(m, width=700, height=500)











    # Envios de material
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




