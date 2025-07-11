import time
import os
import json
from dotenv import load_dotenv
import openai

def create_web_scraping_embeddings():

    from pinecone import Pinecone, ServerlessSpec

    #cargar la variable de entorno
    load_dotenv()

    #inicializar Pinecone
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

    #cargar el modelo de embedding: en este caso usamos el modelo text-embedding-3-large
    openai.api_key = os.getenv("OPENAI_API_KEY")

    #cargamos la data que se usara para generar los embeddings, proviene de la carpeta data
    data = []
    for file in os.listdir("data"):
        if file.startswith("tramites"):
            with open(f"data/{file}", "r") as f:
                file_data = json.load(f)
                data.extend(file_data)

    #crear embeddings para nombre
    texts = [d["nombre"] for d in data]

    def get_embeddings(texts):
        response = openai.embeddings.create(
            model="text-embedding-3-large",
            input=texts
        )
        return [embedding.embedding for embedding in response.data]
    embeddings = get_embeddings(texts)

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

    #borramos en Pinecone los datos anteriores del Web Scraping
    index = pc.Index(index_name)
    for ids in index.list(prefix = "FCI_WebScraping_", namespace = "quillagpt-namespace"):
        index.delete(ids = ids, namespace = "quillagpt-namespace")

    #preparar para el insertado de los datos
    records = [
        {
            "id": f"{'FCI_WebScraping_'}{idx}",
            "values": embedding,
            "metadata": d
        }
        for idx, (d, embedding) in enumerate(zip(data, embeddings))
    ]

    #insertar los datos en el index
    index.upsert(vectors = records, namespace = "quillagpt-namespace")