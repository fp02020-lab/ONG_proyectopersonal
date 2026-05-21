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
import numpy as np
import altair as alt

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

#%% PAGE 1 - DATOS HISTORICOS
from data_loader import load_historical_data

page = st.sidebar.selectbox("Go to", ["Envíos historicos", "Material enviado"])

if page == "Envíos historicos":
    st.title('Ayuda Contenedores impacto')
    # Load data
    df_contenedores, datasets, data_map = load_historical_data()

    # Envios por año - histogramma y mapa
    st.subheader('📊 Histórico de envíos por año')
    total_contenedores = df_contenedores["Envíos"].sum()
    st.metric("Total contenedores", total_contenedores)
    # st.bar_chart(df_contenedores.set_index("Año"), color="#4CAF50") # BAR CHART IS LIMITED, no formatting allowed
    chart = alt.Chart(df_contenedores).mark_bar(color="#4CAF50").encode(
        x=alt.X(
            "Año:O",
            axis=alt.Axis(labelFontSize=16, titleFontSize=18) ),
        y=alt.Y(
            "Envíos:Q",
            axis=alt.Axis(labelFontSize=16, titleFontSize=18))
    ).properties(width=700, height=400)
    
    st.altair_chart(chart, use_container_width=True)



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
            )).add_to(m)
    
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

    chart = alt.Chart(df_selected).mark_bar(color="#4CAF50").encode(
        x=alt.X(
            "Año:O",
            axis=alt.Axis(labelFontSize=16, titleFontSize=18) ),
        y=alt.Y(
            "Envíos:Q",
            axis=alt.Axis(labelFontSize=16, titleFontSize=18))
    ).properties(width=700, height=400)
    
    st.altair_chart(chart, use_container_width=True)

#%% PAGE 2 - MATERIAL ENVIADO
elif page == "Material enviado":
    st.title('Ayuda Contenedores impacto')
    
    ### NEW VERSION
    from data_loader import load_detailed_data
    data_general = load_detailed_data("tabla_publica__18_05_2026.xlsx")
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
            
            
    st.sidebar.markdown(
        """
        <div style='font-size:11px; color:#888888; font-style:italic;'>
        Nota: solo están disponibles los datos detallados de los contenedores posteriores al año 2025.
        </div>
        """,
        unsafe_allow_html=True
    )
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
    st.markdown("<div style='height:25px;'></div>", unsafe_allow_html=True) # spacing vertical
    
    # Calculate and display totals
    
    def get_base64(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    
    def card(img_path, text, info):
        img_base64 = get_base64(img_path)
    
        st.markdown(f"""
            <div style="
                    text-align:center;
                    height:170px;
                    display:flex;
                    flex-direction:column;
                    justify-content:center;
                    align-items:center;
                    margin-bottom:30px;
                    padding:10px;
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
    st.markdown("<div style='height:25px;'></div>", unsafe_allow_html=True) # spacing vertical
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
        
    st.markdown("<div style='margin-top:40px;'></div>", unsafe_allow_html=True)
    expander = st.expander("Otras donaciones")
    
    with expander:
        st.markdown("""
        <style>
        div[data-testid="stExpander"] details div[role="group"] {
            padding-top: 20px;
            padding-left: 15px;
            padding-right: 15px;
            padding-bottom: 10px;
        }
        </style>
        """, unsafe_allow_html=True)
    
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
        st.markdown("<div style='height:25px;'></div>", unsafe_allow_html=True) # spacing vertical
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
        st.markdown("<div style='height:25px;'></div>", unsafe_allow_html=True) # spacing vertical
        col9, col10, col11, col12 = st.columns(4)
        with col9:
            total_cleaning = data_show["Limpieza y higiene [-]"].sum()  
            card("images/higiene.png", f"{total_cleaning} material de limpieza y higiene", 
                 "Incluye pallets y cajas de material de limpieza y higiene.")
    
        with col10:
            total_others = data_show["Otro [-]"].sum()  
            card("images/others.png", f"{total_others} otro material", 
                 "Incluye todas las donacciones que no caben en una categoria especifica.")        
    
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
            # location=[group["Latitud"].iloc[0], group["Longitud"].iloc[0]],
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
    st.subheader('Datos seleccionados')
    
    raw_data_show = data_show.copy()
    raw_data_show['Fecha'] = raw_data_show['Fecha'].dt.strftime('%d/%m/%Y')
    
    st.write(raw_data_show.drop(['coords'], axis=1)) # this displays all kinds of data based on type





