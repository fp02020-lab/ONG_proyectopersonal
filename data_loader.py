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
    df_coords = pd.read_excel("tabla_publica__18_05_2026.xlsx", sheet_name= "Destinos", engine="openpyxl")
    coords_dict = {
        row['Destino']: [row['Latitud'], row['Longitud']]
        for _, row in df_coords.iterrows()}
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
    # normalized_coords = {
    #     normalize_country(k): v
    #     for k, v in coords_dict.items() }
    # data_general['coords'] = (
    #     data_general['Destino']
    #     .apply(normalize_country)
    #     .map(normalized_coords) )
    data_general['coords'] = data_general['Destino'].map(coords_dict) 
    data_general = data_general.sort_values(by=["Numero Contenedor"]) # sort numero contenedor
    data_general = data_general.reset_index(drop=True)
    return data_general



# import unicodedata
# import re

# def normalize_country(text):
#     if not isinstance(text, str):
#         return text

#     # lowercase
#     text = text.lower()

#     # remove accents
#     text = unicodedata.normalize('NFKD', text)
#     text = ''.join(c for c in text if not unicodedata.combining(c))

#     # remove extra spaces
#     text = re.sub(r'\s+', ' ', text).strip()

#     return text