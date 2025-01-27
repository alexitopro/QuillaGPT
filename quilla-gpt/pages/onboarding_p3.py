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
    st.header("Califica mis respuestas")
    st.write("Puedes calificar mis respuestas para mejorar y brindarte un mejor servicio. ¡Contigo puedo hacer que más estudiantes tengan una experiencia aún mejor!")

lottie_json = load_lottie_json("./static/feedback_p3.json")

with st.container(height=280, border=False):
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st_lottie(lottie_json, 
            reverse=True,
            width=250, 
            speed=1, 
            loop=True, 
            quality='high',
        )

col1, col2, col3 = st.columns([1, 3, 0.75], vertical_alignment="center")
with col1:
    st.write("")
    if st.button("Atrás", type="tertiary"):
        st.switch_page("./pages/onboarding_p2.py")
with col3:
    st.write("")
    if st.button("Siguiente", type="primary"):
        st.switch_page("./pages/onboarding_p4.py")