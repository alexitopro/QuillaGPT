import streamlit as st
from streamlit_navigation_bar import st_navbar
import requests as req
import json
import pandas as pd
from utils.document_embedding_process import procesar_arch_db
from utils.document_vectordb_deletion import eliminar_arch_db
from utils.create_embeddings import create_web_scraping_embeddings
from utils.scraper import scraper
import time

#BARRA DE NAVEGACION
styles = {
    "nav": {
        "background-color": "#31333F",
        "justify-content": "space-between"
    },
    "div": {
        "max-width": "40rem",
    },
    "span": {
        "border-radius": "0.5rem",
        "color": "#E5E5EA",
        "margin": "0 0.125rem",
        "padding": "0.4375rem 0.625rem",
        "font-family": "sans-serif",
    },
    "active": {
        "font-weight": "normal",
    },
    "hover": {
        "background-color": "rgba(255, 255, 255, 0.5)",
    },
}

icons = {
    "Mi cuenta": ":material/account_circle:",
    "Cerrar sesión": ":material/logout:",
    "Panel de Administrador": ":material/switch_account:",
    "Panel de Estudiante": ":material/switch_account:",
}

st.set_page_config(
    layout = "wide",
    page_title = "QuillaGPT"
)

if "page_session" not in st.session_state:
    st.session_state.page_session = " "

#crear la variable de ID tabla para poder reiniciar la seleccion
if "tabla_id" not in st.session_state:
    st.session_state.tabla_id = 0

# CONTENIDO DEL NAV BAR
page = st_navbar(
    [],
    right=[" ", "Panel de Estudiante", "Mi cuenta", "Cerrar sesión"],
    styles=styles,
    icons=icons,
    options={"fix_shadow": False},
    selected= st.session_state.page_session
)

#modal de configuracion del usuario
@st.dialog("Mi cuenta")
def config_user():
    col1, col2, col3 = st.columns([1, 0.75, 1])
    with col2:
        st.image(st.session_state.user["picture"], width=100)
    st.text_input("**Nombre de usuario**", value=st.session_state["username"], disabled=True)
    st.text_input("**Correo electrónico**", value=st.session_state.user["email"], disabled=True)
    st.text_input("**Rol**", value="Administrador" if st.session_state.role_id == 1 else "Estudiante", disabled=True)

if page == "Mi cuenta":
    config_user()
    st.session_state.page_session = "Mi cuenta"
elif page == "Cerrar sesión":
    st.session_state.page_session = " "
    st.session_state["username"] = ""
    st.session_state.messages = []
    st.session_state["user"] = None
    st.session_state["credentials"] = None
    st.session_state.feedback_response = False
    st.switch_page('main.py')
elif page == "Panel de Estudiante":
    st.session_state.page_session = " "
    st.switch_page('./pages/quillagpt.py')

#cargar el archivo css y llamarla
def cargar_css(file_path):
    with open(file_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
cargar_css("style.css")

#titulo
container_inicio = st.container()
container_inicio.write("")
container_inicio.write("")
container_inicio.write("")
container_inicio.write("")
container_inicio.write("")
container_inicio.write("")
container_inicio.title("Gestión de Conocimiento")

tab1, tab2, tab3 = st.tabs(["Conocimiento inicial", "Conocimiento dinámico", "Instrucciones personalizadas"])

#conocimiento inicial
with tab1:
    st.write("QuillaGPT tiene en cuenta la información de los procesos académicos y administrativos disponibles públicamente en las siguientes páginas web:")
    st.markdown("""
    - https://sites.google.com/pucp.edu.pe/fci-pucp/estudiantes
    - https://estudiante.pucp.edu.pe/tramites-y-certificaciones/tramites-academicos/?dirigido_a%5B%5D=Estudiantes&unidad%5B%5D=Facultad+de+Ciencias+e+Ingenier%C3%ADa
    - https://facultad-ciencias-ingenieria.pucp.edu.pe/estudiantes/tramites-academicos-y-administrativos/
    """)
    st.subheader("¿Deseas actualizar la información disponible?")
    st.write("""
El proceso de actualización incluye los siguientes pasos:

1. Revisión automática de las páginas previamente mencionadas.
2. Identificación y extracción de los trámites y procesos administrativos según la página correspondiente.
3. Almacenamiento de datos en la base de datos para que QuillaGPT pueda utilizarlos en respuestas a consultas de los estudiantes.

Haz clic en el botón de abajo para asegurarte de tener los datos más recientes. Recuerda que este proceso puede tardar algunos minutos en completarse.""")

    if 'run_button' in st.session_state and st.session_state.run_button == True:
        st.session_state.running = True
    else:
        st.session_state.running = False

    if st.button('Actualizar información', disabled=st.session_state.running, key='run_button', icon=":material/sync:", type="secondary"):
        status = st.progress(0, text="Extrayendo datos de la Facultad de Ciencias e Ingeniería...")
        scraper()
        status.progress(0.50, text="Actualizando base de datos de QuillaGPT...")
        create_web_scraping_embeddings()
        status.progress(0.99, text="Actualización completada exitosamente...")
        time.sleep(3)
        st.rerun()

with st.sidebar:
    st.title("Bienvenido, "+ f":blue[{st.session_state["username"]}]!")

    st.write("")
    
    if st.button("Gestión de Usuarios", use_container_width=True, type="secondary", icon=":material/group:"):
        st.switch_page("./pages/dashboard_users.py")

    st.button("Gestión de Conocimiento", use_container_width=True, icon=":material/description:", disabled=True)

    if st.button("Solicitudes de Soporte", use_container_width=True, type="secondary", icon=":material/question_answer:"):
        st.switch_page("./pages/dashboard_queries.py")

    if st.button("Reporte de Indicadores", use_container_width=True, type="secondary", icon=":material/bar_chart:"):
        st.switch_page("./pages/dashboard_report.py")