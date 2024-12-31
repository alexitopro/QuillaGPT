from guiapanda_embedding_process import procesar_arch_db
import streamlit as st
import pymysql
import pandas as pd
from datetime import datetime
from streamlit_lottie import st_lottie_spinner
import json

st.set_page_config(
    layout = "wide",
    page_title = "QuillaGPT"
)

#esto es para que el header sea transparente y cuando se haga scroll no malogre
st.markdown(
    """
    <style>
        .stAppHeader {
            background-color: rgba(255, 255, 255, 0.0);  /* Transparent background */
            visibility: visible;  /* Ensure the header is visible */
        }
    </style>
    """,
    unsafe_allow_html=True,
)

#carga de spinner lottie
def load_lottie_json(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

#conexion en mysql
conn = pymysql.connect(
    host=st.secrets["mysql"]["host"],
    user=st.secrets["mysql"]["username"],
    password=st.secrets["mysql"]["password"],
    database=st.secrets["mysql"]["database"]
)

#cargar el archivo css y llamarla
def cargar_css(file_path):
    with open(file_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
cargar_css("./style.css")

container_inicio = st.container()
container_inicio.write("")
# container_inicio.write("")
container_inicio.title("Gestión de Conocimiento")

tab1, tab2, tab3 = st.tabs(["Conocimiento inicial", "Conocimiento dinámico", "Instrucciones personalizadas"])

#conocimiento inicial
with tab1:
    st.write("QuillaGPT tiene en cuenta la información de los procesos académicos y administrativos disponibles públicamente en las siguientes páginas web:")
    st.markdown("""
    - https://sites.google.com/pucp.edu.pe/fci-pucp/estudiantes
    - https://estudiante.pucp.edu.pe/tramites-y-certificaciones/tramites-academicos/?dirigido_a%5B%5D=Estudiantes&unidad%5B%5D=Facultad+de+Ciencias+e+Ingenier%C3%ADa
    - https://facultad-ciencias-ingenieria.pucp.edu.pe/estudiantes/tramites-academicos-y-administrativos/
    """)

#conocimiento dinamico
with tab2:
    st.subheader("Guía de consulta del Panda")
    st.write("QuillaGPT utiliza la Guía del Panda del ciclo actual. Si observas que se está usando una guía de un ciclo anterior, sube el nuevo documento para reemplazar al actual. Recuerda que sólo se aceptan archivos en formato PDF.")
    # #tabla de guia de consulta del panda
    cursor = conn.cursor()

    #esto es para no se vuelva a cargar
    if "uploader_key" not in st.session_state:
        st.session_state["uploader_key"] = 1
    
    #uploader
    document =  st.file_uploader("**Cargar la Guía de Consulta del Panda**", type=["pdf"], key=st.session_state["uploader_key"])
    if document is not None:

        bytes_content = document.getvalue()
        file_name = document.name
        current_date = datetime.now().strftime('%y-%m-%d')

        #eliminamos el archivo antiguo de guia de consulta panda
        delete_query = "UPDATE File SET active = 0 WHERE type = 'GuiaConsultaPanda'"
        cursor.execute(delete_query)

        insert_query = """
            INSERT INTO File (content, name, register_date, type, active)
            VALUES (%s, %s, %s, %s, 1)
        """
        cursor.execute(insert_query, (bytes_content, file_name, current_date, 'GuiaConsultaPanda'))
        conn.commit()

        # st.success("El archivo ha sido cargado exitosamente y reemplazó el anterior")
        st.toast("El archivo se ha cargado a la base de datos exitosamente. Actualizando la base de datos de QuillaGPT...", icon=":material/sync:")

        #spinner mientras se actualiza en la vectorial bd
        with st.spinner("Actualizando la base de datos de QuillaGPT..."):
            procesar_arch_db(document.name, document)
            st.toast("Se ha actualizado la base de datos de QuillaGPT exitosamente", icon=":material/check:")
            st.session_state["uploader_key"] += 1

    query = """
        SELECT 
            name as 'Nombre de archivo',
            register_date as 'Fecha de registro'
        FROM File
        WHERE type = 'GuiaConsultaPanda' AND active = 1
    """
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns = ['Nombre de archivo', 'Fecha de registro'])
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.subheader("Otros documentos")

    st.write("QuillaGPT también puede utilizar otros documentos que consideres pertinentes. Sin embargo, recuerda lo siguiente:")

    st.markdown("""
    - Sólo se aceptan archivos en formato PDF.
    - QuillaGPT solo podrá leer y procesar contenido textual. Si el documento contiene imágenes, gráficos u otros elementos visuales, estos no podrán ser utilizados como conocimiento, ya que el sistema solo puede extraer texto.
    """)

    
    #uploader
    document_other =  st.file_uploader("**Cargar otro documento**", type=["pdf"], key=st.session_state["uploader_key"] + 1)

    if document_other is not None:

        bytes_content = document_other.getvalue()
        file_name = document_other.name
        current_date = datetime.now().strftime('%y-%m-%d')

    col1, col2 = st.columns([3, 1], vertical_alignment="bottom")
    with col1:
        usuario = st.text_input("**Buscar documento**", placeholder="Ingrese el nombre del archivo", max_chars=100)
    with col2:
        st.button("Eliminar archivos seleccionados", type="primary", use_container_width=True)

    query = """
        SELECT 
            name as 'Nombre de archivo',
            register_date as 'Fecha de registro'
        FROM File
        WHERE type != 'GuiaConsultaPanda' AND active = 1
    """
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns = ['Nombre de archivo', 'Fecha de registro'])
    st.dataframe(df, use_container_width=True, hide_index=True)

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

    if st.button("Cerrar sesión", use_container_width=True, type="primary"):
        st.session_state["username"] = ""
        st.switch_page('main.py')