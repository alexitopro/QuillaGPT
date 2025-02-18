import streamlit as st
import json
from streamlit_lottie import st_lottie 

st.set_page_config(
    layout = "centered",
    page_title = "QuillaGPT"
)

#carga de spinner lottie
def load_lottie_json(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

with st.container(height=160, border=False):
    st.header("Deriva tu consulta")
    st.write("Y si no encuentras la respuesta que buscabas, puedo derivar derivar tu consulta al administrador para que te brinde una respuesta por correo electrónico.")

lottie_json = load_lottie_json("./static/email_support_p4.json")

with st.container(height=280, border=False):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st_lottie(lottie_json, 
            reverse=True,
            width=350, 
            speed=1, 
            loop=True, 
            quality='high',
        )

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    col21, col22, col23 = st.columns([1, 5, 1])
    with col22:
        st.write("")
        if st.button("Entrar a QuillaGPT", type="primary"):
            st.switch_page("./pages/quillagpt.py")