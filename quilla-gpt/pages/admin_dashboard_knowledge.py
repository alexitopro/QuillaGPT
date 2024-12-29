import streamlit as st

st.set_page_config(
    layout = "wide",
    page_title = "QuillaGPT"
)

#cargar el archivo css y llamarla
def cargar_css(file_path):
    with open(file_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
cargar_css("./style.css")

container_inicio = st.container()
container_inicio.title("Gestión de Conocimiento")

with st.sidebar:
    # cargar_css("./style.css")
    st.title("Bienvenido, "+ f":blue[{st.session_state["username"]}]!")
    
    if st.button("Gestión de Usuarios", use_container_width=True, type="secondary", icon=":material/group:"):
        st.switch_page("./pages/admin_dashboard_users.py")

    st.button("Gestión de Conocimiento", use_container_width=True, icon=":material/description:", disabled=True)

    if st.button("Banco de Consultas", use_container_width=True, type="secondary", icon=":material/question_answer:"):
        st.switch_page("./pages/admin_dashboard_queries.py")

    if st.button("Reporte de Indicadores", use_container_width=True, type="secondary", icon=":material/bar_chart:"):
        st.switch_page("./pages/admin_dashboard_report.py")

    if st.button("Cerrar sesión", use_container_width=True):
        st.session_state["username"] = ""
        st.switch_page('main.py')