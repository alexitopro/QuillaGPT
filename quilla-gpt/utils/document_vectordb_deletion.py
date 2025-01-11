import streamlit as st

#conectarse a pinecone y crear un index si tdv no se ha hecho
def pinecone_init(index_name):
    from pinecone import Pinecone, ServerlessSpec
    #inicializar Pinecone
    pc = Pinecone(api_key=st.secrets["pinecone"]["PINECONE_API_KEY"])

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
    #crear el index de Pinecone
    index_name = "quillagpt-index"

    #inicializamos Pinecone
    pc = pinecone_init(index_name)

    #borramos en Pinecone los datos anteriores de la Guia del Panda
    index = pc.Index(index_name)
    for ids in index.list(prefix = tipo, namespace = "quillagpt-namespace"):
        index.delete(ids = ids, namespace = "quillagpt-namespace")