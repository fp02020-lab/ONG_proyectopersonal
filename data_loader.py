# -*- coding: utf-8 -*-
"""
Created on Wed May  6 10:44:48 2026

Data loader and coordinates creator

@author: feder
"""

import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
import streamlit as st

#%% Cache: geocoding and data
# geolocator = Nominatim(user_agent="my_app", timeout=10 )
# @st.cache_data
# def get_coords(country):
#     import time
#     time.sleep(1)
#     location = geolocator.geocode(country)
#     return [location.latitude, location.longitude] if location else None
@st.cache_data
def get_coords():
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
    return coords_dict


@st.cache_data
def load_historical_data():
    ##### READ DATA
    data_history_contenedores = pd.read_excel("Historical_data_AC.xlsx", sheet_name= "All containers", engine="openpyxl")
    data_history_material = pd.read_excel("Historical_data_AC.xlsx", sheet_name= "Material", engine="openpyxl")

    ##### ENVIOS
    years = sorted(data_history_contenedores["Fecha"].dropna().unique())
    envios = []
    for year_i in years:
        envios.append(sum(data_history_contenedores["Fecha"] == year_i))
    df_contenedores = pd.DataFrame(data= {"Año": years, "Envíos": envios})

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
        
    ###### DATA for map
    data_map = data_history_contenedores.groupby(["Destino", "Fecha"]).size().reset_index(name="Numero Contenedores")
    data_map["Destino"] = data_map["Destino"].str.strip()
    return df_contenedores, datasets, data_map

@st.cache_data
def load_detailed_data(filename):
    # Load datas
    data_general = pd.read_excel(filename, engine="openpyxl")
    # fix reading dates 
    data_general['Fecha'] = pd.to_datetime(data_general['Fecha'], dayfirst=True, errors="coerce")

    # Add coordinates countries
    coords_dict = get_coords()
    data_general['coords'] = data_general['Destino'].map(coords_dict)
    
    
    #old way
    # unique_countries = data_general['Destino'].dropna().unique()
    # coords_dict = {c: get_coords(c) for c in unique_countries}
    # data_general['coords'] = data_general['Destino'].map(coords_dict)
    return data_general



