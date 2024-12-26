import os
import re
import time
from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

#cargar la variable de entorno
load_dotenv()

#inicializar Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

#cargar el modelo de embedding: en este caso usamos all mini lm l12 v2 de HuggingFace
model = SentenceTransformer('sentence-transformers/all-MiniLM-L12-v2')

#crear el index de Pinecone
index_name = "quillagpt-index"

if not pc.has_index(index_name):
    pc.create_index(
        name = index_name,
        dimension = 384,  #dimensiones del modelo a utilizar
        metric = "cosine",
        spec = ServerlessSpec(cloud="aws", region="us-east-1")
    )
    
#preprocesar texto
def preprocesar_texto(texto):
    #reemplazar saltos de linea, tabuladores por espacios
    texto = re.sub(r'\s+', ' ', texto)
    return texto

#procesar archivo pdf
def procesar_arch_pdf(arch):
    #cargar el archivo pdf
    pdf_loader = PyPDFLoader(arch)
    data = pdf_loader.load()

    #efectuar el chunking del texto
    #chunk size es cuanto texto tiene cada fragmento
    #chunk overlap es cuanto texto se comparte entre fragmentos consecutivos
    splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 100)
    documentos = splitter.split_documents(data)

    #preprocesar cada fragmento y agregar la fuente
    texto_con_fuente = [
        {"text": preprocesar_texto(str(documento.page_content)), "source": arch, "page": documento.metadata.get("page", None)}
        for documento in documentos
    ]

    return texto_con_fuente

#buscar el archivo pdf que se encuentra en data
arch = [file for file in os.listdir("data_pdf") if file.endswith('.pdf')]
if not arch:
    raise FileNotFoundError("No se encontró ningún archivo PDF en la carpeta especificada.")

#crear embeddings
def crear_embeddings(texto):
    embeddings = model.encode(texto).tolist()
    return embeddings

#insertar datos en Pinecone
def insertar_datos(data, embeddings):
    index = pc.Index(index_name)
    stats = index.describe_index_stats(namespace = "quillagpt-index")
    total_vectores = stats['total_vector_count']
    records = [
        {
            "id": str(total_vectores + idx),
            "values": embedding,
            "metadata": {"texto": d["text"], "fuente": d["source"], "pagina": d["page"]}
        }
        for idx, (d, embedding) in enumerate(zip(data, embeddings))
    ]
    index.upsert(vectors = records, namespace = "quillagpt-namespace")

#procesar el archivo pdf
texto = procesar_arch_pdf(f"data_pdf/{arch[0]}")
insertar_datos(texto, crear_embeddings(texto))