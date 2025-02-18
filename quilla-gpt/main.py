import streamlit as st
from google.auth.transport import requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import InstalledAppFlow
import pymysql
from streamlit_extras.stylable_container import stylable_container
import requests as req
import json
import base64

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
        clock_skew_in_seconds=10
    )
    st.session_state.credentials = credentials
    st.session_state.user = id_info

if not st.session_state.user:

    col1, col3 = st.columns([2, 2])
    with col1:
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")

        st.markdown("<img src='app/static/panda.png' width='200' style='display: block; margin: 0 auto;'>" , unsafe_allow_html=True)

        #00205B
        st.markdown(
            '<div style="color: #00205B; font-size: 3em; font-weight: 600;">PandaGPT</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div style="color: #00205B; font-size: 1.5em; font-weight: 600;">Un asistente virtual pensado en ti para trámites de la Facultad de Ciencias e Ingeniería.</div>',
            unsafe_allow_html=True
        )

        #00CFB4
        with stylable_container(
        key="registrarse_button",
        css_styles="""
                .element-container:has(#button-after) + div button {
                    background-color: #00CFB4 !important;
                    color: white !important;
                    border-color: #00CFB4 !important;
                }
                .element-container:has(#button-after) + div button::hover {
                    background-color: #00CFB4 !important;
                    border-color: #00CFB4 !important;
                }
                """,
        ):
            st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
            st.button("Iniciar sesión con Google", type = 'secondary', icon=':material/login:', use_container_width = True, on_click=login_callback)

    with col3:
        file_ = open("./static/animacion_main.gif", "rb")
        contents = file_.read()
        data_url = base64.b64encode(contents).decode("utf-8")
        file_.close()

        st.markdown(
            f"""
            <div style="text-align: center;">
                <img src="data:image/gif;base64,{data_url}" style="width: 85%;">
            </div>
            """,
            unsafe_allow_html=True,
        )

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