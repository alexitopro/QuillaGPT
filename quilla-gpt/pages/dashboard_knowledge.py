import streamlit as st
from streamlit_navigation_bar import st_navbar
import requests as req
import json
import pandas as pd
from datetime import datetime
from utils.document_embedding_process import procesar_arch_db
from utils.document_vectordb_deletion import eliminar_arch_db
from utils.create_embeddings import create_web_scraping_embeddings
from utils.scraper import scraper
import time
import base64

#BARRA DE NAVEGACION
styles = {
    "nav": {
        "background-color": "#31333F",
        "justify-content": "space-between"
    },
    "div": {
        "max-width": "40rem",
    },
    "span": {
        "border-radius": "0.5rem",
        "color": "#E5E5EA",
        "margin": "0 0.125rem",
        "padding": "0.4375rem 0.625rem",
        "font-family": "sans-serif",
    },
    "active": {
        "font-weight": "normal",
    },
    "hover": {
        "background-color": "rgba(255, 255, 255, 0.5)",
    },
}

icons = {
    "Mi cuenta": ":material/account_circle:",
    "Cerrar sesión": ":material/logout:",
    "Panel de Administrador": ":material/switch_account:",
    "Panel de Estudiante": ":material/switch_account:",
}

st.set_page_config(
    layout = "wide",
    page_title = "QuillaGPT"
)

if "page_session" not in st.session_state:
    st.session_state.page_session = " "

#crear la variable de ID tabla para poder reiniciar la seleccion
if "tabla_id" not in st.session_state:
    st.session_state.tabla_id = 0

# CONTENIDO DEL NAV BAR
page = st_navbar(
    [],
    right=[" ", "Panel de Estudiante", "Mi cuenta", "Cerrar sesión"],
    styles=styles,
    icons=icons,
    options={"fix_shadow": False},
    selected= st.session_state.page_session
)

#modal de configuracion del usuario
@st.dialog("Mi cuenta")
def config_user():
    col1, col2, col3 = st.columns([1, 0.75, 1])
    with col2:
        st.image(st.session_state.user["picture"], width=100)
    st.text_input("**Nombre de usuario**", value=st.session_state["username"], disabled=True)
    st.text_input("**Correo electrónico**", value=st.session_state.user["email"], disabled=True)
    st.text_input("**Rol**", value="Administrador" if st.session_state.role_id == 1 else "Estudiante", disabled=True)

if page == "Mi cuenta":
    config_user()
    st.session_state.page_session = "Mi cuenta"
elif page == "Cerrar sesión":
    st.session_state.page_session = " "
    st.session_state["username"] = ""
    st.session_state.messages = []
    st.session_state["user"] = None
    st.session_state["credentials"] = None
    st.session_state.feedback_response = False
    st.switch_page('main.py')
elif page == "Panel de Estudiante":
    st.session_state.page_session = " "
    st.switch_page('./pages/quillagpt.py')

#cargar el archivo css y llamarla
def cargar_css(file_path):
    with open(file_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
cargar_css("style.css")

#titulo
container_inicio = st.container()
container_inicio.write("")
container_inicio.write("")
container_inicio.write("")
container_inicio.write("")
container_inicio.write("")
container_inicio.write("")
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
    st.subheader("¿Deseas actualizar la información disponible?", anchor=False)
    st.write("""
El proceso de actualización incluye los siguientes pasos:

1. Revisión automática de las páginas previamente mencionadas.
2. Identificación y extracción de los trámites y procesos administrativos según la página correspondiente.
3. Almacenamiento de datos en la base de datos para que QuillaGPT pueda utilizarlos en respuestas a consultas de los estudiantes.

Haz clic en el botón de abajo para asegurarte de tener los datos más recientes. Recuerda que este proceso puede tardar algunos minutos en completarse.""")

    if 'run_button' in st.session_state and st.session_state.run_button == True:
        st.session_state.running = True
    else:
        st.session_state.running = False

    if st.button('Actualizar información', disabled=st.session_state.running, key='run_button', icon=":material/sync:", type="secondary"):
        status = st.progress(0, text="Extrayendo datos de la Facultad de Ciencias e Ingeniería...")
        scraper()
        status.progress(0.60, text="Actualizando base de datos de QuillaGPT...")
        create_web_scraping_embeddings()
        status.progress(0.99, text="Actualización completada exitosamente...")
        time.sleep(3)
        st.rerun()

#conocimiento dinamico
with tab2:
    st.write("QuillaGPT puede utilizar otros documentos que consideres pertinentes como conocimiento adicional. Para ello, debes tomar en cuenta las siguientes consideraciones:")

    st.markdown("""
    - **Formato de archivo:** Sólo se aceptan archivos en formato PDF.
    - **Procesamiento de contenido:** QuillaGPT solo puede leer y procesar contenido textual. Si el documento incluye imágenes, gráficos u otros elementos visuales, estos no podrán ser interpretados, ya que el sistema solo extrae texto.
    - **Actualización de documentos:** Si subes un documento cuyo nombre del archivo ya está registrado en la base de datos, por favor elimina el documento de mayor antigüedad. Caso contrario, QuillaGPT considerará ambos documentos en sus respuestas.
    - **Eliminación de documentos:** Si identificas uno o más documentos que ya no tienen vigencia para el ciclo académico actual, puedes seleccionarlos y eliminarlos de la base de datos.
    """)

    st.write("")

    #esto es para no se vuelva a cargar
    if "uploader_key_other" not in st.session_state:
        st.session_state["uploader_key_other"] = []

    if "documents" not in st.session_state:
        st.session_state["documents"] = []

    #cargar archivos adicionales
    document =  st.file_uploader("**Cargar documento adicional**", type=["pdf"], key=st.session_state["uploader_key_other"])

    if document is not None and document.name not in st.session_state["documents"]:
        bytes_content = document.getvalue()
        encoded_content = base64.b64encode(bytes_content).decode('utf-8')
        file_name = document.name
        current_date = datetime.now().strftime('%y-%m-%d')
        input = {"contenido" : encoded_content, "filename" : file_name, "current_date" : current_date}
        result = req.post(url="http://127.0.0.1:8000/CargarDocumento", data = json.dumps(input))
        file_id = result.json()
        st.toast("El archivo se ha cargado a la base de datos exitosamente. Actualizando la base de datos de QuillaGPT...", icon=":material/sync:")
        #spinner mientras se actualiza en la vectorial bd
        with st.spinner("Actualizando la base de datos de QuillaGPT..."):
            procesar_arch_db(document.name, document, 'DocumentoAdicional_' + str(file_id) + '_')
            st.toast("Se ha actualizado la base de datos de QuillaGPT exitosamente", icon=":material/check:")
            st.session_state["documents"].append(document.name)

    col1, col2 = st.columns([3, 1], vertical_alignment="bottom")
    with col1:
        document_name = st.text_input("**Buscar documento**", placeholder="Ingrese el nombre del archivo", max_chars=100)
    with col2:
        if st.button("Eliminar archivos seleccionados", type="primary", use_container_width=True):
            if st.session_state["uploader_key_other"]:
                for file_id in st.session_state["uploader_key_other"]:
                    req.delete(f"http://127.0.0.1:8000/File/{file_id}")

                st.toast("Los archivos han sido eliminados exitosamente. Actualizando la base de datos de QuillaGPT...", icon=":material/sync:")
                with st.spinner("Actualizando la base de datos de QuillaGPT..."):
                    for file_id in st.session_state["uploader_key_other"]:
                        eliminar_arch_db('DocumentoAdicional_' + str(file_id) + '_')
                    st.toast("Se ha actualizado la base de datos de QuillaGPT exitosamente", icon=":material/check:")
                st.session_state["uploader_key_other"] = []
            else:
                st.toast("No se han seleccionado archivos para eliminar", icon=':material/error:')

    if document_name:
        result_files = req.get("http://127.0.0.1:8000/File/")
    else:
        result_files = req.get(f"http://127.0.0.1:8000/File/{document_name}")
    data_files = result_files.json()
    df = pd.DataFrame(data_files, columns = ['ID', 'Nombre de documento', 'Tamaño del documento (MB)', 'Fecha de registro'])
    df["Seleccionar"] = False
    df = df[['Seleccionar', 'ID', 'Nombre de documento', 'Tamaño del documento (MB)', 'Fecha de registro']]

    selected = st.data_editor(
        data = df,
        column_config={
            "Seleccionar": st.column_config.CheckboxColumn(
                "Seleccionar",
                help="Seleccione los documentos que desea eliminar",
                default=False,
            )
        },
        disabled=['ID', 'Nombre de documento', 'Tamaño del documento (MB)', 'Fecha de registro'],
        hide_index=True,
        use_container_width=True
    )

    #filtramos los usuarios seleccionados
    st.session_state["uploader_key_other"] = [
        row["ID"]
        for idx, row in selected.iterrows()
        if row["Seleccionar"]
    ]

with tab3:
    if "disabled" not in st.session_state:
        st.session_state["disabled"] = True
    if "text" not in st.session_state:
        st.session_state.text = ""
    def disable_instructions():
        st.session_state["disabled"] = not st.session_state["disabled"]

    result_files = req.get("http://127.0.0.1:8000/CustomInstruction/")
    data = result_files.json()

    if not st.session_state.text and data:
        st.session_state.text = data

    def cancel_instructions():
        st.session_state.text = data
        disable_instructions()

    def save_instructions(instrucciones):
        if not st.session_state["disabled"]:
            input = {"instruccion" : instrucciones}
            req.post(url = "http://127.0.0.1:8000/CustomInstruction", data = json.dumps(input))
            st.toast("Las instrucciones personalizadas se han guardado exitosamente", icon=":material/check:")
            st.session_state.text = instrucciones
        disable_instructions()

    st.write("Las instrucciones personalizadas permiten compartir lo que quieras que QuillaGPT deba tener en cuenta al responder. Lo que compartas se tomará en cuenta en las  conversaciones nuevas que los estudiantes de la PUCP tengan con ella.")

    instrucciones = st.text_area("**Instrucciones personalizadas**", height=500, max_chars=None, placeholder="Escribe lo que quieres que sepa QuillaGPT para responder mejor las consultas de los estudiantes...", disabled=st.session_state["disabled"], label_visibility="collapsed", key="text")

    col1, col2, col3 = st.columns([8, 2, 2])
    with col2:
        if not st.session_state["disabled"]:
            st.button("Cancelar" if st.session_state["disabled"] else "Cancelar instrucciones", type="secondary", on_click=cancel_instructions, use_container_width=True)
    with col3:
        st.button("Editar instrucciones" if st.session_state["disabled"] else "Guardar instrucciones", type="primary", on_click=save_instructions, use_container_width=True, args=(instrucciones, ))

    st.subheader("Historial de instrucciones personalizadas")

    result_instrucciones = req.get(url="http://127.0.0.1:8000/ListarInstruccionesInactivas")
    data_instrucciones = result_instrucciones.json()

    df = pd.DataFrame(data_instrucciones, columns = ['Instrucción', 'Estado'])
    st.table(df)

with st.sidebar:
    st.title("Bienvenido, "+ f":blue[{st.session_state["username"]}]!")

    st.write("")
    
    if st.button("Gestión de Usuarios", use_container_width=True, type="secondary", icon=":material/group:"):
        st.switch_page("./pages/dashboard_users.py")

    st.button("Gestión de Conocimiento", use_container_width=True, icon=":material/description:", disabled=True)

    if st.button("Solicitudes de Soporte", use_container_width=True, type="secondary", icon=":material/question_answer:"):
        st.switch_page("./pages/dashboard_queries.py")

    if st.button("Reporte de Indicadores", use_container_width=True, type="secondary", icon=":material/bar_chart:"):
        st.switch_page("./pages/dashboard_report.py")