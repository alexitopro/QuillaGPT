import streamlit as st
import hashlib
import pymysql
import time
from streamlit_extras.stylable_container import stylable_container

st.set_page_config(
    layout = "wide",
    page_title = "QuillaGPT"
)

#quitar la barra superior de streamlit
# st.markdown("""
# <style>
# 	[data-testid="stDecoration"] {
# 		display: none;
# 	}
# </style>""",
# unsafe_allow_html=True)

#conexion en mysql
conn = pymysql.connect(
    host=st.secrets["mysql"]["host"],
    user=st.secrets["mysql"]["username"],
    password=st.secrets["mysql"]["password"],
    database=st.secrets["mysql"]["database"]
)

#settings for text input
# tabs_font_css = """
# <style>
#     div[class*="forgot_password"] p {
#         text-decoration: underline;
#     }

#     div[class*="register"] p {
#         text-decoration: underline;
#     }
# # </style>
# # """
# st.write(tabs_font_css, unsafe_allow_html=True)

#parametros para enviar el estado a la siguiente página
if "username" not in st.session_state:
    st.session_state["username"] = ""

col1, col2, col3 = st.columns([1, 1.5, 1])
with col2:
    st.markdown("<img src='app/static/squirrel.png' width='100' style='display: block; margin: 0 auto;'>" , unsafe_allow_html=True)

    st.markdown(
        """
        <h2 style="text-align: center;">Inicia sesión en QuillaGPT</h2>
        """,
        unsafe_allow_html=True
    )

    # st.write("")

    email = st.text_input(f"**Correo electrónico**", placeholder = "Email", max_chars = 50)

    password = st.text_input(f"**Contraseña**", placeholder = "Contraseña", type = "password", max_chars = 50)

    flag = ""
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
        if st.button("Iniciar sesión", type = 'secondary', use_container_width = True):
            if email == "":
                flag = "Debe ingresar su correo electrónico."
            elif password == "":
                flag = "Debe ingresar su contraseña."
            else:
                cursor = conn.cursor()
                query = "SELECT username, role_id from User WHERE email = %s AND password = %s"
                hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
                values = (email, hashed_password)
                cursor.execute(query, values)
                record = cursor.fetchone()
                if record:
                    st.session_state["username"] = record[0]
                    if record[1] == 1:
                        st.switch_page('./pages/admin_dashboard_users.py')
                    else:
                        st.switch_page('./pages/quilla_gpt.py')
                else:
                    flag = "Correo electrónico o contraseña incorrectos."
        
    with stylable_container(
        key="olvidar_contra_button",
        css_styles="""
            .element-container:has(#olvidar-contra-after) + div button {
                text-decoration: underline !important;
            }
            """,
    ):
        st.markdown('<span id="olvidar-contra-after"></span>', unsafe_allow_html=True)
        if st.button("¿Has olvidado tu contraseña?", type = "tertiary", use_container_width = True):
            st.switch_page('./pages/forgot_password.py')

    col1, col2, col3, col4 = st.columns([2.25, 2, 2.5, 2.25], vertical_alignment="center")
    with col2:
        st.write("")
        st.write("¿No tienes cuenta?")
    with col3:
        with stylable_container(
            key="inicia_sesion_button",
            css_styles="""
                .element-container:has(#registrarse-after) + div button {
                    text-decoration: underline !important;
                }
                """,
        ):
            st.markdown('<span id="registrarse-after"></span>', unsafe_allow_html=True)
            if st.button("Regístrate en QuillaGPT", type = "tertiary", use_container_width = True):
                st.switch_page('./pages/user_registration.py')

    if flag:
        error = st.error(flag)
        time.sleep(4)
        error.empty()