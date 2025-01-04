import streamlit as st
import hashlib
import pymysql
import time
from streamlit_extras.stylable_container import stylable_container

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

col1, col2, col3 = st.columns([1, 1.5, 1])
with col2:
    st.markdown("<img src='app/static/squirrel.png' width='100' style='display: block; margin: 0 auto;'>" , unsafe_allow_html=True)

    st.markdown(
        """
        <h2 style="text-align: center;">Regístrate en QuillaGPT</h2>
        """,
        unsafe_allow_html=True
    )

    email = st.text_input(f"**Correo electrónico**", placeholder = "name@domain.com", max_chars = 50)

    password = st.text_input(f"**Contraseña**", type = "password", max_chars = 50, help = "La contraseña debe tener por lo menos 8 caracteres, una mayúscula, una minúscula y un número")

    username = st.text_input(f"**Nombre de usuario**", max_chars = 50)

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
        if st.button("Registrarse", type = 'secondary', use_container_width = True):
            if email == "":
                flag = "Debe ingresar su correo electrónico."
            elif password == "":
                flag = "Debe ingresar su contraseña."
            elif not any(char.isupper() for char in password):
                flag = "La contraseña debe tener por lo menos una letra mayúscula."
            elif not any(char.islower() for char in password):
                flag = "La contraseña debe tener por lo menos una letra minúscula."
            elif not any(char.isdigit() for char in password):
                flag = "La contraseña debe tener por lo menos un número."
            elif len(password) < 8:
                flag = "La contraseña debe tener por lo menos 8 caracteres."
            else:
                cursor = conn.cursor()
                query = "SELECT username from User WHERE email = %s"
                values = email
                cursor.execute(query, values)
                record = cursor.fetchone()
                if record:
                    flag = "El correo electrónico ingresado ya se encuentra en uso."
                else:
                    query = "SELECT username from User WHERE username = %s"
                    values = username
                    cursor.execute(query, values)
                    record = cursor.fetchone()
                    if record:
                        flag = "El nombre de usuario ingresado ya se encuentra en uso."
                    else:
                        contrasena_hasheada = hashlib.sha256(password.encode()).hexdigest()
                        query = """
                            INSERT INTO User 
                            (email, username, password, role_id, active) 
                            VALUES (%s, %s, %s, 2, 1)
                        """
                        values = (email, username, contrasena_hasheada)
                        cursor.execute(query, values)
                        conn.commit()
                        st.session_state["username"] = username
                        st.switch_page('./pages/quilla_gpt.py')

    col1, col2, col3, col4 = st.columns([2, 1.40, 1.40, 2], vertical_alignment="center")
    with col2:
        st.write("")
        st.write("¿Ya tienes cuenta?")
    with col3:
        with stylable_container(
            key="inicia_sesion_button",
            css_styles="""
                .element-container:has(#button-iniciar-after) + div button {
                    text-decoration: underline !important;
                }
                """,
        ):
            st.markdown('<span id="button-iniciar-after"></span>', unsafe_allow_html=True)
            if st.button("Inicia sesión aquí", type = "tertiary", use_container_width = True):
                st.switch_page('main.py')

    if flag:
        error = st.error(flag)
        time.sleep(4)
        error.empty()