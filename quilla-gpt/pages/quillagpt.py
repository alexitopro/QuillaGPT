import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import openai
import os
from pinecone import Pinecone, ServerlessSpec
from streamlit_navigation_bar import st_navbar
from streamlit_extras.stylable_container import stylable_container
import requests as req
import json
from streamlit_lottie import st_lottie_spinner
from uuid import uuid4
import time
from PIL import Image
from io import BytesIO

#inicializar las variables de entorno
load_dotenv()
cliente = OpenAI(
#   base_url = "https://integrate.api.nvidia.com/v1",
  api_key = os.getenv("OPENAI_API_KEY")
)

# openai.api_key = os.getenv("OPENAI_API_KEY")

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
    "Configuración": ":material/settings:",
    "Cerrar sesión": ":material/logout:",
    "Panel de Administrador": ":material/switch_account:",
}

if "messages" not in st.session_state:
    st.session_state.messages = []

if "prompt_ingresado" not in st.session_state:
    st.session_state.prompt_ingresado = None

if st.session_state.messages == [] and st.session_state.prompt_ingresado == None:
    st.set_page_config(
        layout = "centered",
        page_title = "PandaGPT",
    )
else:
    st.set_page_config(
        layout = "wide",
        page_title = "PandaGPT",
    )

if "page_session" not in st.session_state:
    st.session_state.page_session = " "

# CONTENIDO DEL NAV BAR
if st.session_state.role_id == 1:
    page = st_navbar(
        [],
        right=[" ", "Panel de Administrador", "Configuración", "Cerrar sesión"],
        styles=styles,
        icons=icons,
        options={"fix_shadow": False},
        selected= st.session_state.page_session
    )
else:
    page = st_navbar(
        [],
        right=[" ", "Configuración", "Cerrar sesión"],
        styles=styles,
        icons=icons,
        options={"fix_shadow": False},
        selected= st.session_state.page_session
    )

# incicializar pinecone
@st.cache_resource(show_spinner="Inicializando PandaGPT...")
def inicializar_pinecone():
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = "quillagpt-index"
    if not pc.has_index(index_name):
        pc.create_index(
            name = index_name,
            dimension = 1536,  #dimensiones del modelo a utilizar
            metric = "cosine",
            spec = ServerlessSpec(cloud="aws", region="us-east-1")
        )
    index = pc.Index(index_name)
    return index
index = inicializar_pinecone()

#cargar el modelo de embedding
# @st.cache_data(show_spinner="Inicializando PandaGPT...")
# def cargar_modelo():
#     return SentenceTransformer('sentence-transformers/all-MiniLM-L12-v2')
# model = cargar_modelo()

#cargar el archivo css
def cargar_css(file_path):
    with open(file_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
cargar_css("style.css")

#cargar las instrucciones personalizadas
system_message = req.get(f"http://127.0.0.1:8000/CustomInstruction/")
sistema = {
    "role": "system",
    "content": (
        system_message.json()
    ),
}

#esto es para icono de plus de añadir conversacion
st.markdown(
    '<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons"/>',
    unsafe_allow_html=True,
)

#carga de spinner lottie
def load_lottie_json(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

#FUNCIONES
#funcion para eliminar conversaciones
def delete_conversations(email):
    result = req.delete(f"http://127.0.0.1:8000/Session/{email}")
    if result.status_code == 200:
        st.session_state.messages = []
        st.session_state.current_session_id = None
        st.session_state.sessions_updated = True

if "conversation_delete" not in st.session_state:
    st.session_state.conversation_delete = False
if st.session_state.conversation_delete:
    st.session_state.conversation_delete = False
    st.toast("Todas las conversaciones fueron eliminadas exitosamente.", icon=":material/check:")

#modal de configuracion del usuario
@st.dialog("Configuración")
def config_user():
    tab1, tab2 = st.tabs(["Mi cuenta", "Conversaciones"])
    st.session_state.page_session = " "
    with tab1:
        col1, col2, col3 = st.columns([1, 0.75, 1])
        with col2:
            image_url = st.session_state.user["picture"]
            response = req.get(image_url)
            image = Image.open(BytesIO(response.content))
            st.image(image, width=100)
        st.text_input("**Nombre de usuario**", value=st.session_state["username"], disabled=True)
        st.text_input("**Correo electrónico**", value=st.session_state.user["email"], disabled=True)
        st.text_input("**Rol**", value="Administrador" if st.session_state.role_id == 1 else "Estudiante", disabled=True)
    with tab2:
        if st.button("Eliminar todas las conversaciones"):
            delete_conversations(st.session_state.user["email"])
            st.session_state.conversation_delete = True
            st.session_state.feedback_response = False
            st.rerun()

if page == "Configuración":
    config_user()
    # st.session_state.page_session = "Configuración"
elif page == "Cerrar sesión":
    st.session_state["username"] = ""
    st.session_state.messages = []
    st.session_state["user"] = None
    st.session_state["credentials"] = None
    st.session_state.feedback_response = False
    st.session_state.page_session = " "
    st.switch_page('main.py')
elif page == "Panel de Administrador":
    st.session_state.messages = []
    st.session_state.feedback_response = False
    st.session_state.page_session = " "
    st.switch_page('./pages/dashboard_users.py')

#inicializar historial de mensajes

if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None

if "session_new" not in st.session_state:
    st.session_state.session_new = False

if "feedback_response" not in st.session_state:
    st.session_state.feedback_response = False

if "message_response_id" not in st.session_state:
    st.session_state.message_response_id = None

if st.session_state.messages == [] and st.session_state.prompt_ingresado == None:
    col1, col2, col3 = st.columns([1, 5, 1])
    with col2:
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.markdown("<img src='app/static/panda.png' width='150' style='display: block; margin: 0 auto;'>" , unsafe_allow_html=True)
        st.write("")
        st.write("")
        st.header("¿En qué te puedo ayudar?", anchor = False)
        st.write("")
        st.write("")
else:
    #container de inicio
    container_inicio = st.container()
    with container_inicio:
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.title("¡Hola, soy PandaGPT! ¿En qué te puedo ayudar?", anchor = False)
        st.write(
            "Recuerda que los datos personales que proporciones en este chatbot serán de uso exclusivo para atender las consultas que formules."
        )

        st.write("")

#sidebar
if "username" not in st.session_state:
    st.session_state.username = False
with st.sidebar:
    # st.title("Bienvenido, "+ f":blue[{st.session_state["username"]}]!")
    st.markdown(
        f"""
        <h1 style="color:#00205B;">Bienvenido, {st.session_state["username"]}!</h1>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([5, 1], vertical_alignment="center")
    with col1:
        st.markdown(
            """
            <h2 style="color:#00205B;">Mis conversaciones</h2>
            """,
            unsafe_allow_html=True
        )
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
                    color: #00CFB4;
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
        
    result = req.get(f"http://127.0.0.1:8000/Session/ObtenerSesionesUsuario/{st.session_state.user["email"]}")
    sessions = result.json()
    if not sessions:
        st.caption("Por el momento no tienes conversaciones activas. Si deseas iniciar una nueva conversación, haz clic en el botón de + o ingresa directamente tu consulta en la entrada de chat de la pantalla principal.")
    else:
        for session in sessions:
            if st.button(session[0], use_container_width = True, type="secondary", key=session[1]):
                st.session_state.feedback_response = False
                result = req.get(f"http://127.0.0.1:8000/Message/ObtenerMensajesSesion/{session[1]}")
                st.session_state.page_session = " "
                messages = result.json()
                st.session_state.messages = []
                for message in messages:
                    st.session_state.messages.append({"role": message[0], "content": message[1]})
                st.session_state.current_session_id = session[1]

#contenedor para los mensajes de chat
for message in st.session_state.messages:
    if message["role"] == "assistant":
        with st.chat_message(message["role"], avatar = "./static/panda_green.png"):
            st.empty()
            st.markdown(message["content"])
    else:
        div = f"""
        <div class = "chat-row row-reverse">
            <img src = "app/static/profile-account.png" width=40 height=40>
            <div class = "user-message">{message["content"]}</div>
        </div>"""
        st.markdown(div, unsafe_allow_html=True)

if st.session_state.messages == [] and st.session_state.prompt_ingresado == None:
    with st.container():
        if prompt := st.chat_input(placeholder = "Ingresa tu consulta a PandaGPT"):
            st.session_state.prompt_ingresado = prompt
            st.rerun()
        col1, col2, col3 = st.columns([1, 5, 1])
        with col2:
            st.caption("Puedes consultar sobre cómo realizar tu trámite de reincorporación, cómo retirarte de un curso, cómo acreditar un curso, cómo realizar el reclamo de notas y entre otras cosas más. ¡Pregunta lo que necesites; estaré aquí para apoyarte!")
else:
    if prompt := st.chat_input(placeholder = "Ingresa tu consulta sobre algún procedimiento académico-administrativo de la PUCP") or st.session_state.prompt_ingresado:
        if st.session_state.prompt_ingresado is not None:
            prompt = st.session_state.prompt_ingresado
        st.empty()
        #mostrar la respuesta del usuario
        div = f"""
        <div class = "chat-row row-reverse">
            <img src = "app/static/profile-account.png" width=40 height=40>
            <div class = "user-message">{prompt}</div>
        </div>"""
        st.markdown(div, unsafe_allow_html=True)
        #agregar respuesta del asistente
        with st.chat_message("assistant", avatar = "./static/panda_green.png"):
            lottie_spinner = load_lottie_json("./static/loader_thinking_2.json")
            with st_lottie_spinner(lottie_spinner, height=40, width=40, quality='high'):
                if st.session_state.messages == []:
                    #generamos el titulo de la session
                    response = cliente.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Genera un titulo corto y apropiado de hasta máximo 5 palabras para la nueva conversación con el usuario según la consulta que recibes. Responde únicamente con el nombre del título correspondiente, nada más. Recuerda que es hasta máximo 5 palabras el título."},
                            {"role": "user", "content": prompt},
                        ],
                        temperature=0.2,
                        max_tokens=20,
                        stream=False
                    )
                    titulo = response.choices[0].message.content
                    titulo = titulo.replace('"', "")
                    result = req.get(f"http://127.0.0.1:8000/User/{st.session_state.user["email"]}")
                    user_id = result.json()[0]
                    #insertar la nueva session en la base de datos
                    input = {"user_id" : user_id, "titulo" : titulo}
                    result = req.post(url="http://127.0.0.1:8000/Session", data = json.dumps(input))
                    #obtener el id de la session
                    session_id = result.json()
                    st.session_state.current_session_id = session_id
                    #activamos la nueva session
                    st.session_state.session_new = True
                
                #insertar el mensaje del usuario en la base de datos
                input = {"session_id" : st.session_state.current_session_id, "role" : "user", "content" : prompt, "classification" : "-1"}
                result = req.post(url="http://127.0.0.1:8000/Message", data = json.dumps(input))

                #preparar el historial de conversacion
                conversacion = []
                historial_conversacion = ""
                for message in st.session_state.messages:
                    conversacion.append({"role": message["role"], "content": message["content"]})
                    historial_conversacion += f"{message['role']}: {message['content']}\n"

                #buscar en pinecone los resultados del prompt
                # query_embedding = model.encode([prompt])[0].tolist()

                historial_conversacion += f"user: {prompt}\n"
                response = openai.embeddings.create(
                    model="text-embedding-3-small",
                    input=historial_conversacion
                )

                query_embedding = response.data[0].embedding

                results = index.query(
                    namespace = "quillagpt-namespace",
                    vector = query_embedding,
                    top_k = 3,
                    include_values = False,
                    include_metadata = True
                )
                retrieved_documents = [f"Metadata: {result['metadata']}" for result in results['matches']]
                contexto = "\n".join(retrieved_documents)

                print(results)

                #generamos la respuesta natural
                stream =  cliente.chat.completions.create(
                    model = "gpt-4o-mini",
                    messages=[
                        sistema,
                        *conversacion,
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": contexto}
                    ],
                    temperature = 0.5,
                    max_tokens = 1000,
                    stream = True
                )

                # #generamos respuesta como string
                # respuesta =  cliente.chat.completions.create(
                #     model = "meta/llama-3.3-70b-instruct",
                #     messages=[
                #         sistema,
                #         *conversacion,
                #         {"role": "user", "content": prompt},
                #         {"role": "assistant", "content": contexto}
                #     ],
                #     temperature = 0.2,
                #     top_p = 0.7,
                #     max_tokens = 1000,
                #     stream = False
                # )

            response = st.write_stream(stream)
            st.session_state.feedback_response = True

        #identificamos el tema del mensaje
        tema_response = cliente.chat.completions.create(
            model="gpt-4o-mini",
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
            max_tokens=50,
            stream=False
        )
        tema = tema_response.choices[0].message.content
        tema = tema.replace('"', "")

        #insertar el mensaje del usuario en la base de datos
        input = {"session_id" : st.session_state.current_session_id, "role" : "assistant", "content" : response, "classification" : tema}
        result = req.post(url="http://127.0.0.1:8000/Message", data = json.dumps(input))
        added_message_id = result.json()
        st.session_state.message_response_id = added_message_id

        #insertar el tema en la base de datos o actualizar el timestamp si es que ya existe
        input = {"session_id" : st.session_state.current_session_id, "tema" : tema}
        result = req.post(url="http://127.0.0.1:8000/SessionClassification", data = json.dumps(input))

        #actualizar el historial de mensajes
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": response})

        st.session_state.prompt_ingresado = None

        #reiniciamos el sidebar para actualizar con la nueva conversacion
        if st.session_state.session_new:
            st.session_state.session_new = False
            st.rerun()

def send_feedback(derivar, message_id):
    input = {"derivar" : derivar, "message_id" : message_id, "email" : st.session_state.user["email"]}
    req.post(url="http://127.0.0.1:8000/RequestQuery", data = json.dumps(input))
    input = {"message_id" : message_id, "derivado" : 1}
    req.put(url="http://127.0.0.1:8000/ActualizarDerivado", data = json.dumps(input))
  
if "feedback_sent" not in st.session_state:
    st.session_state.feedback_sent = False

if st.session_state.feedback_sent:
    st.session_state.feedback_sent = False
    st.toast("Consulta derivada. Se te enviará un correo con los detalles una vez el administrador la resuelva.", icon=":material/check:")

@st.dialog("¿La respuesta brindada no fue de tu satisfacción?")
def config_feedback(message_id):
#   st.write("Si PandaGPT no pudo responder tu consulta, indícalo en el recuadro de abajo para derivarla al administrador. Para una mejor asistencia, especifica el procedimiento de interés y detalla tu consulta. Esto permitirá al administrador ofrecerte una respuesta más precisa según el contexto.")
  derivar = st.text_area("**Consulta a derivar al administrador**", placeholder = "Si PandaGPT no pudo responder tu consulta, indícalo en el recuadro de abajo para derivarla al administrador. Para una mejor asistencia, especifica el procedimiento de interés y detalla tu consulta. Esto permitirá al administrador ofrecerte una respuesta más precisa según el contexto.", height=250, max_chars=500)
  col1, col2, col3 = st.columns([5, 2, 2])
  with col2:
    if st.button("Cancelar", type="secondary", use_container_width=True):
        st.rerun()
  with col3:
    if st.button("Enviar", type="primary", use_container_width=True):
        send_feedback(derivar, message_id)
        st.session_state.feedback_sent = True
        st.rerun()

if 'fbk' not in st.session_state:
    st.session_state.fbk = str(uuid4())
def save_feedback(respuesta):
    input = {"positivo" : respuesta, "message_id" : st.session_state.message_response_id}
    req.put(url="http://127.0.0.1:8000/ActualizarFeedback", data = json.dumps(input))

    if respuesta == 1:
        input = {"message_id" : st.session_state.message_response_id, "derivado" : 0}
        req.put(url="http://127.0.0.1:8000/ActualizarDerivado", data = json.dumps(input))
        st.toast("Hemos registrado tu feedback. Nos alegra que la respuesta brindada sea de tu satisfacción.")
    else:
        config_feedback(st.session_state.message_response_id)

    #crear un nuevo feedback id (si le quitamos se mantendra el feedback anterior)
    st.session_state.fbk = str(uuid4())
    st.session_state.feedback_response = False
    st.session_state.message_response_id = None

if st.session_state.feedback_response:
    cols= st.columns([0.45, 0.6, 10], vertical_alignment="center", gap='small')
    with cols[1]:
        feedback = st.feedback("thumbs", key=st.session_state.fbk)
        if feedback is not None:
            save_feedback(feedback)
    with cols[2]:
        if st.button("Derivar consulta", type="tertiary"):
            st.session_state.feedback_response = False
            config_feedback(st.session_state.message_response_id)

st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.markdown(
    """
    <style>
    [data-testid="stAppScrollToBottomContainer"] {
        margin-bottom: -50px;
    }
    </style>
    """,
    unsafe_allow_html=True
)