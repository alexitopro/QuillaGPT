import streamlit as st
import time

st.set_page_config(
    layout = "centered",
    page_title = "QuillaGPT"
)

col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.title("¡Bienvenido, "+ st.session_state["username"] + "!", anchor=False)    
    col21, col22, col23 = st.columns([1, 3, 1])
    with col22:
        st.image("./static/panda.png", use_container_width=True)

welcome_text = """
¡Hola! Soy PandaGPT, tu asistente virtual de la Facultad de Ciencias e Ingeniería de la PUCP.
Estoy aquí para ayudarte con tus dudas sobre trámites académico-administrativos, como reclamos de notas, retiros de cursos y más.
¡Disponible las 24 horas para responderte rápido y fácil!
"""

if "stream_complete" not in st.session_state:
    st.session_state.stream_complete = False

if not st.session_state.stream_complete:
    def stream_text(text):
        for word in text.split():
            yield word + " "
            time.sleep(0.035)
        st.session_state.stream_complete = True

    st.write_stream(stream_text(welcome_text))

if st.session_state.stream_complete:
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:   
        col21, col22, col23 = st.columns([1, 1, 1])
        with col22:
            st.write("")
            st.write("")
            st.write("")
            if st.button("¡Comencemos!", type="primary"):
                st.session_state.stream_complete = False
                st.switch_page("./pages/onboarding_p2.py")