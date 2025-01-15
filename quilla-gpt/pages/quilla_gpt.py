import streamlit as st
import base64
import os
import json
import pymysql
import hashlib
import time
from datetime import datetime
from sentence_transformers import SentenceTransformer
from streamlit_extras.stylable_container import stylable_container
# from streamlit_feedback import streamlit_feedback
from uuid import uuid4
from pinecone import Pinecone
from dotenv import load_dotenv
from openai import OpenAI
from streamlit_lottie import st_lottie_spinner
from typing import Literal

#inicializar las variables de entorno
load_dotenv()
cliente = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = os.getenv("OPENAI_API_KEY")
)

st.set_page_config(
    layout = "wide",
    page_title = "QuillaGPT"
)

# incicializar pinecone
@st.cache_resource(show_spinner="Inicializando QuillaGPT...")
def inicializar_pinecone():
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = "quillagpt-index"
    index = pc.Index(index_name)
    return index
index = inicializar_pinecone()

#cargar el modelo de embedding
@st.cache_data(show_spinner="Inicializando QuillaGPT...")
def cargar_modelo():
    return SentenceTransformer('sentence-transformers/all-MiniLM-L12-v2')
model = cargar_modelo()

#funcion para eliminar conversaciones
def delete_conversations():
    cursor = conn.cursor()
    query = """
        UPDATE Session
        SET active = 0
        WHERE user_id = (SELECT user_id FROM User WHERE username = %s)
    """
    cursor.execute(query, st.session_state["username"])
    conn.commit()
    st.session_state.messages = []
    st.session_state.current_session_id = None
    st.session_state.sessions_updated = True

if "conversation_delete" not in st.session_state:
    st.session_state.conversation_delete = False

if st.session_state.conversation_delete:
    st.session_state.conversation_delete = False
    st.toast("Todas las conversaciones fueron eliminadas exitosamente.", icon=":material/check:")

#modal para la configuracion del usuario
@st.dialog("Configuración del usuario")
def config_user():
    tab1, tab2 = st.tabs(["Configuración del perfil", "Conversaciones"])
    with tab1:
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
                    
    with tab2:
        if st.button("Eliminar todas mis conversaciones", type="primary", on_click=delete_conversations):
            st.session_state.conversation_delete = True
            st.rerun()

#esto es para el sticky del titulo de la conversacion
MARGINS = {
    "top": "2.875rem",
    "bottom": "0",
}
STICKY_CONTAINER_HTML = """
<style>
div[data-testid="stVerticalBlock"] div:has(div.fixed-header-{i}) {{
    position: sticky;
    {position}: {margin};
    background-color: white;
    z-index: 999;
}}
</style>
<div class='fixed-header-{i}'/>
""".strip()
count = 0
def sticky_container(
    *,
    height: int | None = None,
    border: bool | None = None,
    mode: Literal["top", "bottom"] = "top",
    margin: str | None = None,
):
    if margin is None:
        margin = MARGINS[mode]

    global count
    html_code = STICKY_CONTAINER_HTML.format(position=mode, margin=margin, i=count)
    count += 1

    container = st.container(height=height, border=border)
    container.markdown(html_code, unsafe_allow_html=True)
    return container

#esto es para icono de plus de añadir conversacion
st.markdown(
    '<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons"/>',
    unsafe_allow_html=True,
)

#conexion en mysql
conn = pymysql.connect(
    host=st.secrets["mysql"]["host"],
    user=st.secrets["mysql"]["username"],
    password=st.secrets["mysql"]["password"],
    database=st.secrets["mysql"]["database"]
)

#cargar las instrucciones personalizadas
cursor = conn.cursor()
query = """
    SELECT instruction
    FROM CustomInstruction
    WHERE active = 1
"""
cursor.execute(query)
sistem_message = cursor.fetchone()[0]

sistema = {
    "role": "system",
    "content": (
        sistem_message
    ),
}

#cargar el archivo css y llamarla
# @st.cache_data
def cargar_css(file_path):
    with open(file_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
cargar_css("style.css")

#carga de imagenes
def encode_image(file_path):
    with open(file_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")
plus_icon = encode_image("./static/plus.png")

#carga de spinner lottie
# @st.cache_data
def load_lottie_json(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

#inicializar historial de mensajes
if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None

if "session_new" not in st.session_state:
    st.session_state.session_new = False

if "feedback_response" not in st.session_state:
    st.session_state.feedback_response = False

if "message_response_id" not in st.session_state:
    st.session_state.message_response_id = None

#container de inicio
container_inicio = st.container()
# container_inicio.write("")
with container_inicio:
    # with sticky_container(mode="top", border=False):
        # st.write("")
        st.title("¡Hola, soy QuillaBot! ¿En qué te puedo ayudar?")
        st.write(
            "Recuerda que los datos personales que proporciones en este chatbot serán de uso exclusivo para atender las consultas que formules."
        )
        st.write("")

#barra lateral
with st.sidebar:
    st.title("Bienvenido, "+ f":blue[{st.session_state["username"]}]!")

    col1, col2 = st.columns([5, 1], vertical_alignment="center")
    with col1:
        st.header("Mis conversaciones")
    with col2:
        #cargar el icono de agregar nueva conversacion
        with stylable_container(
            key="container_with_border",
            css_styles=r"""
                .element-container:has(#button-after) + div button {
                    border: none;
                    background: none;
                    padding: 0;
                    cursor: pointer;
                    font-family: 'Material Icons';
                    font-size: 35px;
                }
                .element-container:has(#button-after) + div button::before {
                    content: 'add_circle';
                    display: inline-block;
                    padding-right: 3px;
                }
                """,
        ):
            st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
            if st.button(''):
                st.session_state.messages = []
                st.session_state.feedback_response = False

    cursor = conn.cursor()
    query = """
        SELECT title, session_id
        FROM Session s
        JOIN User u ON s.user_id = u.user_id
        WHERE u.username = %s AND s.active = 1
        ORDER BY start_session DESC
    """
    cursor.execute(query, st.session_state["username"])
    sessions = cursor.fetchall()
    if not sessions:
        st.caption("Por el momento no tienes conversaciones activas. Si deseas iniciar una nueva conversación, haz clic en el botón de + o ingresa directamente tu consulta en la entrada de chat de la pantalla principal.")
    else:
        for session in sessions:
            if st.button(session[0], use_container_width = True, type="secondary", key=session[1]):
                # print("Se dio click en session: " + session[0] + " con ID: " + str(session[1]))
                query = """
                    SELECT role, content
                    FROM Message
                    WHERE session_id = %s AND active = 1
                """
                cursor.execute(query, session[1])
                messages = cursor.fetchall()
                st.session_state.messages = []
                for message in messages:
                    st.session_state.messages.append({"role": message[0], "content": message[1]})
                st.session_state.current_session_id = session[1]
    st.header("Opciones")
    if st.button("Configuración del usuario", use_container_width=True, icon=":material/settings:"):
        config_user()
    if st.button("Cerrar sesión", use_container_width=True, type="primary", icon=":material/logout:"):
        st.session_state["username"] = ""
        st.switch_page('main.py')

#contenedor para los mensajes de chat
for message in st.session_state.messages:
    if message["role"] == "assistant":
        with st.chat_message(message["role"], avatar = "./static/squirrel.png"):
            st.empty()
            st.markdown(message["content"])
    else:
        div = f"""
        <div class = "chat-row row-reverse">
            <img src = "app/static/profile-account.png" width=40 height=40>
            <div class = "user-message">{message["content"]}</div>
        </div>"""
        st.markdown(div, unsafe_allow_html=True)

#entrada de texto del usuario
if prompt := st.chat_input(placeholder = "Ingresa tu consulta sobre algún procedimiento académico-administrativo de la PUCP"):

    st.empty()
    #mostrar la respuesta del usuario
    div = f"""
    <div class = "chat-row row-reverse">
        <img src = "app/static/profile-account.png" width=40 height=40>
        <div class = "user-message">{prompt}</div>
    </div>"""
    st.markdown(div, unsafe_allow_html=True)

    #agregar respuesta del asistente
    with st.chat_message("assistant", avatar = "./static/squirrel.png"):
        
        lottie_spinner = load_lottie_json("./static/loader_thinking_2.json")
        with st_lottie_spinner(lottie_spinner, height=40, width=40, quality='high'):

            if st.session_state.messages == []:
                #generamos el titulo de la session
                response = cliente.chat.completions.create(
                    model="meta/llama-3.3-70b-instruct",
                    messages=[
                        {"role": "system", "content": "Genera un titulo corto y apropiado de hasta máximo 5 palabras para la nueva conversación con el usuario según la consulta que recibes. Responde únicamente con el nombre del título correspondiente, nada más. Recuerda que es hasta máximo 5 palabras el título."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.2,
                    top_p=0.7,
                    max_tokens=8192,
                    stream=False
                )
                titulo = response.choices[0].message.content
                titulo = titulo.replace('"', "")
                cursor = conn.cursor()
                query = """
                    SELECT user_id
                    FROM User
                    WHERE username = %s AND active = 1
                """
                cursor.execute(query, st.session_state["username"])
                user_id = cursor.fetchone()[0]
                #insertar la nueva session en la base de datos
                query = """
                    INSERT INTO Session (start_session, user_id, title, active)
                    VALUES (%s, %s, %s, 1)
                """
                cursor.execute(query, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user_id, titulo))
                conn.commit()
                #obtener el id de la session
                session_id = cursor.lastrowid
                st.session_state.current_session_id = session_id
                #activamos la nueva session
                st.session_state.session_new = True

            #insertar el mensaje del usuario en la base de datos
            cursor = conn.cursor()
            query = """
                INSERT INTO Message (session_id, timestamp, register_date, role, content, active)
                VALUES (%s, %s, %s, 'user', %s, 1)
            """
            cursor.execute(query, (st.session_state.current_session_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.now().strftime('%y-%m-%d'), prompt))
            conn.commit()

            #preparar el historial de conversacion
            conversacion = []
            for message in st.session_state.messages:
                conversacion.append({"role": message["role"], "content": message["content"]})

            #buscar en pinecone los resultados del prompt
            query_embedding = model.encode([prompt])[0].tolist()
            results = index.query(
                namespace = "quillagpt-namespace",
                vector = query_embedding,
                top_k = 3,
                include_values = False,
                include_metadata = True
            )
            retrieved_documents = [f"Metadata: {result['metadata']}" for result in results['matches']]
            contexto = "\n".join(retrieved_documents)

            #generamos la respuesta natural
            stream =  cliente.chat.completions.create(
                model = "meta/llama-3.3-70b-instruct",
                messages=[
                    sistema,
                    *conversacion,
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": contexto}
                ],
                temperature = 0.2,
                top_p = 0.7,
                max_tokens = 8192,
                stream = True
            )

            #generamos respuesta como string
            respuesta =  cliente.chat.completions.create(
                model = "meta/llama-3.3-70b-instruct",
                messages=[
                    sistema,
                    *conversacion,
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": contexto}
                ],
                temperature = 0.2,
                top_p = 0.7,
                max_tokens = 8192,
                stream = False
            )

        response = st.write_stream(stream)
        st.session_state.feedback_response = True
        
    #identificamos el tema del mensaje
    tema_response = cliente.chat.completions.create(
        model="meta/llama-3.3-70b-instruct",
        messages=[
            {"role": "system", "content": """
            Cual es el titulo que mejor describe la consulta? Obligatoriamente debe ser uno de los siguientes:
1. Cambio de especialidad
2. Certificado de notas
3. Convalidación de cursos
4. Duplicado de carné universitario
5. Matrícula
6. Obtención del título profesional
7. Pago para trámites académicos no presenciales
8. Reconocimiento de cursos
9. Registro histórico de notas
10. Reincorporación
11. Retiro de cursos
12. Solicitud de constancias a la OCR
13. Transferencia interna
14. Verificación de grados y/o títulos
15. Otros
            Solo responde con el titulo correspondiente sin la numeración, nada más.
            """},
            {"role": "user", "content": "La consulta es" + prompt},
        ],
        temperature=0.2,
        top_p=0.7,
        max_tokens=8192,
        stream=False
    )
    tema = tema_response.choices[0].message.content
    tema = tema.replace('"', "")

    cursor = conn.cursor()
    query = """
        INSERT INTO Message (session_id, timestamp, register_date, role, content, classification, active)
        VALUES (%s, %s, %s, 'assistant', %s, %s, 1)
    """
    print("Este es el tema:")
    print(tema)
    cursor.execute(query, (st.session_state.current_session_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.now().strftime('%y-%m-%d'), response, tema))
    conn.commit()
    added_message_id = cursor.lastrowid
    st.session_state.message_response_id = added_message_id

    #insertar el tema en la base de datos o actualizar el timestamp si es que ya existe
    cursor = conn.cursor()
    query_upsert = """
        INSERT INTO SessionClassification (timestamp, session_id, classification, active)
        VALUES (%s, %s, %s, 1)
        ON DUPLICATE KEY UPDATE timestamp = %s
    """
    cursor.execute(
        query_upsert,
        (
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            st.session_state.current_session_id,
            tema,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
    )
    conn.commit()

    #actualizar el historial de mensajes
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": response})

    #reiniciamos el sidebar para actualizar con la nueva conversacion
    if st.session_state.session_new:
        st.session_state.session_new = False
        st.rerun()

def send_feedback(derivar, message_id):
  cursor = conn.cursor()
  query = """
    INSERT INTO RequestQuery (query, register_date, classification, resolved, active)
    VALUES (%s, %s, (SELECT classification FROM Message WHERE message_id = %s AND active = 1), 0, 1)
  """
  cursor.execute(query, (derivar, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message_id))
  conn.commit()
  query = """
    UPDATE Message
    SET derived = 1
    WHERE message_id = %s
    AND active = 1
  """
  cursor.execute(query, (message_id))
  conn.commit()
  
if "feedback_sent" not in st.session_state:
    st.session_state.feedback_sent = False

if st.session_state.feedback_sent:
    st.session_state.feedback_sent = False
    st.toast("Consulta derivada al administrador. Muchas gracias por ayudar a QuillaGPT!", icon=":material/check:")

@st.dialog("¿La respuesta brindada no fue de tu satisfacción?")
def config_feedback(message_id):
  st.write("Si QuillaGPT no ha podido responder a tu consulta y deseas que fuera respondida, favor de indicarlo en el recuadro de abajo para derivar la consulta al administrador. A fin de que el administrador pueda asistirte mejor, especifique el procedimiento de interés y consecuentemente añada la consulta correspondiente. De esta manera, el administrador podrá brindarte una respuesta más precisa según el contexto especificado.")
  derivar = st.text_area("**Consulta a derivar al administrador**", height=250, max_chars=500, placeholder="Escribe aquí tu consulta...")
  col1, col2, col3 = st.columns([5, 2, 2])
  with col2:
    if st.button("Cancelar", type="secondary", use_container_width=True):
        st.rerun()
  with col3:
    if st.button("Enviar", type="primary", use_container_width=True, args=(derivar, message_id), on_click=send_feedback):
        st.session_state.feedback_sent = True
        st.rerun()

if 'fbk' not in st.session_state:
    st.session_state.fbk = str(uuid4())
def save_feedback(respuesta):
    # print(respuesta)
    cursor = conn.cursor()
    query = """
        UPDATE Message
        SET positive = %s
        WHERE message_id = %s
    """
    cursor.execute(query, (respuesta, st.session_state.message_response_id))
    conn.commit()

    if respuesta == 1:
        query = """
            UPDATE Message
            SET derived = 0
            WHERE message_id = %s
        """
        cursor.execute(query, st.session_state.message_response_id)
        conn.commit()
        bandera = st.success("Hemos registrado tu feedback. Nos alegra que la respuesta brindada sea de tu satisfacción.")
        time.sleep(3)
        bandera.empty()
    else:
        config_feedback(st.session_state.message_response_id)

    #crear un nuevo feedback id (si le quitamos se mantendra el feedback anterior)
    st.session_state.fbk = str(uuid4())
    st.session_state.feedback_response = False
    st.session_state.message_response_id = None

if st.session_state.feedback_response:
    # streamlit_feedback(
    #     feedback_type="thumbs",
    #     # optional_text_label="[Optional]",
    #     align="flex-end",
    #     key=st.session_state.fbk,
    #     on_submit=save_feedback
    # )
    feedback = st.feedback("thumbs", key=st.session_state.fbk)
    if feedback is not None:
        save_feedback(feedback)