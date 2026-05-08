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
# coords_dict = {
#     "Angola": [-8.8390, 13.2894],
#     "Argelia": [28.0339, 1.6596],
#     "Benin": [9.3077, 2.3158],
#     "Burquina Faso": [12.2383, -1.5616],
#     "Burundi": [-3.3731, 29.9189],
#     "Cabo Verde": [16.5388, -23.0418],
#     "Camerun": [7.3697, 12.3547],
#     "Congo": [-0.2280, 15.8277],  # Republic of Congo (Brazzaville)
#     "Cuba": [21.5218, -77.7812],
#     "España": [40.4637, -3.7492],
#     "Etiopia": [9.1450, 40.4897],
#     "Gambia": [13.4432, -15.3101],
#     "Ghana": [7.9465, -1.0232],
#     "Grecia": [39.0742, 21.8243],
#     "Guatemala": [15.7835, -90.2308],
#     "Guinea": [9.9456, -9.6966],
#     "Guinea Bisau": [11.8037, -15.1804],
#     "Guinea Ecuatorial": [1.6508, 10.2679],
#     "Honduras": [15.2000, -86.2419],
#     "India": [20.5937, 78.9629],
#     "Kenia": [-0.0236, 37.9062],
#     "Libano": [33.8547, 35.8623],
#     "Liberia": [6.4281, -9.4295],
#     "Madagascar": [-18.7669, 46.8691],
#     "Malawi": [-13.2543, 34.3015],
#     "Mali": [17.5707, -3.9962],
#     "Mozambique": [-18.6657, 35.5296],
#     "Palestine": [31.9522, 35.2332],
#     "Perú": [-9.1900, -75.0152],
#     "Republica Centroafricana": [6.6111, 20.9394],
#     "Republica Democratica del Congo": [-4.0383, 21.7587],
#     "Republica Dominicana": [18.7357, -70.1627],
#     "Senegal": [14.4974, -14.4524],
#     "Sierra Leona": [8.4606, -11.7799],
#     "Siria": [34.8021, 38.9968],
#     "Tanzania": [-6.3690, 34.8888],
#     "Togo": [8.6195, 0.8248],
#     "Ucrania": [48.3794, 31.1656],
#     "Uganda": [1.3733, 32.2903],
#     "Uruguay": [-32.5228, -55.7658],
#     "Venezuela": [6.4238, -66.5897],
#     "Vietnam": [14.0583, 108.2772]
# }
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
# from pages import page1
# from page1 import render
from data_loader import load_historical_data

# st.set_page_config(page_title="Envíos historicos")

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
    st.subheader("📍 Mapa de envíos")
    ## 1. select timeperiod
    years = sorted(data_map["Fecha"].dropna().unique())

    min_year = int(min(years))
    max_year = int(max(years))
    
    start_year, end_year = st.slider(
        "Selecciona periodo de años",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year))
    filtered_data = data_map[
        (data_map["Fecha"] >= start_year) &
        (data_map["Fecha"] <= end_year)]

    st.metric("Total contenedores", filtered_data["Numero Contenedores"].sum())
    
    ## 2. Plot  
    from data_loader import get_coords
    coords_dict = get_coords()
    filtered_data["coords"] = filtered_data["Destino"].map(coords_dict)
    filtered_data = filtered_data.dropna(subset=["coords"])
    grouped = filtered_data.groupby("Destino")
    m = folium.Map(location=[20, 0], zoom_start=2)
    for destino, group in grouped:
    
        coords = group["coords"].iloc[0]
        total = group["Numero Contenedores"].sum()
    
        # popup content (breakdown by year)
        popup_lines = f"""
            <div style="font-size:12px;">
                <b>{destino}</b>
                <ul style="padding-left:15px; margin:0;">
            """
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
    # render()   
    #%% IMPORT PACKAGES
    import streamlit as st
    import pandas as pd
    import datetime
    import base64
    from streamlit_folium import st_folium
    import folium
    from folium.features import DivIcon
    
    
    
    #%%
    st.title('Ayuda Contenedores impacto')
    
    ### NEW VERSION
    from data_loader import load_detailed_data
    data_general = load_detailed_data("tabla_publica__TEST.xlsx")
    start_year = data_general['Fecha'].min().year #.strftime("%Y")
    end_year = data_general['Fecha'].max().year #.strftime("%Y")
    
    
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
       
    #%% MATERIAL ENVIADO - CARDS -
    st.subheader('📦 Material enviado')
    
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
                <div style="font-size:17px; margin-top:20px; font-weight:bold;">
                    {text}
                    <details style="display:inline;">
                            <summary style="
                                display:inline;
                                cursor:pointer;
                                margin-left:5px;
                                font-size:10px;
                                background:#eee;
                                border-radius:50%;
                                padding:2px 6px;
                            ">?</summary>
                            <div style="font-size:12px; margin-top:5px; font-weight:normal;">
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
             f"{total_bicis} bicicletas",
             "Número de bicicletas enviadas, no incluye las piezas de repuesto.")
    
    with col2:
        total_pcs = data_show["Ordenadores [-]"].sum()
        card("images/computer.png", f"{total_pcs} ordenadores",
             "Número de ordenadores enviados, no incluye otros dispositivos electrónicos.")
    
    with col3:
        total_food = data_show["Comida [tons]"].sum()
        card("images/food.png", f"{total_food/1000:.1f}ton de comida", 
             "Toneladas de alimentos enviadas.")
    
    with col4:
        total_clothes = data_show["Ropa [-]"].sum()  
        card("images/clothes.png", f"{total_clothes} ropa", 
             "Incluye cajas de ropa, bolsas, zapatos, ropa de seguridad y complementos.")
    
    # ---- ROW 2 (4 columns) ----
    st.write("") # spacing vertical
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        total_hospital = data_show["Hospital [-]"].sum()  
        card("images/hospital.png", f"{total_hospital} material de hospital",
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
            card("images/porterias.png", f"{total_porterias} porterias de fútbol", 
                 "Número de porterias de fútbol enviadas.")
            
        with col8:
            total_school = data_show["Material escolar [-]"].sum()  
            card("images/school.png", f"{total_school} cajas de material escolar", 
                 "Incluye libros, pupitres, sillas, pizarras y otro material.")
        
        # ---- ROW 3 ----
        st.write("") # spacing vertical
        col9, col10, col11, col12 = st.columns(4)
        with col9:
            total_cleaning = data_show["Limpieza y higiene [-]"].sum()  
            card("images/higiene.png", f"{total_cleaning} articulos de limpieza y higiene", 
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
    st.subheader('📍 Mapa de envios')
    
    # Group data by coordinates
    data_show = data_show.copy()    
    data_show = data_show.dropna(subset=["coords"])  # remove unmatched cases 
    grouped = data_show.groupby('Destino') # group by location
    
    # Plot map
    m = folium.Map(location=[20, 0], zoom_start=2)
    
    for destino, group in grouped:
        count = len(group)
        coords = group["coords"].iloc[0]
    
        popup_lines = ""
    
        if count > 15:
            popup_lines = f"""
            <div style="font-size:12px;">
                <b>{destino}</b><br>
            """
        
            containers = []
        
            for _, row in group.iterrows():
        
                year = str(row['Fecha'])[:4]
        
                containers.append(
                    f"""
                    <a href="{row['Enlace']}" target="_blank"
                       style="text-decoration:none; font-weight:bold;">
                        {row['Numero Contenedor']}
                    </a> ({year})
                    """ )
        
            popup_lines += "Contenedor " + ", ".join(containers)
            popup_lines += "</div>"
        
        
        elif count > 1:
            popup_lines = f'''
            <div style="font-size:12px;">
                <ul style="padding-left:15px; margin:0;">
                    <b>{destino}</b>
            '''
        
            for _, row in group.iterrows():
                popup_lines += f"""
                <li style="margin-bottom:5px;">
                    <a href="{row['Enlace']}" target="_blank"
                       style="text-decoration:none; font-weight:bold;">
                        Contenedor {row['Numero Contenedor']}
                    </a> {str(row['Fecha'])[:10]}
                </li>
                """
        
            popup_lines += "</ul></div>"
        
        
        else:
            row = group.iloc[0]
        
            popup_lines = f"""
            <div style="font-size:12px;">
                <b>{destino}</b><br>
                <a href="{row['Enlace']}" target="_blank"
                   style="text-decoration:none; font-weight:bold;">
                    Contenedor {row['Numero Contenedor']}
                </a> {str(row['Fecha'])[:10]}
            </div>
            """
        
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
            )).add_to(m)
    
    st_folium(m, width=700, height=500)
    
    
    #%% Display raw data as table
    st.subheader('Datos')
    
    raw_data_show = data_show.copy()
    raw_data_show['Fecha'] = raw_data_show['Fecha'].dt.strftime('%d/%m/%Y')
    
    st.write(raw_data_show.drop(['coords'], axis=1)) # this displays all kinds of data based on type





