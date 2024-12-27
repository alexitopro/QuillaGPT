import streamlit as st
import base64
import random
import time

st.set_page_config(
    layout = "wide",
    page_title = "QuillaGPT"
)

#cargar el archivo css y llamarla
def cargar_css(file_path):
    with open(file_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
cargar_css("./style.css")

#carga de imagenes
def encode_image(file_path):
    with open(file_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")
user_icon = encode_image("./static/profile-account.png")
bot_icon = encode_image("./static/squirrel.png")
plus_icon = encode_image("./static/plus.png")

#barra lateral
with st.sidebar:
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <h1 style="margin: 0;">Mis conversaciones</h1>
            <a href="#" style="text-decoration: none;"">
                <img src="data:image/png;base64,{plus_icon}" width="30" style="cursor: pointer;" />
            </a>
        </div>
        """,
        unsafe_allow_html = True
    )

#container de inicio
container_inicio = st.container()
container_inicio.title("¡Hola, soy QuillaBot! ¿En qué te puedo ayudar?")
container_inicio.write(
    "Recuerda que los datos personales que proporciones en este chatbot serán de uso exclusivo para atender las consultas que formules."
)

#inicializar historial de mensajes
if "messages" not in st.session_state:
    st.session_state.messages = []

#entrada de texto del usuario
prompt = st.chat_input(placeholder="Ingresa tu consulta sobre algún procedimiento académico-administrativo de la PUCP")