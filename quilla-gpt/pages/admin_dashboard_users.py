import streamlit as st
import pymysql
import hashlib
import time
import pandas as pd

st.set_page_config(
    layout = "wide",
    page_title = "QuillaGPT"
)

# st.markdown("""
# <style>
# 	[data-testid="stDecoration"] {
# 		display: none;
# 	}
# </style>""",
# unsafe_allow_html=True)

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

#inicializar lista de usuarios si no existe
if "usuarios" not in st.session_state:
    st.session_state["usuarios"] = []

#funcion para habilitar usuarios
def habilitar_usuarios():
    if st.session_state["usuarios"]:
        for usuario in st.session_state["usuarios"]:
            cursor = conn.cursor()
            cursor.execute("UPDATE User SET active = 1 WHERE email = %s AND active = 0", (usuario,))
            conn.commit()
            st.session_state["usuarios"] = []
            st.toast("Tus cambios han sido guardados exitosamente", icon=":material/check:")

#funcion para deshabilitar usuarios
def deshabilitar_usuarios():
    if st.session_state["usuarios"]:
        for usuario in st.session_state["usuarios"]:
            cursor = conn.cursor()
            cursor.execute("UPDATE User SET active = 0 WHERE email = %s AND active = 1 AND username != %s", (usuario, st.session_state["username"]))
            conn.commit()
            st.session_state["usuarios"] = []
            st.toast("Tus cambios han sido guardados exitosamente", icon=":material/check:")

#cargar el archivo css y llamarla
def cargar_css(file_path):
    with open(file_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
cargar_css("style.css")

#titulo
container_inicio = st.container()
container_inicio.write("")
container_inicio.write("")
container_inicio.title("Gestión de Usuarios")

#contenido
col1, col2, col3, col4, col5 = st.columns([2.5, 1.5, 1, 2.5, 2.5], vertical_alignment="bottom")
with col1:
    usuario = st.text_input("**Buscar usuario**", placeholder="Ingrese el correo o nombre del usuario", max_chars=50)
with col2:
    rol = st.selectbox("**Rol**", ["Todos", "Administrador", "Estudiante"])
with col3:
    estado = st.selectbox("**Estado**", ["Todos", "Activo", "Inactivo"])
with col4:
    if st.button("Habilitar usuarios seleccionados", type="primary", use_container_width=True):
        habilitar_usuarios()
with col5:
    if st.button("Deshabilitar usuarios seleccionados", type="primary", use_container_width=True):
        deshabilitar_usuarios()

#tabla de usuarios
cursor = conn.cursor()
query = """
    SELECT 
        u.username AS 'Nombre de usuario', 
        u.email AS 'Correo electrónico', 
        r.name AS 'Rol', 
        CASE WHEN u.active = 1 THEN 'Activo' ELSE 'Inactivo' END AS 'Estado'
    FROM User u
    INNER JOIN Role r ON u.role_id = r.role_id
    WHERE (%s = 'Todos' OR r.name = %s)
      AND (%s = 'Todos' OR u.active = %s)
      AND (%s = '' OR u.email LIKE %s OR u.username LIKE %s)
"""
values = (
    rol, rol, 
    estado, 1 if estado == 'Activo' else 0 if estado == 'Inactivo' else None,
    usuario, f"%{usuario}%", f"%{usuario}%"
)

cursor.execute(query, values)
data = cursor.fetchall()

cursor.execute(query, values)
data = cursor.fetchall()
df = pd.DataFrame(data, columns = ['Nombre de usuario', 'Correo electrónico', 'Rol', 'Estado'])
df["Seleccionar"] = False
df = df[['Seleccionar', 'Nombre de usuario', 'Correo electrónico', 'Rol', 'Estado']]

selected = st.data_editor(
    data = df,
    column_config={
        "Seleccionar": st.column_config.CheckboxColumn(
            "Seleccionar",
            help="Seleccionar usuarios que se desean habilitar o deshabilitar",
            default=False,
        )
    },
    disabled=['Nombre de usuario', 'Correo electrónico', 'Rol', 'Estado'],
    hide_index=True,
    use_container_width=True
)

#filtramos los usuarios seleccionados
st.session_state["usuarios"] = [
    row["Correo electrónico"]
    for idx, row in selected.iterrows()
    if row["Seleccionar"]
]

# if st.session_state["usuarios"]:
#     st.write("Usuarios seleccionados:")
    # for usuario in st.session_state["usuarios"]:
    #     st.write(usuario)

with st.sidebar:
    # cargar_css("./style.css")
    st.title("Bienvenido, "+ f":blue[{st.session_state["username"]}]!")
    
    st.button("Gestión de Usuarios", use_container_width=True, icon=":material/group:", disabled=True)

    if st.button("Gestión de Conocimiento", use_container_width=True, type="secondary", icon=":material/description:"):
        st.switch_page("./pages/admin_dashboard_knowledge.py")

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