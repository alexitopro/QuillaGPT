import time
import streamlit as st
import os
import openai

def create_query_embedding(arch_json):
    from pinecone import Pinecone, ServerlessSpec
    
    #inicializar Pinecone
    pc = Pinecone(api_key=st.secrets["pinecone"]["PINECONE_API_KEY"])

    #cargar el modelo de embedding: en este caso usamos el modelo text-embedding-3-large
    openai.api_key = os.getenv("OPENAI_API_KEY")

    #values de pinecone sera la pregunta de la query
    texts = [arch_json['consulta']]
    def crear_embeddings_openai(textos):
        response = openai.embeddings.create(
            model="text-embedding-3-large",
            input=textos
        )
        return [embedding.embedding for embedding in response.data]
    embeddings = crear_embeddings_openai(texts)

    #crear el index de Pinecone
    index_name = "quillagpt-index"

    if not pc.has_index(index_name):
        pc.create_index(
            name = index_name,
            dimension = 3072,  #dimensiones del modelo a utilizar
            metric = "cosine",
            spec = ServerlessSpec(cloud="aws", region="us-east-1")
        )

    #esperar a que el index este listo
    while not pc.describe_index(index_name).status['ready']:
        time.sleep(1)

    #obtener el index
    index = pc.Index(index_name)

    #preparar para el insertado de los datos
    tipo = "ConsultaDerivada_"
    records = [
        {
            "id": f"{tipo}{arch_json['id']}",
            "values": embedding,
            "metadata": arch_json
        }
        for _, embedding in enumerate(embeddings)
    ]

    #insertar los datos en el index
    index.upsert(vectors = records, namespace = "quillagpt-namespace")