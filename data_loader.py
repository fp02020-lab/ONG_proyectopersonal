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
geolocator = Nominatim(user_agent="my_app")
@st.cache_data
def get_coords(country):
    location = geolocator.geocode(country)
    return [location.latitude, location.longitude] if location else None

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
    
    return df_contenedores, datasets, data_map

@st.cache_data
def load_detailed_data(filename):
    # Load datas
    data_general = pd.read_excel(filename, engine="openpyxl")
    # fix reading dates 
    data_general['Fecha'] = pd.to_datetime(data_general['Fecha'], dayfirst=True, errors="coerce")

    # Add coordinates countries
    unique_countries = data_general['Destino'].dropna().unique()
    coords_dict = {c: get_coords(c) for c in unique_countries}
    data_general['coords'] = data_general['Destino'].map(coords_dict)
    return data_general



