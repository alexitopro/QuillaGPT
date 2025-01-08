from document_embedding_process import procesar_arch_db
from document_vectordb_deletion import eliminar_arch_db
import streamlit as st
import pymysql
import pandas as pd
import hashlib
import time
from datetime import datetime

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

#modal para la configuracion del usuario
@st.dialog("Configuración del usuario")
def config_user():
    with st.form("Perfil del usuario", border=False, enter_to_submit=True):
        st.text_input("**Nombre de usuario**", value=st.session_state["username"], disabled=True)
        nueva_contra = st.text_input("**Cambiar contraseña**", placeholder="Nueva contraseña", type="password", help="La contraseña debe tener por lo menos 8 caracteres, una mayúscula, una minúscula y un número.")
        repetir_contra = st.text_input(" ", placeholder="Repetir nueva contraseña", type="password", label_visibility="collapsed")
        actual_contra = st.text_input(" ", placeholder="Contraseña actual", type="password", label_visibility="collapsed")

        col1, col2 = st.columns([3, 2])
        with col2:
            submitted = st.form_submit_button("Guardar cambios", use_container_width=True, type="primary")
            #validar los campos ingresados
        flag = ""
        if submitted:
            if not nueva_contra:
                flag = "Debes ingresar tu nueva contraseña."
            elif not repetir_contra:
                flag = "Debes repetir tu nueva contraseña."
            elif not actual_contra:
                flag = "Debes ingresar tu contraseña actual."
            elif nueva_contra != repetir_contra:
                flag = "Las contraseñas ingresadas no coinciden."
            #contraseña debe tener por lo menos 8 caracteres, una mayuscula, una minuscula y un número
            elif not any(char.isupper() for char in nueva_contra):
                flag = "La contraseña debe tener por lo menos una letra mayúscula."
            elif not any(char.islower() for char in nueva_contra):
                flag = "La contraseña debe tener por lo menos una letra minúscula."
            elif not any(char.isdigit() for char in nueva_contra):
                flag = "La contraseña debe tener por lo menos un número."
            elif len(nueva_contra) < 8:
                flag = "La contraseña debe tener por lo menos 8 caracteres."
            else:
                cursor = conn.cursor()
                query = """
                    SELECT password
                    FROM User
                    WHERE username = %s
                    AND active = 1
                """
                cursor.execute(query, st.session_state["username"])
                contra_hasheada = cursor.fetchone()[0]
                actual_contra_hasheada = hashlib.sha256(actual_contra.encode()).hexdigest()
                if contra_hasheada != actual_contra_hasheada:
                    flag = "La contraseña actual ingresada es incorrecta."
                else:
                    nueva_contra_hasheada = hashlib.sha256(nueva_contra.encode()).hexdigest()
                    query = """
                        UPDATE User
                        SET password = %s
                        WHERE username = %s
                        AND active = 1
                    """
                    cursor.execute(query, (nueva_contra_hasheada, st.session_state["username"]))
                    conn.commit()
                    bandera = st.success("Tus cambios han sido guardados correctamente.")
                    time.sleep(4)
                    bandera.empty()
                    st.rerun()
            if flag:
                error = st.error(flag)
                time.sleep(4)
                error.empty()

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
    if "uploader_key_other" not in st.session_state:
        st.session_state["uploader_key_other"] = []
    
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
            procesar_arch_db(document.name, document, 'GuiaPanda_')
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
    document_other =  st.file_uploader("**Cargar otro documento**", type=["pdf"], key=st.session_state["uploader_key_other"])
    if "documents" not in st.session_state:
        st.session_state["documents"] = []

    if document_other is not None and document_other.name not in st.session_state["documents"]:

        bytes_content = document_other.getvalue()
        file_name = document_other.name
        current_date = datetime.now().strftime('%y-%m-%d')

        insert_query = """
            INSERT INTO File (content, name, register_date, type, active)
            VALUES (%s, %s, %s, %s, 1)
        """
        cursor.execute(insert_query, (bytes_content, file_name, current_date, 'DocumentoAdicional'))
        conn.commit()

        #obtenemos el id del archivo ingresado
        query = "SELECT file_id FROM File WHERE name = %s AND type = 'DocumentoAdicional' AND active = 1"
        cursor.execute(query, (file_name,))
        file_id = cursor.fetchone()[0]

        st.toast("El archivo se ha cargado a la base de datos exitosamente. Actualizando la base de datos de QuillaGPT...", icon=":material/sync:")

        #spinner mientras se actualiza en la vectorial bd
        with st.spinner("Actualizando la base de datos de QuillaGPT..."):
            procesar_arch_db(document_other.name, document_other, 'DocumentoAdicional_' + str(file_id) + '_')
            st.toast("Se ha actualizado la base de datos de QuillaGPT exitosamente", icon=":material/check:")
            st.session_state["documents"].append(document_other.name)

    col1, col2 = st.columns([3, 1], vertical_alignment="bottom")
    with col1:
        document_name = st.text_input("**Buscar documento**", placeholder="Ingrese el nombre del archivo", max_chars=100)
    with col2:
        if st.button("Eliminar archivos seleccionados", type="primary", use_container_width=True):
            if st.session_state["uploader_key_other"]:
                for file_id in st.session_state["uploader_key_other"]:
                    delete_query = "UPDATE File SET active = 0 WHERE file_id = %s"
                    cursor.execute(delete_query, (file_id,))
                    conn.commit()
                st.toast("Los archivos han sido eliminados exitosamente. Actualizando la base de datos de QuillaGPT...", icon=":material/sync:")
                with st.spinner("Actualizando la base de datos de QuillaGPT..."):
                    for file_id in st.session_state["uploader_key_other"]:
                        eliminar_arch_db('DocumentoAdicional_' + str(file_id) + '_')
                    st.toast("Se ha actualizado la base de datos de QuillaGPT exitosamente", icon=":material/check:")
                st.session_state["uploader_key_other"] = []
            else:
                st.toast("No se han seleccionado archivos para eliminar", icon=':material/error:')

    query = """
        SELECT 
            file_id as 'ID',
            name as 'Nombre de archivo',
            register_date as 'Fecha de registro'
        FROM File
        WHERE type != 'GuiaConsultaPanda' AND active = 1 AND name LIKE %s
    """
    values = (f"%{document_name}%",)
    cursor.execute(query, values)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns = ['ID', 'Nombre de archivo', 'Fecha de registro'])
    df["Seleccionar"] = False
    df = df[['Seleccionar', 'ID', 'Nombre de archivo', 'Fecha de registro']]

    selected = st.data_editor(
        data = df,
        column_config={
            "Seleccionar": st.column_config.CheckboxColumn(
                "Seleccionar",
                help="Seleccione los documentos que desea eliminar",
                default=False,
            )
        },
        disabled=['ID', 'Nombre de archivo', 'Fecha de registro'],
        hide_index=True,
        use_container_width=True
    )

    #filtramos los usuarios seleccionados
    st.session_state["uploader_key_other"] = [
        row["ID"]
        for idx, row in selected.iterrows()
        if row["Seleccionar"]
    ]

    # if st.session_state["usuarios"]:
    # st.write("Archivos seleccionados:")
    # for usuario in st.session_state["uploader_key_other"]:
    #     st.write(usuario)

with tab3:
    if "disabled" not in st.session_state:
        st.session_state["disabled"] = True
    if "text" not in st.session_state:
        st.session_state.text = ""
    def disable_instructions():
        st.session_state["disabled"] = not st.session_state["disabled"]

    cursor = conn.cursor()
    query = """
        SELECT instruction
        FROM CustomInstruction
        WHERE active = 1
    """
    cursor.execute(query)
    data = cursor.fetchone()
    if not st.session_state.text and data:
        st.session_state.text = data[0]

    def cancel_instructions():
        st.session_state.text = data[0] if data else ""
        disable_instructions()

    def save_instructions(instrucciones):
        if not st.session_state["disabled"]:
            print(instrucciones)
            if data:
                query = """
                    UPDATE CustomInstruction
                    SET instruction = %s
                    WHERE active = 1
                """
                cursor.execute(query, (instrucciones,))
                conn.commit()
            else:
                insert_query = """
                    INSERT INTO CustomInstruction (instruction, active)
                    VALUES (%s, 1)
                """
                cursor.execute(insert_query, (instrucciones,))
                conn.commit()
            st.toast("Las instrucciones personalizadas se han guardado exitosamente", icon=":material/check:")
            st.session_state.text = instrucciones
        disable_instructions()

    st.write("Las instrucciones personalizadas permiten compartir lo que quieras que QuillaGPT deba tener en cuenta al responder. Lo que compartas se tomará en cuenta en las  conversaciones nuevas que los estudiantes de la PUCP tengan con ella.")
    instrucciones = st.text_area("**Instrucciones personalizadas**", height=300, max_chars=None, placeholder="Escribe lo que quieres que sepa QuillaGPT para responder mejor las consultas de los estudiantes...", disabled=st.session_state["disabled"], key = "text", label_visibility="collapsed", value=st.session_state["text"])

    col1, col2, col3 = st.columns([8, 2, 2])
    with col2:
        if not st.session_state["disabled"]:
            st.button("Cancelar" if st.session_state["disabled"] else "Cancelar instrucciones", type="secondary", on_click=cancel_instructions, use_container_width=True)
    with col3:
        st.button("Editar instrucciones" if st.session_state["disabled"] else "Guardar instrucciones", type="primary", on_click=save_instructions, use_container_width=True, args=(instrucciones, ))

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

    st.header("Opciones")
    if st.button("Configuración del usuario", use_container_width=True, icon=":material/settings:"):
        config_user()
    if st.button("Cerrar sesión", use_container_width=True, type="primary", icon=":material/logout:"):
        st.session_state["username"] = ""
        st.switch_page('main.py')