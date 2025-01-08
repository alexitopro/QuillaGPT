import streamlit as st
import pymysql
import hashlib
import time
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(
    layout = "wide",
    page_title = "QuillaGPT"
)

#conexion en mysql
conn = pymysql.connect(
    host=st.secrets["mysql"]["host"],
    user=st.secrets["mysql"]["username"],
    password=st.secrets["mysql"]["password"],
    database=st.secrets["mysql"]["database"]
)

#crear la variable de ID tabla para poder reiniciar la seleccion
if "tabla_id" not in st.session_state:
    st.session_state.tabla_id = 0

#modal para revisar la consulta del estudiante
@st.dialog("Detalle de la consulta")
def verDetalle():

    st.text_input("**Tema**", value=tabla.selected_rows.iloc[0]["Tema"], disabled=True)

    st.text_area("**Consulta del estudiante**", value=tabla.selected_rows.iloc[0]["Consulta"], disabled=True)

    if tabla.selected_rows.iloc[0]["Estado"] == "Resuelta":
        respuesta = st.text_area("**Respuesta**", value=tabla.selected_rows.iloc[0]["Respuesta"], disabled = True)
    else:
        respuesta = st.text_area("**Respuesta**", placeholder="Ingrese la respuesta a la consulta...")
        col1, col2 = st.columns([4, 2])
        with col2:
            if st.button("Guardar cambios", type="primary"):
                cursor = conn.cursor()
                query = """
                    UPDATE RequestQuery
                    SET reply = %s, resolved = 1
                    WHERE request_query_id = %s and active = 1
                """
                cursor.execute(query, (respuesta, tabla.selected_rows.iloc[0]["ID"]))
                conn.commit()
                st.session_state.tabla_id += 1
                st.rerun()

#cargar el archivo css y llamarla
def cargar_css(file_path):
    with open(file_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
cargar_css("./style.css")

container_inicio = st.container()
container_inicio.write("")
container_inicio.write("")
container_inicio.title("Banco de Consultas")

cursor = conn.cursor()
query = """
    SELECT request_query_id, register_date, classification, query, IF(reply IS NULL, '-', reply), IF(resolved = 1, 'Resuelta', 'Pendiente') AS status
    FROM RequestQuery
    WHERE active = 1
"""
cursor.execute(query)
data = cursor.fetchall()
df = pd.DataFrame(data, columns=["ID", "Fecha de registro", "Tema", "Consulta", "Respuesta", "Estado"])
df['Fecha de registro'] = pd.to_datetime(df['Fecha de registro'], format="%d/%m/%Y")

builder = GridOptionsBuilder.from_dataframe(df)
builder.configure_default_column(filter=True)
builder.configure_selection(selection_mode='single', use_checkbox=True)

filter_model = {
    "Consulta": {
        "filterType": "text",
        "type": "equals",   # Change 'contains' to 'equals' or other types if needed
        "filter": "cac"  # The preset filter value
    }
}

# builder.configure_column("Fecha de registro", type=["customDateTimeFormat"], custom_format_string='dd-MM-yyyy')
grid_options = builder.build()

grid_options["filterModel"] = filter_model

builder.configure_auto_height(True)
tabla = AgGrid(df, gridOptions = grid_options, key = str(st.session_state.tabla_id), fit_columns_on_grid_load=True)
if tabla.selected_rows is not None:
    verDetalle()

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

with st.sidebar:
    # cargar_css("./style.css")
    st.title("Bienvenido, "+ f":blue[{st.session_state["username"]}]!")
    
    if st.button("Gestión de Usuarios", use_container_width=True, type="secondary", icon=":material/group:"):
        st.switch_page("./pages/admin_dashboard_users.py")

    if st.button("Gestión de Conocimiento", use_container_width=True, icon=":material/description:", type="secondary"):
        st.switch_page("./pages/admin_dashboard_knowledge.py")

    st.button("Banco de Consultas", use_container_width=True, icon=":material/question_answer:", disabled=True)

    if st.button("Reporte de Indicadores", use_container_width=True, icon=":material/bar_chart:", type="secondary"):
        st.switch_page("./pages/admin_dashboard_report.py")

    st.header("Opciones")
    if st.button("Configuración del usuario", use_container_width=True, icon=":material/settings:"):
        config_user()
    if st.button("Cerrar sesión", use_container_width=True, type="primary", icon=":material/logout:"):
        st.session_state["username"] = ""
        st.switch_page('main.py')