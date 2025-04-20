import streamlit as st
from streamlit_navigation_bar import st_navbar
import requests as req
import json
from PIL import Image
from io import BytesIO

#BARRA DE NAVEGACION
styles = {
    "nav": {
        "background-color": "#00205B",
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
    page_title = "PandaGPT"
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
    st.text_input("**Nombre de usuario**", value=data[selected_index][1], disabled=True)

    st.text_input("**Correo electrónico**", value=data[selected_index][2], disabled=True)

    rol_detalle = st.selectbox("**Rol**",  ["Administrador", "Estudiante"], disabled=True if data[selected_index][2] == st.session_state.user["email"] else False, index=0 if data[selected_index][3] == "Administrador" else 1)

    st.text_input("**Estado**", value=data[selected_index][4], disabled=True)

    st.write("")
    col1, col2, col3 = st.columns([2, 3, 3])
    with col2:
        if st.button("Cancelar", use_container_width=True, type="secondary"):
            st.session_state.tabla_id += 1
            st.rerun()
    with col3:
        submitted = st.button("Guardar cambios", use_container_width=True, type="primary", disabled=True if data[selected_index][2] == st.session_state.user["email"] else False)
        if submitted:
            input = {"email" : data[selected_index][2], "rol" : rol_detalle}
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
    # st.session_state["user"] = None
    # st.session_state["credentials"] = None
    st.session_state.feedback_response = False
    # st.switch_page('main.py')
    st.logout()
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
container_inicio.title("Gestión de Usuarios", anchor=False)

#anadir css para el buscador
st.markdown("""
    <link rel="stylesheet" 
        href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
            
    <script>
        function triggerSearch() {
            const searchBox = document.querySelector('div[data-testid="stTextInput"] input');
            searchBox.dispatchEvent(new Event('input', { bubbles: true }));
        }
    </script>

    <style>
    div[data-testid="stTextInput"] {
        position: relative;
    }
    div[data-testid="stTextInput"] input {
        padding-right: 35px;
    }
    div[class*="st-key-usuario_buscador"] div[data-testid="stTextInput"]::after {
        content: "search";
        font-family: 'Material Symbols Outlined';
        font-size: 20px;
        position: absolute;
        right: 10px;
        top: 50%;
        color: gray;
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

#contenido
col1, col2, col3 = st.columns([1.5, 1, 3], vertical_alignment="bottom")
with col1:
    usuario = st.text_input("**Buscar usuario**", placeholder="Ingrese el correo del usuario", max_chars=50, key="usuario_buscador")
with col2:
    rol = st.selectbox("**Rol**", ["Todos", "Administrador", "Estudiante"])
# with col3:
#     estado = st.selectbox("**Estado**", ["Todos", "Activo", "Inactivo"])

input = {"email" : usuario, "rol" : rol, "estado" : "Activo"}
result = req.get(url="http://127.0.0.1:8000/ObtenerUsuarios", data = json.dumps(input))
data = result.json()

for i in range(len(data)):
    with st.container(border=True, key="container"+str(i)):
        col_cont1, col_cont2 = st.columns([4, 0.25], vertical_alignment
        ="center")
        with col_cont1:
            st.subheader(data[i][1], anchor=False)
            st.write(f"**Correo electrónico:** {data[i][2]}")
            st.write(f"**Rol:** {data[i][3]}")
            st.write("")
        with col_cont2:
            if st.button("", key="editar"+str(i), type="secondary", icon=":material/edit:"):
                verDetalle(i)

# df = pd.DataFrame(data, columns=["ID", "Nombre de usuario", "Correo electrónico", "Rol", "Estado"])

# event = st.dataframe(
#     df,
#     on_select="rerun",
#     column_order=["Nombre de usuario", "Correo electrónico", "Rol", "Estado"],
#     selection_mode=["single-row"],
#     hide_index=True,
#     key = str(st.session_state.tabla_id),
#     use_container_width=True
# )

# if event.selection is not None:
#     if event.selection['rows']:
#         selected_index = event.selection['rows'][0]
#         verDetalle(selected_index)

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

    st.markdown(
        f"""
        <h1 style="color:#00205B;">Bienvenido, {st.session_state["username"]}!</h1>
        """,
        unsafe_allow_html=True
    )
    
    st.write("")

    st.button("Gestión de Usuarios", use_container_width=True, icon=":material/group:", type="primary")

    if st.button("Gestión del Conocimiento", use_container_width=True, type="secondary", icon=":material/description:"):
        st.switch_page("./pages/dashboard_knowledge.py")

    if st.button(button_text, use_container_width=True, type="secondary", icon=":material/question_answer:"):
        st.switch_page("./pages/dashboard_queries.py")

    if st.button("Reporte de Indicadores", use_container_width=True, type="secondary", icon=":material/bar_chart:"):
        st.switch_page("./pages/dashboard_report.py")