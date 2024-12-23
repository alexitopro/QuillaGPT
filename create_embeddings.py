from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
import time
import os
import json
from dotenv import load_dotenv

#cargar la variable de entorno
load_dotenv()

#inicializar Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

#cargar el modelo de embedding: en este caso usamos all mini lm l12 v2 de HuggingFace
model = SentenceTransformer('sentence-transformers/all-MiniLM-L12-v2')

#cargamos la data que se usara para generar los embeddings, proviene de la carpeta data
data = []
for file in os.listdir("data"):
    with open(f"data/{file}", "r") as f:
        file_data = json.load(f)
        data.extend(file_data)

#guardar la data en un json
# with open("data.json", "w", encoding = "utf-8") as f:
#     json.dump(data, f, ensure_ascii = False, indent = 4)

#crear embeddings para nombre
texts = [d["nombre"] for d in data]
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
    for idx, (d, embedding) in enumerate(zip(data, embeddings))
]

#insertar los datos en el index
index.upsert(vectors = records, namespace = "quillagpt-namespace")

#esperar a que los datos se inserten
time.sleep(30)

#probar la entrega de resultados
query = "Hay algo relacionado con reconocimiento de cursos?"
query_embedding = model.encode([query])[0].tolist()
results = index.query(
    namespace = "quillagpt-namespace",
    vector = query_embedding,
    top_k = 3,
    include_values = False,
    include_metadata = True
)
print(results)