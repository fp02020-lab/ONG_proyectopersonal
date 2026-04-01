# -*- coding: utf-8 -*-
"""
Created on Fri Feb 27 08:36:56 2026
STREAMLIT WEBSITE script
@author: feder
"""


import streamlit as st
import pandas as pd
import numpy as np

#%%
st.title('Ayuda Contenedores impacto')
#%%
# Load datas
data_general = pd.read_excel("testfile.xlsx")
# fix reading dates 
data_general['Fecha'] = pd.to_datetime(data_general['Fecha'], dayfirst=True, errors="coerce")
start_year = data_general['Fecha'].min().year #.strftime("%Y")
end_year = data_general['Fecha'].max().year #.strftime("%Y")

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
    options = st.sidebar.multiselect(
        "Cuales año(s)?",
        list(range(start_year, end_year+1))
    )
    st.write("You selected:", options)
    
    
elif time_range == "Especifica periodo":
    # i want to specify full date
    pass
else:
    pass
    #take all df
    



