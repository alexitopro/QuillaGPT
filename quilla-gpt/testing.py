import streamlit as st
import time

conn = st.connection('mysql', type='sql')

df = conn.query('SELECT * from Role', ttl = 600)

st.write(df)

def checkLogin(username, password):
    error = st.error("Usuario o contraseña incorrectos")
    time.sleep(2)
    error.empty()

col1, col2, col3 = st.columns([1, 1.5, 1])
with col2:
    username = st.text_input(f"**Correo electrónico**", placeholder = "Email", max_chars = 50)

    password = st.text_input(f"**Contraseña**", placeholder = "Contraseña", type = "password", max_chars = 50)

    if st.button("Iniciar sesión", type = 'primary', use_container_width = True):
        error = st.error("Usuario o contraseña incorrectos")
        time.sleep(2)
        error.empty()