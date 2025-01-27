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
        st.image("./static/squirrel.png", use_container_width=True)

welcome_text = """
Mi nombre es QuillaGPT, asistente virtual de la Facultad de Ciencias e Ingeniería de la PUCP. 
Estoy aquí para ayudarte con todas tus dudas sobre trámites académico-administrativos, como reclamo de notas, retiro de cursos y más. 
Puedes contar conmigo las **24 horas del día** para resolver tus preguntas de manera rápida y sencilla.
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