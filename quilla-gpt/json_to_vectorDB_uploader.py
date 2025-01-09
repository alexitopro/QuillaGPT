from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
import time
import streamlit as st

def create_query_embedding(arch_json):
    #inicializar Pinecone
    pc = Pinecone(api_key=st.secrets["pinecone"]["PINECONE_API_KEY"])

    #cargar el modelo de embedding: en este caso usamos all mini lm l12 v2 de HuggingFace
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L12-v2')

    #values de pinecone sera la pregunta de la query
    texts = [d["nombre"] for d in arch_json]
    embeddings = model.encode(texts).tolist()

    #crear el index de Pinecone
    index_name = "quillagpt-index"

    if not pc.has_index(index_name):
        pc.create_index(
            name = index_name,
            dimension = 384,  #dimensiones del modelo a utilizar
            metric = "cosine",
            spec = ServerlessSpec(cloud="aws", region="us-east-1")
        )

    #esperar a que el index este listo
    while not pc.describe_index(index_name).status['ready']:
        time.sleep(1)

    #obtener el index
    index = pc.Index(index_name)

    #preparar para el insertado de los datos
    records = [
        {
            "id": str(idx),
            "values": embedding,
            "metadata": d
        }
        for idx, (d, embedding) in enumerate(zip(arch_json, embeddings))
    ]

    #insertar los datos en el index
    index.upsert(vectors = records, namespace = "quillagpt-namespace")