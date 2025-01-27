import streamlit as st
from google.auth.transport import requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import InstalledAppFlow
import pymysql
from streamlit_extras.stylable_container import stylable_container
import requests as req
import json

if "user" not in st.session_state:
    st.session_state.user = None
if "credentials" not in st.session_state:
    st.session_state.credentials = None
if "role_id" not in st.session_state:
    st.session_state.role_id = None

flow = InstalledAppFlow.from_client_secrets_file(
    "./client_secret.json",
    scopes=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ],
    redirect_uri="http://localhost:9000/",
)

st.set_page_config(
    layout = "wide",
    page_title = "QuillaGPT"
)

conn = pymysql.connect(
    host=st.secrets["mysql"]["host"],
    user=st.secrets["mysql"]["username"],
    password=st.secrets["mysql"]["password"],
    database=st.secrets["mysql"]["database"]
)

def login_callback():
    credentials = flow.run_local_server(
        port=9000,
        open_browser=True,
        success_message="La autenticación ha sido completada exitosamente. Ya puedes cerrar esta ventana.",
        prompt="login",
    )
    id_info = id_token.verify_token(
        credentials.id_token,
        requests.Request(),
    )
    st.session_state.credentials = credentials
    st.session_state.user = id_info

if not st.session_state.user:

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("<img src='app/static/squirrel.png' width='200' style='display: block; margin: 0 auto;'>" , unsafe_allow_html=True)

        st.markdown(
            """
            <h2 style="text-align: center;">¡Bienvenido a QuillaGPT!</h2>
            """,
            unsafe_allow_html=True
        )

        st.write("Quilla es tu asistente virtual de la Facultad de Ciencias e Ingeniería de la PUCP. Está aquí para ayudarte con todas tus dudas sobre trámites académico-administrativos, como reclamo de notas, retiro de cursos y más. Puedes contar con ella las 24 horas del día para resolver tus preguntas de manera rápida y sencilla.")

        with stylable_container(
        key="registrarse_button",
        css_styles="""
                .element-container:has(#button-after) + div button {
                    background-color: #31333F !important;
                    color: white !important;
                    border-color: #31333F !important;
                }
                .element-container:has(#button-after) + div button::hover {
                    background-color: #31333F !important;
                    border-color: #31333F !important;
                }
                """,
        ):
            st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
            st.button("Iniciar sesión con Google", type = 'secondary', icon=':material/login:', use_container_width = True, on_click=login_callback)

        st.stop()

result = req.get(f"http://127.0.0.1:8000/User/{st.session_state.user["email"]}")
if result.status_code == 200:
    if result.json() != -1:
        print("Se procede a iniciar sesión con el rol del usuario")
        st.session_state.role_id = result.json()[1]
        st.session_state["username"] = st.session_state.user["given_name"]
        st.switch_page('./pages/quillagpt.py')
    else:
        print("Se procede a crear un nuevo usuario con rol de estudiante")
        input = {"email" : st.session_state.user["email"]}
        result = req.post(url="http://127.0.0.1:8000/User", data = json.dumps(input))
        st.session_state.role_id = 2
        st.session_state["username"] = st.session_state.user["given_name"]
        st.switch_page('./pages/onboarding_p1.py')