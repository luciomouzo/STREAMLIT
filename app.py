### TAREA MÓDULO 8 LUCIO ALEJANDRO MOUZO MONTEAGUDO

## Lo que vamos a realizar consiste en la opcion numero 3 de la Actividad Colaborativa, en la que vamos a haer Web Scrapping de una de las paginas y 
## finalizaremos con la utlizacion de streamlit para poder hacer la pagina web y filtrar jugadores y momentos de cada uno de los jugadores.
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests
import os
import time

### 1. CREACIÓN DE LA APLICACIÓN WEB CON STREAMLIT

# Configuración inicial
st.set_page_config(page_title="Aplicación Deportiva", layout="wide")


# Configuración inicial para la API
api_key = os.getenv("FOOTBALL_DATA_API_KEY", "2b4bfa139edd4579bb1f791da1bcc3b4")
headers = {"X-Auth-Token": api_key}


# Estado de sesión
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Función de Login
def login():
    st.title("Iniciar Sesión")
    username = st.text_input("Usuario", key="username_input")
    password = st.text_input("Contraseña", type="password", key="password_input")
    if st.button("Ingresar"):
        if username == "admin" and password == "admin":
            st.session_state["logged_in"] = True
            st.success("Inicio de sesión exitoso")
        else:
            st.error("Usuario o contraseña incorrectos. Intenta nuevamente.")

# Función para obtener las ligas por webscraping
def obtener_datos_webscraping(headers, guardar_csv=True):
    # Obtener todas las ligas
    url_ligas = "https://api.football-data.org/v4/competitions"
    response_ligas = requests.get(url_ligas, headers=headers, timeout=10)
    
    if response_ligas.status_code != 200:
        st.error(f"Error {response_ligas.status_code}: {response_ligas.text}")
        return pd.DataFrame()
    
    # Filtrar ligas nacionales y excluir selecciones
    ligas = [
        liga for liga in response_ligas.json().get('competitions', [])
        if liga.get('type') == "LEAGUE" and liga['name'] not in ["European Championship", "FIFA World Cup"]
    ]
    
    clasificaciones = pd.DataFrame()

    # Iterar sobre cada liga y obtener su clasificación
    for liga in ligas:
        liga_id = liga['id']
        url_clasificacion = f"https://api.football-data.org/v4/competitions/{liga_id}/standings"
        
        for intento in range(3):  # Reintentos en caso de fallo
            try:
                response_clasificacion = requests.get(url_clasificacion, headers=headers, timeout=10)
                if response_clasificacion.status_code == 200:
                    standings_data = response_clasificacion.json()
                    if 'standings' in standings_data and standings_data['standings']:
                        standings = standings_data['standings'][0]['table']
                        clasificacion_df = pd.DataFrame([{
                            'Equipo': team['team']['name'],
                            'Liga': standings_data['competition']['name'],
                            'Posición': team['position'],
                            'Puntos': team['points'],
                            'Partidos Jugados': team['playedGames'],
                            'Ganados': team['won'],
                            'Empatados': team['draw'],
                            'Perdidos': team['lost'],
                            'Goles a Favor': team['goalsFor'],
                            'Goles en Contra': team['goalsAgainst'],
                            'Diferencia de Goles': team['goalDifference']
                        } for team in standings])

                        clasificaciones = pd.concat([clasificaciones, clasificacion_df], ignore_index=True)
                        break  # Salir del bucle de reintentos si tiene éxito
                    else:
                        st.warning(f"No se encontraron datos de clasificación para la liga {liga['name']}")
                else:
                    st.warning(f"Error {response_clasificacion.status_code} al obtener datos de la liga {liga['name']}")
            except requests.exceptions.RequestException as e:
                st.warning(f"Error en la solicitud para la liga {liga['name']}: {e}")
                time.sleep(2)
        
        # Respetar los límites de la API
        time.sleep(5)

    # Procesar datos
    if not clasificaciones.empty:
        clasificaciones['Efectividad'] = (clasificaciones['Puntos'] / (clasificaciones['Partidos Jugados'] * 3))
        clasificaciones['Promedio Goles a Favor'] = clasificaciones['Goles a Favor'] / clasificaciones['Partidos Jugados']
        clasificaciones['Promedio Goles en Contra'] = clasificaciones['Goles en Contra'] / clasificaciones['Partidos Jugados']
        clasificaciones['Diferencia de Goles por Partido'] = clasificaciones['Diferencia de Goles'] / clasificaciones['Partidos Jugados']

        # Guardar en CSV si se solicita
        if guardar_csv:
            clasificaciones.to_csv('clasificacion_ligas_procesadas.csv', index=False)
            st.success("Datos guardados en 'clasificacion_ligas_procesadas.csv'.")

    return clasificaciones


# Función de comparación dentro de una misma Liga
def comparacion_dentro_liga(df):
    st.title("Comparación dentro de una Liga")
    
    # Seleccionar liga
    ligas = df["Liga"].unique()
    seleccion_liga = st.selectbox("Selecciona una Liga:", ligas)
    
    if seleccion_liga:
        df_liga = df[df["Liga"] == seleccion_liga]
        
        # Tabla personalizada
        st.subheader(f"Tabla de Clasificación - {seleccion_liga}")
        columnas_disponibles = df_liga.columns.tolist()
        columnas_seleccionadas = st.multiselect(
            "Selecciona las columnas que quieres visualizar:",
            options=columnas_disponibles,
            default=columnas_disponibles
        )
        st.dataframe(df_liga[columnas_seleccionadas])
        
        # Gráfico de dispersión
        st.subheader("Gráfico de Dispersión")
        x_columna = st.selectbox("Selecciona la columna para el eje X:", options=df_liga.columns)
        y_columna = st.selectbox("Selecciona la columna para el eje Y:", options=df_liga.columns)
        fig, ax = plt.subplots()
        ax.scatter(df_liga[x_columna], df_liga[y_columna], alpha=0.7)
        ax.set_title(f"{x_columna} vs {y_columna}")
        ax.set_xlabel(x_columna)
        ax.set_ylabel(y_columna)
        st.pyplot(fig)
        
        # Radar plot
        st.subheader("Radar Plot Comparativo")
        equipos_seleccionados = st.multiselect(
            "Selecciona los equipos para comparar:",
            options=df_liga["Equipo"].unique(),
            default=df_liga["Equipo"].unique()[:3]
        )
        columnas_radar = st.multiselect(
            "Selecciona las métricas para el radar:",
            options=[col for col in df_liga.columns if df_liga[col].dtype in ['int64', 'float64']],
            default=[col for col in df_liga.columns if df_liga[col].dtype in ['int64', 'float64']][:5]
        )

        if equipos_seleccionados and columnas_radar:
            df_radar = df_liga[df_liga["Equipo"].isin(equipos_seleccionados)][["Equipo"] + columnas_radar]
            df_radar.set_index("Equipo", inplace=True)

            num_vars = len(columnas_radar)
            angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
            angles += angles[:1]

            fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
            for equipo in df_radar.index:
                valores = df_radar.loc[equipo].values.flatten().tolist()
                valores += valores[:1]
                ax.plot(angles, valores, label=equipo)
                ax.fill(angles, valores, alpha=0.25)

            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(columnas_radar)
            ax.legend(loc="upper right", bbox_to_anchor=(1.1, 1.1))
            st.pyplot(fig)


# Función de comparación entre ligas
def comparacion_entre_equipos(df):
    st.title("Comparación entre Equipos de Distintas Ligas")

    # Filtrar solo las columnas numéricas
    columnas_numericas = df.select_dtypes(include=['int64', 'float64']).columns

    # Seleccionar equipos
    equipos_seleccionados = st.multiselect(
        "Selecciona los equipos para comparar:",
        options=df["Equipo"].unique(),
        default=df["Equipo"].unique()[:3]  # Mostrar los 3 primeros por defecto
    )

    # Seleccionar métricas para comparar
    columnas_seleccionadas = st.multiselect(
        "Selecciona las métricas para la comparación:",
        options=columnas_numericas,
        default=columnas_numericas[:5]
    )

    # Filtrar el DataFrame
    if equipos_seleccionados and columnas_seleccionadas:
        df_comparacion = df[df["Equipo"].isin(equipos_seleccionados)][["Equipo", "Liga"] + columnas_seleccionadas]
        st.subheader("Tabla Comparativa de Equipos")
        st.dataframe(df_comparacion)

        # Gráfico de dispersión
        st.subheader("Gráfico de Dispersión entre Equipos")
        x_columna = st.selectbox("Selecciona la columna para el eje X:", options=columnas_seleccionadas)
        y_columna = st.selectbox("Selecciona la columna para el eje Y:", options=columnas_seleccionadas)
        
        fig, ax = plt.subplots()
        for equipo in equipos_seleccionados:
            datos_equipo = df_comparacion[df_comparacion["Equipo"] == equipo]
            ax.scatter(
                datos_equipo[x_columna],
                datos_equipo[y_columna],
                label=equipo,
                s=100  # Tamaño de los puntos
            )
            ax.text(
                datos_equipo[x_columna].values[0],
                datos_equipo[y_columna].values[0],
                equipo,
                fontsize=9,
                ha="right"
            )
        ax.set_title(f"{x_columna} vs {y_columna} (Comparación entre Equipos)")
        ax.set_xlabel(x_columna)
        ax.set_ylabel(y_columna)
        ax.legend(title="Equipos")
        st.pyplot(fig)

        # Crear el radar plot
        st.subheader("Radar Plot Comparativo")
        df_radar = df_comparacion.set_index("Equipo")[columnas_seleccionadas]
        num_vars = len(columnas_seleccionadas)
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        for equipo in df_radar.index:
            valores = df_radar.loc[equipo].values.flatten().tolist()
            valores += valores[:1]
            ax.plot(angles, valores, label=equipo)
            ax.fill(angles, valores, alpha=0.25)

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(columnas_seleccionadas)
        ax.legend(loc="upper right", bbox_to_anchor=(1.1, 1.1))
        st.pyplot(fig)

    else:
        st.warning("Selecciona al menos un equipo y una métrica para generar la comparación.")



# Función principal
def main():

    def login():
        st.title("Iniciar Sesión")
        username = st.text_input("Usuario", key="username_input")
        password = st.text_input("Contraseña", type="password", key="password_input")
        if st.button("Ingresar"):
            if username == "admin" and password == "admin":
                st.session_state["logged_in"] = True
                st.success("Inicio de sesión exitoso")
            else:
                st.error("Usuario o contraseña incorrectos. Intenta nuevamente.")

    if st.session_state["logged_in"]:
        st.sidebar.title("Menú de Navegación")
        opciones = [
            "Inicio",
            "Actualizar Datos",
            "Visualizar Ligas",
            "Comparación dentro de una Liga",
            "Comparación entre Ligas",
            "Cerrar Sesión"
        ]
        eleccion = st.sidebar.radio("Selecciona una opción", opciones)

        if eleccion == "Inicio":
            st.title("Bienvenido a la Aplicación Deportiva")
            st.write("Navega por el menú para explorar las funcionalidades.")
            if st.button("Limpiar caché"):
                st.cache_data.clear()
                st.success("Caché limpiado correctamente.")

        elif eleccion == "Actualizar Datos":
            st.title("Actualizando datos desde la API...")
            with st.spinner("Obteniendo datos..."):
                datos = obtener_datos_webscraping(headers)
                if not datos.empty:
                    st.success("Datos actualizados correctamente.")
                    st.dataframe(datos)
                    st.cache_data.clear() #Se utiliza para limpiar el caché después de actualizar los datos
                else:
                    st.error("No se pudieron obtener los datos desde la API.")

        elif eleccion == "Visualizar Ligas":
                df = pd.read_csv('clasificacion_ligas_procesadas.csv')
                ligas = df["Liga"].unique()
                seleccion = st.selectbox("Selecciona una liga para visualizar", ligas)
                if seleccion:
                    st.write(f"Mostrando datos para la liga: {seleccion}")
                    st.dataframe(df[df["Liga"] == seleccion])
        elif eleccion == "Comparación dentro de una Liga":
                df = pd.read_csv('clasificacion_ligas_procesadas.csv')
                comparacion_dentro_liga(df)

        elif eleccion == "Comparación entre Ligas":
                df = pd.read_csv('clasificacion_ligas_procesadas.csv')
                comparacion_entre_equipos(df)
           
        elif eleccion == "Cerrar Sesión":
            st.session_state["logged_in"] = False
            st.experimental_rerun()
    else:
        login()


# Ejecutar la aplicación
if __name__ == "__main__":
    main()




#python -m streamlit run app.py
