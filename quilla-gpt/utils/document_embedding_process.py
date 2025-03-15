import os
import re
import streamlit as st
import openai
from datetime import datetime

#conectarse a pinecone y crear un index si tdv no se ha hecho
def pinecone_init(index_name):
    from pinecone import Pinecone, ServerlessSpec

    #inicializar Pinecone
    pc = Pinecone(api_key=st.secrets["pinecone"]["PINECONE_API_KEY"])

    if not pc.has_index(index_name):
        pc.create_index(
            name = index_name,
            dimension = 3072,  #dimensiones del modelo a utilizar
            metric = "cosine",
            spec = ServerlessSpec(cloud="aws", region="us-east-1")
        )
    
    return pc
    
#preprocesar texto
def preprocesar_texto(texto):
    #reemplazar saltos de linea, tabuladores por espacios
    texto = re.sub(r'\s+', ' ', texto)
    return texto

#procesar archivo pdf
def procesar_arch_pdf(arch):
    from langchain_community.document_loaders import PyPDFLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    #cargar el archivo pdf
    pdf_loader = PyPDFLoader(arch)
    data = pdf_loader.load()

    #efectuar el chunking del texto
    #chunk size es cuanto texto tiene cada fragmento
    #chunk overlap es cuanto texto se comparte entre fragmentos consecutivos
    splitter = RecursiveCharacterTextSplitter(chunk_size = 1050, chunk_overlap = 160)
    documentos = splitter.split_documents(data)

    #preprocesar cada fragmento y agregar la fuente
    texto_con_fuente = [
        {"text": preprocesar_texto(str(documento.page_content)), "source": arch, "page": documento.metadata.get("page", None) + 1}
        for documento in documentos
    ]

    return texto_con_fuente

#crear embeddings
def crear_embeddings(textos):
    text_list = [item['text'] for item in textos]
    #generar embeddings con open ai
    response = openai.embeddings.create(
        model="text-embedding-3-large",
        input=text_list
    )
    return [embedding.embedding for embedding in response.data]

#insertar datos en Pinecone
def insertar_datos(data, embeddings, pc, tipo, index_name):
    index = pc.Index(index_name)
    stats = index.describe_index_stats(namespace = "quillagpt-index")
    total_vectores = stats['total_vector_count']
    records = [
        {
            "id": f"{tipo}{total_vectores + idx}",
            "values": embedding,
            "metadata": {"texto": d["text"], "fuente": d["source"], "pagina": d["page"], "fecha de extracción": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        }
        for idx, (d, embedding) in enumerate(zip(data, embeddings))
    ]
    index.upsert(vectors = records, namespace = "quillagpt-namespace")

#procesar el archivo pdf
# texto = procesar_arch_pdf(f"data_pdf/{arch[0]}")
# insertar_datos(texto, crear_embeddings(texto))

#procesar el archivo pdf que se encuentra en la base de datos
def procesar_arch_db(nombre_arch, arch, tipo):

    #cargar el modelo de embedding: en este caso usamos el modelo text-embedding-3-large
    openai.api_key = os.getenv("OPENAI_API_KEY")
    #crear el index de Pinecone
    index_name = "quillagpt-index"

    #guardar el documento en un archivo temporal
    archivo_temporal = nombre_arch
    with open(archivo_temporal, "wb") as f:
        f.write(arch.read())

    #inicializamos Pinecone
    pc = pinecone_init(index_name)

    #borramos en Pinecone los datos anteriores de la Guia del Panda
    index = pc.Index(index_name)
    for ids in index.list(prefix = tipo, namespace = "quillagpt-namespace"):
        index.delete(ids = ids, namespace = "quillagpt-namespace")

    #procesamos el archivo pdf y creamos los embeddings
    texto = procesar_arch_pdf(archivo_temporal)
    embeddings = crear_embeddings(texto)

    #insertamos los datos
    insertar_datos(texto, embeddings, pc, tipo, index_name)

    #borramos el archivo temporal
    os.remove(archivo_temporal)