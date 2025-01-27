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
    st.header("Soporte en trámites administrativos")
    st.write("Puedo guiarte en los trámites académico-administrativos de la universidad. A través de una interfaz de conversación, te explico el proceso, los pasos a seguir, los requisitos necesarios y dónde encontrar información adicional.")

lottie_json = load_lottie_json("./static/girl_chatting_onboarding_p2.json")

with st.container(height=280, border=False):
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st_lottie(lottie_json, 
            reverse=True, 
            width=350, 
            speed=1, 
            loop=True, 
            quality='high',
        )

col1, col2, col3 = st.columns([1, 3, 0.75], vertical_alignment="center")
with col1:
    st.write("")
    if st.button("Atrás", type="tertiary"):
        st.switch_page("./pages/onboarding_p1.py")
with col3:
    st.write("")
    if st.button("Siguiente", type="primary"):
        st.switch_page("./pages/onboarding_p3.py")