import streamlit as st
import hashlib
import pymysql
import time

st.set_page_config(
    layout = "wide",
    page_title = "QuillaGPT"
)

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
    if st.button("Iniciar sesión", type = 'secondary', use_container_width = True):
        if email == "":
            flag = "Debe ingresar su correo electrónico"
        elif password == "":
            flag = "Debe ingresar su contraseña"
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
                flag = "Correo electrónico o contraseña incorrectos"
        
    if st.button("¿Has olvidado tu contraseña?", type = "tertiary", use_container_width = True, key = "forgot_password"):
        st.toast("Enviando correo de recuperación...")

    if st.button("¿No tienes cuenta? Regístrate en QuillaGPT", type = "tertiary", use_container_width = True, key = "register"):
        st.toast("Redirigiendo a la página de registro...")

    if flag:
        error = st.error(flag)
        time.sleep(4)
        error.empty()