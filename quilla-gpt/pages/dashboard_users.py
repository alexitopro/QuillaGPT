import streamlit as st
from streamlit_navigation_bar import st_navbar
import requests as req
import json
import pandas as pd
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

#crear la variable de ID tabla para poder reiniciar la seleccion
if "tabla_id" not in st.session_state:
    st.session_state.tabla_id = 0

if "bandera" not in st.session_state:
    st.session_state.bandera = False

#modal para revisar la consulta del estudiante
@st.dialog("Detalle del usuario")
def verDetalle(selected_index):
    st.text_input("**Correo electrónico**", value=df.loc[selected_index, "Correo electrónico"], disabled=True)

    rol_detalle = st.selectbox("**Rol**",  ["Administrador", "Estudiante"], disabled=True if df.loc[selected_index, "Correo electrónico"] == st.session_state.user["email"] else False, index=0 if df.loc[selected_index, "Rol"] == "Administrador" else 1)

    st.text_input("**Estado**", value=df.loc[selected_index, "Estado"], disabled=True)

    st.write("")
    col1, col2, col3 = st.columns([2, 3, 3])
    with col2:
        if st.button("Cancelar", use_container_width=True, type="secondary"):
            st.session_state.tabla_id += 1
            st.rerun()
    with col3:
        submitted = st.button("Guardar cambios", use_container_width=True, type="primary", disabled=True if df.loc[selected_index, "Correo electrónico"] == st.session_state.user["email"] else False)
        if submitted:
            input = {"email" : df.loc[selected_index, "Correo electrónico"], "rol" : rol_detalle}
            req.put(f"http://127.0.0.1:8000/User/CambiarRolUsuario", data = json.dumps(input))
            st.session_state.tabla_id += 1
        
            st.session_state.bandera = True
            st.rerun()

if st.session_state.bandera:
    st.toast("Se ha actualizado el rol del usuario", icon=":material/check:")
    st.session_state.bandera = False

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

#titulo
container_inicio = st.container()
container_inicio.write("")
container_inicio.write("")
container_inicio.write("")
container_inicio.write("")
container_inicio.write("")
container_inicio.write("")
container_inicio.title("Gestión de Usuarios")

#contenido
col1, col2, col3 = st.columns([2.5, 1.5, 1], vertical_alignment="bottom")
with col1:
    usuario = st.text_input("**Buscar usuario**", placeholder="Ingrese el correo del usuario", max_chars=50)
with col2:
    rol = st.selectbox("**Rol**", ["Todos", "Administrador", "Estudiante"])
with col3:
    estado = st.selectbox("**Estado**", ["Todos", "Activo", "Inactivo"])

input = {"email" : usuario, "rol" : rol, "estado" : estado}
result = req.get(url="http://127.0.0.1:8000/ObtenerUsuarios", data = json.dumps(input))
data = result.json()
df = pd.DataFrame(data, columns=["ID", "Correo electrónico", "Rol", "Estado"])

event = st.dataframe(
    df,
    on_select="rerun",
    selection_mode=["single-row"],
    hide_index=True,
    key = str(st.session_state.tabla_id),
    use_container_width=True
)

if event.selection is not None:
    if event.selection['rows']:
        selected_index = event.selection['rows'][0]
        verDetalle(selected_index)

with st.sidebar:
    st.title("Bienvenido, "+ f":blue[{st.session_state["username"]}]!")
    
    st.write("")

    st.button("Gestión de Usuarios", use_container_width=True, icon=":material/group:", disabled=True)

    if st.button("Gestión de Conocimiento", use_container_width=True, type="secondary", icon=":material/description:"):
        st.switch_page("./pages/dashboard_knowledge.py")

    if st.button("Solicitudes de Soporte", use_container_width=True, type="secondary", icon=":material/question_answer:"):
        st.switch_page("./pages/dashboard_queries.py")

    if st.button("Reporte de Indicadores", use_container_width=True, type="secondary", icon=":material/bar_chart:"):
        st.switch_page("./pages/dashboard_report.py")