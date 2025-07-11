import streamlit as st
from streamlit_navigation_bar import st_navbar
import requests as req
import json
from utils.query_to_vectorDB_uploader import create_query_embedding
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from datetime import datetime
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
    # st.session_state["user"] = None
    # st.session_state["credentials"] = None
    st.session_state.feedback_response = False
    # st.switch_page('main.py')
    st.logout()
elif page == "Panel de Estudiante":
    st.session_state.page_session = " "
    st.switch_page('./pages/quillagpt.py')

#cargar el archivo css y llamarla
def cargar_css(file_path):
    with open(file_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
cargar_css("style.css")

#crear la variable de ID tabla para poder reiniciar la seleccion
if "tabla_id" not in st.session_state:
    st.session_state.tabla_id = 0

if "bandera" not in st.session_state:
    st.session_state.bandera = False

#modal para revisar la consulta del estudiante
@st.dialog("Detalle de la consulta", width='large')
def verDetalle(selected_index):

    st.text_input("**Fecha de la consulta**", value=data_consulta[selected_index][1], disabled=True)

    st.text_input("**Nombre del usuario**", value=data_consulta[selected_index][3], disabled=True)

    st.text_input("**Correo del usuario**", value=data_consulta[selected_index][2], disabled=True)

    st.text_area("**Consulta**", value=data_consulta[selected_index][5], disabled=True)

    with st.expander("Contexto", expanded=False):
        input = {"indice" : int(data_consulta[selected_index][0])}
        result = req.get(url="http://127.0.0.1:8000/ObtenerContextoSolicitud", data=json.dumps(input))
        data = result.json()
        cleaned_data = data[0][0].replace("\\n", "\n").strip()

        st.text_area("**Context**", value=cleaned_data, disabled=True, label_visibility="collapsed", height=150)
        # st.write(cleaned_data)

    if data_consulta[selected_index][7] == "Resuelta":
        respuesta = st.text_area("**Respuesta**", value=data_consulta[selected_index][6], disabled = True)
    else:
        respuesta = st.text_area("**Respuesta**", placeholder="Ingrese la respuesta a la consulta...")
        col1, col2 = st.columns([3, 0.85])
        with col2:
            if 'query_resolved_button' in st.session_state and st.session_state.query_resolved_button == True:
                st.session_state.query_running = True
            else:
                st.session_state.query_running = False

            if st.button("Guardar cambios", type="primary", key="query_resolved_button", disabled=st.session_state.query_running):
                
                input = { "id" : int(data_consulta[selected_index][0]), "respuesta" : respuesta }
                req.put(url="http://127.0.0.1:8000/SolicitudResolucion", data = json.dumps(input))

                #subir la respuesta a la base de datos de Pinecone
                data = {}
                data['consulta'] = data_consulta[selected_index][4]
                data['respuesta'] = respuesta
                data['id'] = int(data_consulta[selected_index][0])
                data['fuente'] = "Consulta derivada al administrador del banco de consultas de PandaGPT"
                data['fecha de extracción'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                json_data = json.dumps(data)
                data_dict = json.loads(json_data)
                create_query_embedding(data_dict)

                gmail_user = os.getenv("GMAIL_USER")
                gmail_password = os.getenv("GMAIL_PASSWORD")
                sent_from = gmail_user
                sent_to = [data_consulta[selected_index][2]]
                subject = f"{str(int(data_consulta[selected_index][0])).zfill(5)} - Su consulta en PandaGPT ha sido resuelta"
                message = f"""
<!DOCTYPE html>
<html>
<body>
    <p>¡Hola!</p>

    <p>Te informamos que tu consulta ha sido resuelta por el administrador <b>{st.session_state.user["name"]}</b>.</p>

    <p><b>ID de la consulta:</b> {str(int(data_consulta[selected_index][0])).zfill(5)}<br>
    <b>Fecha de registro:</b> {data_consulta[selected_index][1]}<br>
    <b>Tema:</b> {data_consulta[selected_index][4]}<br>
    <b>Consulta:</b> {data_consulta[selected_index][5]}<br>
    <b>Respuesta:</b> {respuesta}</p>

    <p>Agradecemos tu paciencia y confianza en PandaGPT. Esperamos que la solución brindada haya sido de tu satisfacción.</p>

    <p>Si tienes alguna otra pregunta o necesitas más ayuda, no dudes en contactarnos.</p>

    <h3>Información de contacto:</h3>
    <p><b>Ubicación:</b><br>
    Av. Universitaria 1801, San Miguel 15088, Lima - Perú</p>

    <p><b>Horario de atención:</b><br>
    L-V de 9 a.m. a 5 p.m.<br>
    Refrigerio: 1 p.m. a 2 p.m.</p>

    <p><b>Correo electrónico:</b><br>
    informes-fci@pucp.edu.pe</p>

    <p>¡Gracias por usar a PandaGPT!</p>

    <p><b>Atentamente,</b><br>
    <b>El equipo de PandaGPT</b></p>
</body>
</html>
"""
                msg = MIMEMultipart()
                msg['From'] = sent_from
                msg['To'] = ', '.join(sent_to)
                msg['Subject'] = subject
                msg.attach(MIMEText(message, 'html'))
                try:
                    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                    server.ehlo()
                    server.login(gmail_user, gmail_password)
                    server.sendmail(sent_from, sent_to, msg.as_string())
                except Exception as e:
                    print(f"Error al enviar el correo: {e}")
                finally:
                    server.close()

                st.session_state.tabla_id += 1
                st.session_state.bandera = True
                st.rerun()

if st.session_state.bandera:
    st.toast("Se envió la respuesta al correo electrónico del usuario solicitante", icon=":material/check:")
    st.session_state.bandera = False

#titulo
container_inicio = st.container()
container_inicio.write("")
container_inicio.write("")
container_inicio.write("")
container_inicio.write("")
container_inicio.write("")
container_inicio.write("")
container_inicio.title("Solicitudes de Soporte", anchor=False)

result = req.get(url="http://127.0.0.1:8000/ObtenerClasificaciones")
temas = result.json()
opciones_temas = ["Todos"] + [tema[0] for tema in temas]

col1, col2, col3 = st.columns([3, 2, 6], vertical_alignment="bottom")
with col1:
    tema = st.selectbox("**Tema de consulta**", opciones_temas)
with col2:
    estado = st.selectbox("**Estado**", ["Pendiente", "Resuelta", "Todos"])

#tabla de consultas
input = {"tema" : tema, "estado" : estado}
result = req.get(url="http://127.0.0.1:8000/ObtenerSolicitudesSoporte", data=json.dumps(input))
data_consulta = result.json()

for i in range(len(data_consulta)):
    with st.container(border=True, key="container"+str(i)):
        col_cont1, col_cont2 = st.columns([3, 1], vertical_alignment
        ="center")
        with col_cont1:
            st.subheader(data_consulta[i][5], anchor=False)
            st.write(f"**Realizado por el usuario:** {data_consulta[i][3]}")
            st.write(f"**Fecha de consulta:** {data_consulta[i][1]}")
            st.write(f"**Estado:** {data_consulta[i][7]}")
            st.write("")
        with col_cont2:
            if data_consulta[i][7] == 'Pendiente':
                if st.button("Responder", key="editar"+str(i), type="secondary", icon=":material/reply:"):
                    verDetalle(i)
            else:
                if st.button("Ver detalle", key="editar"+str(i), type="secondary", icon=":material/visibility:"):
                    verDetalle(i)

if any(consulta[7] == 'Pendiente' for consulta in data_consulta) == False and estado == 'Pendiente':
    st.caption("No hay solicitudes de soporte pendientes registradas en la base de datos.")

# df = pd.DataFrame(data, columns=["ID", "Fecha de registro", "Correo del usuario", "Tema", "Consulta", "Respuesta", "Estado"])
# df['Fecha de registro'] = pd.to_datetime(df['Fecha de registro'], format="%Y-%m-%d")
# df['Fecha de registro'] = df['Fecha de registro'].dt.strftime("%d/%m/%Y")

# event = st.dataframe(
#     df,
#     on_select="rerun",
#     selection_mode=["single-row"],
#     hide_index=True,
#     key = str(st.session_state.tabla_id),
#     use_container_width=True
# )

# if event.selection is not None:
#     if event.selection['rows']:
#         selected_index = event.selection['rows'][0]
#         # value_a = df.loc[selected_index, 'a']
#         verDetalle(selected_index)

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

    if st.button("Gestión del Conocimiento", use_container_width=True, icon=":material/description:", type="secondary"):
        st.switch_page("./pages/dashboard_knowledge.py")

    st.button(button_text, use_container_width=True, icon=":material/question_answer:", type="primary")

    if st.button("Reporte de Indicadores", use_container_width=True, icon=":material/bar_chart:", type="secondary"):
        st.switch_page("./pages/dashboard_report.py")