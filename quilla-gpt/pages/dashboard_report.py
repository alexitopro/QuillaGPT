import streamlit as st
from streamlit_navigation_bar import st_navbar
import requests as req
import json
from utils.query_to_vectorDB_uploader import create_query_embedding
import hashlib
import time
import pandas as pd
import plotly.express as px
import datetime
from PIL import Image
from io import BytesIO

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
    st.session_state.page_session = " "
    with col2:
        image_url = st.session_state.user["picture"]
        response = req.get(image_url)
        image = Image.open(BytesIO(response.content))
        st.image(image, width=100)
    st.text_input("**Nombre de usuario**", value=st.session_state["username"], disabled=True)
    st.text_input("**Correo electrónico**", value=st.session_state.user["email"], disabled=True)
    st.text_input("**Rol**", value="Administrador" if st.session_state.role_id == 1 else "Estudiante", disabled=True)

if page == "Mi cuenta":
    config_user()
    # st.session_state.page_session = "Mi cuenta"
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

container_inicio = st.container()
container_inicio.write("")
container_inicio.write("")
container_inicio.write("")
container_inicio.write("")
container_inicio.write("")
container_inicio.write("")
container_inicio.title("Reporte de Indicadores", anchor=False)

hoy = datetime.date.today()
primer_dia = hoy.replace(day=1)
col1, col2 = st.columns([1, 5])
with col1:
    date_picker = st.date_input("**Rango de fecha de análisis**", (primer_dia, "today"), format="DD/MM/YYYY")

if len(date_picker) == 2:
    inicio, fin = date_picker
    input = {"start_date": inicio.isoformat(), "end_date": fin.isoformat()}

    col1, col2, col3, col4 = st.columns(4, vertical_alignment="center")

    with col1:
        sesiones_mes = req.get("http://localhost:8000/ObtenerCantConversaciones", data = json.dumps(input)).json()
        st.metric(label = "**Conversaciones**", value = sesiones_mes, border=True)
        
    with col2:
        porcentaje_derivadas = req.get("http://localhost:8000/RatioConsultasDerivadas", data = json.dumps(input)).json()
        if porcentaje_derivadas is None:
            porcentaje_derivadas = 0
        st.metric(label = "**Ratio de solicitudes de soporte**", value = str(round(porcentaje_derivadas)) + '%', border=True)

    with col3:
        cant_admins = req.get("http://localhost:8000/PromedioEstudiantesActivos", data = json.dumps(input)).json()
        if cant_admins is None:
            cant_admins = 0
        st.metric(label = "**Promedio de estudiantes activos**", value = int(cant_admins), border=True)

    with col4:
        cant_usuarios = req.get("http://localhost:8000/CantidadUsuarios").json()
        st.metric(label = "**Estudiantes registrados**", value = cant_usuarios, border=True)

    with st.container(border=True):
        col1, col2, col3 = st.columns([1, 0.5, 1])
        with col2:
            st.write("**Cantidad de Consultas**")
        st.write("")
        data = req.get("http://localhost:8000/CantidadConsultasDiarias", data = json.dumps(input)).json()
        df = pd.DataFrame(data, columns=["Día", "Cantidad de Consultas"])
        if df.empty:
            st.caption("No se han efectuado consultas en el rango de fechas seleccionadas.")
        else:
            st.bar_chart(data=df, x="Día", y="Cantidad de Consultas")

    # with col2_columna2:
    #     with st.container(border=True):
    #         col1, col2, col3 = st.columns([1, 1.5, 1])
    #         with col2:
    #             st.write("**Top 5 Temas de Consulta**")
    #         data = req.get("http://localhost:8000/Top5TemasConsulta").json()
    #         df = pd.DataFrame(data, columns=["Tema", "Cantidad de Consultas"])
    #         if df.empty:
    #             st.caption("No se han efectuado consultas a lo largo del mes.")
    #         else:
    #             fig = px.pie(df, values='Cantidad de Consultas', names='Tema')
    #             fig.update_traces(textposition='outside', textinfo='percent+label')
    #             fig.update_layout(showlegend=False)
    #             fig.update_layout(height=391)
    #             st.plotly_chart(fig, use_container_width=True)
else:
    st.caption("Por favor, selecciona un rango de fecha apropiado para visualizar los indicadores.")

obtenerContador = req.get(url="http://127.0.0.1:8000/ObtenerContadorSolicitudes")
contadorRequests = obtenerContador.json()

if "support_requests" not in st.session_state:
    st.session_state.support_requests = contadorRequests
else:
    st.session_state.support_requests = contadorRequests

button_text = "Solicitudes de Soporte"
if st.session_state.support_requests > 0:
    button_text += f" ({st.session_state.support_requests})"

with st.sidebar:
    st.title("Bienvenido, "+ f":blue[{st.session_state["username"]}]!")
    
    st.write("")
    
    if st.button("Gestión de Usuarios", use_container_width=True, type="secondary", icon=":material/group:"):
        st.switch_page("./pages/dashboard_users.py")

    if st.button("Gestión del Conocimiento", use_container_width=True, icon=":material/description:", type="secondary"):
        st.switch_page("./pages/dashboard_knowledge.py")

    if st.button(button_text, use_container_width=True, icon=":material/question_answer:", type="secondary"):
        st.switch_page("./pages/dashboard_queries.py")

    st.button("Reporte de Indicadores", use_container_width=True, icon=":material/bar_chart:", type="primary")