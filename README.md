# STREAMLIT
Tarea de máster relacionada con Streamlit

1. Título del proyecto
Aplicación deportiva con Streamlit

2. Descripción del proyecto
Esta aplicación permite visualizar y comparar estadísticas de diferentes ligas de fútbol utilizando Streamlit, realizando la actualización de datos mediante Web Scraping, comparación dentro de una liga y comparación entre equipos de diferentes ligas.

3. Demostración de la aplicación
La aplicación está disponible en el siguiente enlace https://app-mzwyggvsu5puuk4hyjwc6x.streamlit.app/

4. Requisitos previos
Los requisitos previos que se necesitan son Python 3.8, cuenta en GitHub y acceso a una API de fútbol. Y se debe tener 'pip' instalado para manejar las dependencias.

5. Instalación y configuración
Se añade esto en el bash:   
 git clone https://github.com/luciomouzo/STREAMLIT.git
 cd STREAMLIT

6. Configuración de la API key
FOOTBALL_DATA_KEY

7. Estructura del proyecto
.streamlit -> configuración específica para streamlit
data -> Archivos de datos csv
models -> funciones de Web Scrapping
controllers -> funciones de análisis y visualización
common -> funciones auxiliares compartidas
app.py -> archivo principal de la aplicación
.env -> vriables de entorno con la API Key
requirements.txt -> librerías necesarias
README.md -> documentación del proyecto

8. Uso de la aplicación
**Inicio**: Página de bienvenida.
**Actualizar datos**: Permite obtener los últimos datos mediante la API.
**Visualizar ligas**: Explora estadísticas por liga.
**Comparación dentro de una liga**: Compara equipos de una misma liga.
**Comparación entre ligas**: Compara equipos de diferentes ligas.

9. Tecnologías utilizadas
**Streamlit**: Para la interfaz web.
**Pandas**: Manipulación y análisis de datos. 
**Matplotlib**: Visualización de datos. 
**Numpy**: Cálculos numéricos.
**Requests**: Acceso a la API de fútbol.

10. Autor
**Lucio Alejandro Mouzo Monteagudo**
