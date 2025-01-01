import os
import re
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import streamlit as st

#cargar la variable de entorno
load_dotenv()

#cargar el modelo de embedding: en este caso usamos all mini lm l12 v2 de HuggingFace
model = SentenceTransformer('sentence-transformers/all-MiniLM-L12-v2')
#crear el index de Pinecone
index_name = "quillagpt-index"

#conectarse a pinecone y crear un index si tdv no se ha hecho
def pinecone_init():
    #inicializar Pinecone
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

    if not pc.has_index(index_name):
        pc.create_index(
            name = index_name,
            dimension = 384,  #dimensiones del modelo a utilizar
            metric = "cosine",
            spec = ServerlessSpec(cloud="aws", region="us-east-1")
        )
    
    return pc

#eliminar el archivo pdf que se encuentra en la base de datos
def eliminar_arch_db(tipo):
    #inicializamos Pinecone
    pc = pinecone_init()

    #borramos en Pinecone los datos anteriores de la Guia del Panda
    index = pc.Index(index_name)
    for ids in index.list(prefix = tipo, namespace = "quillagpt-namespace"):
        index.delete(ids = ids, namespace = "quillagpt-namespace")