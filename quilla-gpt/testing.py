import streamlit as st

@st.dialog("Configuración del usuario")
def config():
    tab1, tab2 = st.tabs(["Configuración del perfil", "Conversaciones"])
    with tab1:
        with st.form("h", border=False):
            st.write("Inside the form")
            slider_val = st.slider("Form slider")
            checkbox_val = st.checkbox("Form checkbox")

            # Every form must have a submit button.
            submitted = st.form_submit_button("Submit")
            if submitted:
                st.write("slider", slider_val, "checkbox", checkbox_val)
    with tab2:
        st.write("Inside the second tab")

if st.button("Open dialog"):
    config()