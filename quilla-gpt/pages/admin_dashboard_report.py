import streamlit as st
import pymysql
import hashlib
import time
import pandas as pd
import altair as alt
import plotly.express as px

st.set_page_config(
    layout = "wide",
    page_title = "QuillaGPT"
)

#cargar el archivo css y llamarla
def cargar_css(file_path):
    with open(file_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
cargar_css("./style.css")

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

container_inicio = st.container()
container_inicio.write("")
container_inicio.write("")
container_inicio.title("Reporte de Indicadores")

col1, col2, col3, col4 = st.columns(4, vertical_alignment="center")
with col1:
    cursor = conn.cursor()
    query = """
        SELECT COUNT(*)
        FROM Session
        WHERE
            start_session >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
            AND start_session < DATE_FORMAT(DATE_ADD(CURDATE(), INTERVAL 1 MONTH), '%Y-%m-01')
    """
    cursor.execute(query)
    sesiones_mes = cursor.fetchone()[0]
    st.metric(label = "**Conversaciones en el mes**", value = sesiones_mes, border=True)
with col2:
    cursor = conn.cursor()
    query = """
        SELECT 
            ROUND((COUNT(CASE WHEN derived = 1 THEN 1 END) * 100.0 / COUNT(*)), 2) AS porcentaje_consultas_derivadas
        FROM 
            Message
        WHERE 
        register_date >= DATE_FORMAT(CURRENT_DATE, '%Y-%m-01') 
        AND register_date < DATE_FORMAT(CURRENT_DATE + INTERVAL 1 MONTH, '%Y-%m-01') AND active = 1 AND role = 'assistant';
    """
    cursor.execute(query)
    porcentaje_derivadas = cursor.fetchone()[0]
    if porcentaje_derivadas is None:
        porcentaje_derivadas = 0
    st.metric(label = "**Ratio de consultas derivadas en el mes**", value = str(round(porcentaje_derivadas)) + '%', border=True)
with col3:
    cursor = conn.cursor()
    query = """
        SELECT 
            AVG(d.conteo_usuario) AS prom_usuario_activos
        FROM (
            SELECT 
                DATE(start_session) AS dia_interaccion,
                COUNT(DISTINCT user_id) AS conteo_usuario
            FROM 
                Session
            GROUP BY 
                DATE(start_session)
        ) AS d;
    """
    cursor.execute(query)
    cant_admins = cursor.fetchone()[0]
    if cant_admins is None:
        cant_admins = 0
    st.metric(label = "**Promedio de estudiantes activos**", value = int(cant_admins), border=True)
with col4:
    cursor = conn.cursor()
    query = """
        SELECT COUNT(*)
        FROM User
        WHERE active = 1
        AND role_id = 2
    """
    cursor.execute(query)
    cant_usuarios = cursor.fetchone()[0]
    st.metric(label = "**Estudiantes registrados**", value = cant_usuarios, border=True)

col1_columna, col2_columna2 = st.columns([1.5, 1])
with col1_columna:
    with st.container(border=True):
        st.write("")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.write("**Cantidad de Consultas por Mes**")
        cursor = conn.cursor()
        query = """
            SELECT 
                DATE_FORMAT(register_date, '%Y-%m') AS mes,
                COUNT(*) AS conteo_mensajes
            FROM Message
            WHERE active = 1 
                AND role = 'user'
            GROUP BY DATE_FORMAT(register_date, '%Y-%m')
            ORDER BY mes;
        """
        cursor.execute(query)
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=["Mes", "Cantidad de Consultas"])
        if df.empty:
            st.caption("No se han efectuado consultas a lo largo del mes.")
        else:
            st.bar_chart(data = df, x = "Mes", y = "Cantidad de Consultas", height=370)

with col2_columna2:
    with st.container(border=True):
        st.write("")
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            st.write("**Top 5 Temas de Consulta**")
        cursor = conn.cursor()
        query = """
            SELECT 
                classification AS tema,
                COUNT(*) AS cant_class
            FROM Message
            WHERE active = 1 
                AND role = 'assistant'
            GROUP BY classification
            ORDER BY cant_class DESC
            LIMIT 5
        """
        cursor.execute(query)
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=["Tema", "Cantidad de Consultas"])
        if df.empty:
            st.caption("No se han efectuado consultas a lo largo del mes.")
        else:
            fig = px.pie(df, values='Cantidad de Consultas', names='Tema')
            fig.update_traces(textposition='outside', textinfo='percent+label')
            fig.update_layout(showlegend=False)
            fig.update_layout(height=378)
            st.plotly_chart(fig, use_container_width=True)

with st.sidebar:
    # cargar_css("./style.css")
    st.title("Bienvenido, "+ f":blue[{st.session_state["username"]}]!")
    
    if st.button("Gestión de Usuarios", use_container_width=True, type="secondary", icon=":material/group:"):
        st.switch_page("./pages/admin_dashboard_users.py")

    if st.button("Gestión de Conocimiento", use_container_width=True, icon=":material/description:", type="secondary"):
        st.switch_page("./pages/admin_dashboard_knowledge.py")

    if st.button("Banco de Consultas", use_container_width=True, icon=":material/question_answer:", type="secondary"):
        st.switch_page("./pages/admin_dashboard_queries.py")

    st.button("Reporte de Indicadores", use_container_width=True, icon=":material/bar_chart:", disabled=True)

    st.header("Opciones")
    if st.button("Configuración del usuario", use_container_width=True, icon=":material/settings:"):
        config_user()
    if st.button("Cerrar sesión", use_container_width=True, type="primary", icon=":material/logout:"):
        st.session_state["username"] = ""
        st.switch_page('main.py')

st.markdown("""
    <style>
        [data-testid="stMetric"] {
            text-align: center;
        }
            
        [data-testid="stMetricLabel"] {
            display: flex;
        }
    </style>
""", unsafe_allow_html=True)