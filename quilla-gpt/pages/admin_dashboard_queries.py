import streamlit as st
import pymysql
import hashlib
import time

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


#cargar el archivo css y llamarla
def cargar_css(file_path):
    with open(file_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
cargar_css("./style.css")

container_inicio = st.container()
container_inicio.write("")
container_inicio.write("")
container_inicio.title("Banco de Consultas")

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