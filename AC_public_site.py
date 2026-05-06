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
coords_dict = {
    "Angola": [-8.8390, 13.2894],
    "Argelia": [28.0339, 1.6596],
    "Benin": [9.3077, 2.3158],
    "Burquina Faso": [12.2383, -1.5616],
    "Burundi": [-3.3731, 29.9189],
    "Cabo Verde": [16.5388, -23.0418],
    "Camerun": [7.3697, 12.3547],
    "Congo": [-0.2280, 15.8277],  # Republic of Congo (Brazzaville)
    "Cuba": [21.5218, -77.7812],
    "España": [40.4637, -3.7492],
    "Etiopia": [9.1450, 40.4897],
    "Gambia": [13.4432, -15.3101],
    "Ghana": [7.9465, -1.0232],
    "Grecia": [39.0742, 21.8243],
    "Guatemala": [15.7835, -90.2308],
    "Guinea": [9.9456, -9.6966],
    "Guinea Bisau": [11.8037, -15.1804],
    "Guinea Ecuatorial": [1.6508, 10.2679],
    "Honduras": [15.2000, -86.2419],
    "India": [20.5937, 78.9629],
    "Kenia": [-0.0236, 37.9062],
    "Libano": [33.8547, 35.8623],
    "Liberia": [6.4281, -9.4295],
    "Madagascar": [-18.7669, 46.8691],
    "Malawi": [-13.2543, 34.3015],
    "Mali": [17.5707, -3.9962],
    "Mozambique": [-18.6657, 35.5296],
    "Palestine": [31.9522, 35.2332],
    "Perú": [-9.1900, -75.0152],
    "Republica Centroafricana": [6.6111, 20.9394],
    "Republica Democratica del Congo": [-4.0383, 21.7587],
    "Republica Dominicana": [18.7357, -70.1627],
    "Senegal": [14.4974, -14.4524],
    "Sierra Leona": [8.4606, -11.7799],
    "Siria": [34.8021, 38.9968],
    "Tanzania": [-6.3690, 34.8888],
    "Togo": [8.6195, 0.8248],
    "Ucrania": [48.3794, 31.1656],
    "Uganda": [1.3733, 32.2903],
    "Uruguay": [-32.5228, -55.7658],
    "Venezuela": [6.4238, -66.5897],
    "Vietnam": [14.0583, 108.2772]
}
# geolocator = Nominatim(user_agent="my_app")

# coords_cache = {}

# def get_coords(country):
#     if country in coords_cache:
#         return coords_cache[country]

#     try:
#         location = geolocator.geocode(country)

#         if location:
#             coords_cache[country] = [location.latitude, location.longitude]
#         else:
#             coords_cache[country] = None

#     except:
#         coords_cache[country] = None

    # return coords_cache[country]

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
    data_map["coords"] = data_map["Destino"].map(coords_dict)
    data_map = data_map.dropna(subset=["coords"])
    grouped = data_map.groupby("Destino")
    m = folium.Map(location=[20, 0], zoom_start=2)
    for destino, group in grouped:
    
        coords = group["coords"].iloc[0]
        total = group["Numero Contenedores"].sum()
    
        # popup content (breakdown by year)
        popup_lines = f"""{destino} <div style="font-size:12px;"><ul style="padding-left:15px; margin:0;">"""
    
        for _, row in group.iterrows():
            popup_lines += f"""
            <li>{row['Numero Contenedores']} contenedores en {int(row['Fecha'])}</li>
            """
    
        popup_lines += "</ul></div>"
    
        # marker
        folium.Marker(
            location=coords,
            popup=folium.Popup(popup_lines, max_width=300),
            icon=DivIcon(
                html=f"""
                <div style="
                    background-color:green;
                    border-radius:50%;
                    width:32px;
                    height:32px;
                    text-align:center;
                    color:white;
                    font-weight:bold;
                    line-height:32px;
                    font-size:12px;">
                    {total}
                </div>
                """
            )
        ).add_to(m)
    
    # render in Streamlit
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




