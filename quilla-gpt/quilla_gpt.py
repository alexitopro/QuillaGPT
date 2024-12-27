import streamlit as st
import base64
import os
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from dotenv import load_dotenv
from openai import OpenAI

#inicializar las variables de entorno
load_dotenv()
cliente = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = os.getenv("OPENAI_API_KEY")
)
#incicializar pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = "quillagpt-index"
index = pc.Index(index_name)
#cargar el modelo de embedding
model = SentenceTransformer('sentence-transformers/all-MiniLM-L12-v2')

st.set_page_config(
    layout = "wide",
    page_title = "QuillaGPT"
)

#cargar el archivo css y llamarla
def cargar_css(file_path):
    with open(file_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
cargar_css("./style.css")

#carga de imagenes
def encode_image(file_path):
    with open(file_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")
plus_icon = encode_image("./static/plus.png")

#barra lateral
with st.sidebar:
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <h1 style="margin: 0;">Mis conversaciones</h1>
            <a href="#" style="text-decoration: none;"">
                <img src="data:image/png;base64,{plus_icon}" width="30" style="cursor: pointer;" />
            </a>
        </div>
        """,
        unsafe_allow_html = True
    )

#container de inicio
container_inicio = st.container()
container_inicio.title("¡Hola, soy QuillaBot! ¿En qué te puedo ayudar?")
container_inicio.write(
    "Recuerda que los datos personales que proporciones en este chatbot serán de uso exclusivo para atender las consultas que formules."
)

#inicializar historial de mensajes
if "messages" not in st.session_state:
    st.session_state.messages = []

#mostrar los mensajes del historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

#entrada de texto del usuario
if prompt := st.chat_input(placeholder = "Ingresa tu consulta sobre algún procedimiento académico-administrativo de la PUCP"):

    #preparar el historial de conversacion
    conversacion = []
    for message in st.session_state.messages:
        conversacion.append({"role": message["role"], "content": message["content"]})

    #anexar mensaje de usuario al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    #mostrar la respuesta del usuario
    with st.chat_message("user"):
        st.markdown(prompt)
    #agregar respuesta del asistente
    with st.chat_message("assistant"):
        #instruccion personalizada
        sistema = {
            "role": "system",
            "content": (
                "Te llamas QuillaGPT y ayudas sobre procesos académico-administrativos de la PUCP. "
                "Menciona sobre qué fuente has sacado información y, si es de la guía del panda, menciona en qué página el usuario "
                "puede encontrar más información. Asimismo, si hay algún link de interés, compártelo. "
                "Si no encuentras información relacionada, puedes decir 'No tengo información sobre eso'."
            ),
        }

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
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})