import streamlit as st
from streamlit_navigation_bar import st_navbar
import requests as req
import json
from datetime import datetime
from utils.document_embedding_process import procesar_arch_db
from utils.document_vectordb_deletion import eliminar_arch_db
from utils.create_embeddings import create_web_scraping_embeddings
from utils.scraper import scraper
import time
import base64
from PIL import Image
from io import BytesIO

#BARRA DE NAVEGACION
styles = {
    "nav": {
        "background-color": "#00205B",
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
    page_title = "PandaGPT"
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
    st.session_state.page_session = " "
    with col2:
        image_url = st.session_state.user["picture"]
        response = req.get(image_url)
        image = Image.open(BytesIO(response.content))
        st.image(image, width=100)
    st.text_input("**Nombre de usuario**", value=st.session_state["username"], disabled=True)
    st.text_input("**Correo electrónico**", value=st.session_state.user["email"], disabled=True)
    st.text_input("**Rol**", value="Administrador" if st.session_state.role_id == 1 else "Estudiante", disabled=True)

if page == "Mi cuenta":
    config_user()
    # st.session_state.page_session = "Mi cuenta"
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
container_inicio.title("Gestión del Conocimiento", anchor=False)

tab1, tab2, tab3 = st.tabs(["Conocimiento base", "Conocimiento dinámico", "Instrucciones personalizadas"])

def cargar_css(file_path):
    with open(file_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
cargar_css("style.css")

#conocimiento inicial
with tab1:

    st.subheader("Sitios web de referencias", help="PandaGPT tiene en cuenta la información de los procesos académicos y administrativos disponibles de manera pública en las páginas web listadas", anchor=False)

    st.markdown("""
        - <a style='display: block;' href="https://estudiante.pucp.edu.pe/tramites-y-certificaciones/tramites-academicos/?dirigido_a%5B%5D=Estudiantes&unidad%5B%5D=Facultad+de+Ciencias+e+Ingenier%C3%ADa">Trámites académicos dirigidos a estudiantes de la PUCP</a>
        - <a style='display: block;' href="https://facultad-ciencias-ingenieria.pucp.edu.pe/estudiantes/tramites-academicos-y-administrativos/">Trámites académicos dirigidos a estudiantes de la Facultad de Ciencias e Ingeniería</a>
        - <a style='display: block;' href="https://sites.google.com/pucp.edu.pe/fci-pucp/estudiantes">Google Sites de la Facultad de Ciencias e Ingeniería</a>
    """, unsafe_allow_html=True)

    st.subheader("Proceso de actualización de información", anchor=False)

    st.write("""
La actualización del conocimiento garantiza que la información esté al día si los sitios web listados han cambiado.
             
El proceso incluye los siguientes pasos:

1. Revisión automatizada de las páginas indicadas.
2. Extracción de los trámites y procesos administrativos.
3. Guardado de los datos para que PandaGPT los utilice en sus respuestas.

Recuerda que este proceso puede tardar algunos minutos en completarse.""")

    if 'run_button' in st.session_state and st.session_state.run_button == True:
        st.session_state.running = True
    else:
        st.session_state.running = False

    if st.button('Actualizar información', disabled=st.session_state.running, key='run_button', icon=":material/sync:", type="secondary"):
        status = st.progress(0, text="Extrayendo datos de la Facultad de Ciencias e Ingeniería...")
        scraper()
        status.progress(0.60, text="Actualizando base de datos de PandaGPT...")
        create_web_scraping_embeddings()
        status.progress(0.99, text="Actualización completada exitosamente...")
        time.sleep(3)
        st.rerun()

#conocimiento dinamico
with tab2:

    st.subheader("Documentos digitales", anchor=False)

    with st.container(border=True):
        st.write("PandaGPT también puede usar documentos adicionales como conocimiento. Sin embargo, ten en cuenta las siguientes consideraciones:")

        st.markdown("""
        - **Formato de archivos:** Sólo se aceptan archivos en formato PDF estructurado.
        - **Contenido:** PandaGPT solo es capaz de procesar texto; no tiene la capacidad de interpretar imágenes o gráficos.
        - **Actualización de documentos:** Si deseas subir un archivo con el mismo nombre que uno ya existente, asegúrate de eliminar el más antiguo para evitar inconsistencias en las respuestas de PandaGPT.
        - **Eliminación de documentos:** No olvides de borrar aquellos documentos que ya no sean relevantes para el período actual.
        """)

    st.write("")

    #esto es para no se vuelva a cargar
    if "uploader_key_other" not in st.session_state:
        st.session_state["uploader_key_other"] = []

    if "documents" not in st.session_state:
        st.session_state["documents"] = []

    #cargar archivos adicionales
    document =  st.file_uploader("**Cargar documento digital**", type=["pdf"], key=st.session_state["uploader_key_other"])

    if document is not None and document.name not in st.session_state["documents"]:
        bytes_content = document.getvalue()
        encoded_content = base64.b64encode(bytes_content).decode('utf-8')
        file_name = document.name
        current_date = datetime.now().strftime('%y-%m-%d')
        input = {"contenido" : encoded_content, "filename" : file_name, "current_date" : current_date, "correo" : st.session_state.user["email"]}
        result = req.post(url="http://127.0.0.1:8000/CargarDocumento", data = json.dumps(input))
        file_id = result.json()
        st.toast("El archivo se ha cargado a la base de datos exitosamente. Actualizando la base de datos de PandaGPT...", icon=":material/sync:")
        #spinner mientras se actualiza en la vectorial bd
        with st.spinner("Actualizando la base de datos de PandaGPT..."):
            procesar_arch_db(document.name, document, 'DocumentoAdicional_' + str(file_id) + '_')
            st.toast("Se ha actualizado la base de datos de PandaGPT exitosamente", icon=":material/check:")
            st.session_state["documents"].append(document.name)

    #anadir css para el buscador
    st.markdown("""
        <link rel="stylesheet" 
            href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
                
        <script>
            function triggerSearch() {
                const searchBox = document.querySelector('div[data-testid="stTextInput"] input');
                searchBox.dispatchEvent(new Event('input', { bubbles: true }));
            }
        </script>

        <style>
        div[data-testid="stTextInput"] {
            position: relative;
        }
        div[data-testid="stTextInput"] input {
            padding-right: 35px;
        }
        div[data-testid="stTextInput"]::after {
            content: "search";
            font-family: 'Material Symbols Outlined';
            font-size: 20px;
            position: absolute;
            right: 10px;
            top: 50%;
            color: gray;
            cursor: pointer;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([0.75, 1], vertical_alignment="bottom")
    with col1:
        document_name = st.text_input("**Buscar documento**", placeholder="Ingrese el nombre del archivo", max_chars=80)
    # with col2:
    #     if st.button("Eliminar archivos seleccionados", type="primary", use_container_width=True):
    #         if st.session_state["uploader_key_other"]:
    #             for file_id in st.session_state["uploader_key_other"]:
    #                 req.delete(f"http://127.0.0.1:8000/File/{file_id}")

    #             st.toast("Los archivos han sido eliminados exitosamente. Actualizando la base de datos de PandaGPT...", icon=":material/sync:")
    #             with st.spinner("Actualizando la base de datos de PandaGPT..."):
    #                 for file_id in st.session_state["uploader_key_other"]:
    #                     eliminar_arch_db('DocumentoAdicional_' + str(file_id) + '_')
    #                 st.toast("Se ha actualizado la base de datos de PandaGPT exitosamente", icon=":material/check:")
    #             st.session_state["uploader_key_other"] = []
    #         else:
    #             st.toast("No se han seleccionado archivos para eliminar", icon=':material/error:')

    def borrarArchivos(file_id):
        with st.spinner(""):
            req.delete(f"http://127.0.0.1:8000/File/{data_files[i][0]}")
            st.toast("Los archivos han sido eliminados exitosamente. Actualizando la base de datos de PandaGPT...", icon=":material/sync:")
            eliminar_arch_db('DocumentoAdicional_' + str(file_id) + '_')
            st.toast("Se ha actualizado la base de datos de PandaGPT exitosamente", icon=":material/check:")
            st.session_state["uploader_key_other"] = []

    result_files = req.get(f"http://127.0.0.1:8000/File/{document_name}")
    data_files = result_files.json()

    if not data_files and document_name != "":
        st.caption("No se encontraron documentos con el nombre de documento ingresado.")
    elif not data_files:
        st.caption("No hay documentos registrados en la base de datos.")
    else:
        for i in range(len(data_files)):
            with st.container(border=True, key="container"+str(i)):
                col_cont1, col_cont2 = st.columns([4, 0.25], vertical_alignment
                ="center")
                with col_cont1:
                    st.subheader(data_files[i][1], anchor=False)
                    st.write(f"**Responsable del documento:** {data_files[i][4]}")
                    st.write(f"**Tamaño del documento:** {data_files[i][2]} MB")
                    st.write(f"**Fecha de registro:** {data_files[i][3]}")
                    st.write("")
                with col_cont2:
                    if st.button("", key="borrar"+str(i), type="secondary", icon=":material/delete:"):
                        borrarArchivos(data_files[i][0])
                        st.rerun()

    # df = pd.DataFrame(data_files, columns = ['ID', 'Nombre de documento', 'Tamaño del documento (MB)', 'Fecha de registro'])
    # df["Seleccionar"] = False
    # df = df[['Seleccionar', 'ID', 'Nombre de documento', 'Tamaño del documento (MB)', 'Fecha de registro']]

    # selected = st.data_editor(
    #     data = df,
    #     column_config={
    #         "Seleccionar": st.column_config.CheckboxColumn(
    #             "Seleccionar",
    #             help="Seleccione los documentos que desea eliminar",
    #             default=False,
    #         )
    #     },
    #     disabled=['ID', 'Nombre de documento', 'Tamaño del documento (MB)', 'Fecha de registro'],
    #     hide_index=True,
    #     use_container_width=True
    # )

    #filtramos los usuarios seleccionados
    # st.session_state["uploader_key_other"] = [
    #     row["ID"]
    #     for idx, row in selected.iterrows()
    #     if row["Seleccionar"]
    # ]

with tab3:

    st.subheader("Instrucciones personalizadas", anchor=False)

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

    def save_instructions():
        if not st.session_state["disabled"]:
            req.put(url = "http://127.0.0.1:8000/ActualizarInstrucciones")
            input = {"instruccion" : st.session_state.text, "correo" : st.session_state.user["email"]}
            print(input)
            req.post(url = "http://127.0.0.1:8000/CustomInstruction", data = json.dumps(input))
            st.toast("Las instrucciones personalizadas se han guardado exitosamente", icon=":material/check:")
        disable_instructions()

    st.write("Las instrucciones personalizadas permiten compartir lo que quieras que PandaGPT deba tener en cuenta al responder. Lo que compartas se tomará en cuenta en las conversaciones nuevas que los estudiantes de la PUCP tengan con él.")

    instrucciones = st.text_area("**Instrucciones personalizadas**", height=450, max_chars=None, placeholder="Escribe lo que quieres que sepa PandaGPT para responder mejor las consultas de los estudiantes...", disabled=st.session_state["disabled"], label_visibility="collapsed", key="text")
    
    col1, col2, col3 = st.columns([8, 2, 2])
    with col2:
        if not st.session_state["disabled"]:
            st.button("Cancelar" if st.session_state["disabled"] else "Cancelar instrucciones", type="secondary", on_click=cancel_instructions, use_container_width=True)
    with col3:
        st.button("Editar instrucciones" if st.session_state["disabled"] else "Guardar instrucciones", type="primary", on_click=save_instructions, use_container_width=True)

    st.subheader("Historial de instrucciones personalizadas", anchor=False)

    result_instrucciones = req.get(url="http://127.0.0.1:8000/ListarInstruccionesInactivas")

    data_instrucciones = result_instrucciones.json()
    instrucciones_por_fecha = {}
    if data_instrucciones:

        for instruccion in data_instrucciones:
            fecha = instruccion[1]
            if fecha not in instrucciones_por_fecha:
                instrucciones_por_fecha[fecha] = []
            instrucciones_por_fecha[fecha].append(instruccion)

        for fecha, instrucciones in instrucciones_por_fecha.items():
            with st.expander(f"Instrucciones del {fecha}", expanded=False):
                # df = pd.DataFrame(
                #     [
                #         {"Instrucción": instruccion[0], 
                #          "Registrado por": instruccion[3]}
                #         for instruccion in instrucciones
                #     ]
                # )
                # st.table(df)
                for instruccion in instrucciones:
                    with st.container(border=True):
                        st.write(f"**Instrucción:** {instruccion[0]}")
                        st.write(f"**Registrado por:** {instruccion[3]}")
                        st.write(f"**Correo del usuario:** {instruccion[2]}") 
    else:
        st.caption("No hay instrucciones personalizadas anteriores registradas")

obtenerContador = req.get(url="http://127.0.0.1:8000/ObtenerContadorSolicitudes")
contadorRequests = obtenerContador.json()

if "support_requests" not in st.session_state:
    st.session_state.support_requests = contadorRequests
else:
    st.session_state.support_requests = contadorRequests

button_text = "Solicitudes de Soporte"
if st.session_state.support_requests > 0:
    button_text += f" ({st.session_state.support_requests})"

with st.sidebar:
    st.markdown(
        f"""
        <h1 style="color:#00205B;">Bienvenido, {st.session_state["username"]}!</h1>
        """,
        unsafe_allow_html=True
    )

    st.write("")
    
    if st.button("Gestión de Usuarios", use_container_width=True, type="secondary", icon=":material/group:"):
        st.switch_page("./pages/dashboard_users.py")

    st.button("Gestión del Conocimiento", use_container_width=True, icon=":material/description:", type="primary")

    if st.button(button_text, use_container_width=True, type="secondary", icon=":material/question_answer:"):
        st.switch_page("./pages/dashboard_queries.py")

    if st.button("Reporte de Indicadores", use_container_width=True, type="secondary", icon=":material/bar_chart:"):
        st.switch_page("./pages/dashboard_report.py")