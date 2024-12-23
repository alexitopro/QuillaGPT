from pinecone import Pinecone, ServerlessSpec
import time
import os
from dotenv import load_dotenv

load_dotenv()
# Initialize a Pinecone client with your API key
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Define a sample dataset where each item has a unique ID and piece of text
data = [
    {
        "nombre": "Constancias especiales",
        "link": "https://www.google.com/url?q=https%3A%2F%2Fpucp.kissflow.com%2Fpublic%2FProcess%2FPf8ed89502-d2cc-482b-90ab-b5f999de958a&sa=D&sntz=1&usg=AOvVaw2CrmYnBaBRCwqdi5jnfflk",
        "fecha de extracción": "2024-12-23 12:14:24",
        "contacto": "mailto:informes-fci@pucp.edu.pe"
    },
    {
        "nombre": "Reconocimiento de cursos",
        "link": "https://www.google.com/url?q=https%3A%2F%2Fpucp.kissflow.com%2Fpublic%2FProcess%2FPf594a9ec1-91d4-47ee-990e-e8ecab984434&sa=D&sntz=1&usg=AOvVaw2Ma4HCkKyClkEfdX5v1n-S",
        "fecha de extracción": "2024-12-23 12:14:24",
        "contacto": "mailto:informes-fci@pucp.edu.pe"
    },
    {
        "nombre": "Convalidación de cursos (no PUCP)",
        "link": "https://www.google.com/url?q=https%3A%2F%2Fpucp.kissflow.com%2Fpublic%2FProcess%2FPf9b0d6f08-2880-4c40-b3c5-d7657dddc3fc&sa=D&sntz=1&usg=AOvVaw3MwsTs2Lh51Tc8Q_3jsmMK",
        "fecha de extracción": "2024-12-23 12:14:24",
        "contacto": "mailto:informes-fci@pucp.edu.pe"
    },
    {
        "nombre": "Autorización de cuarta matrícula o permanencia (1era instancia)",
        "link": "https://forms.gle/7R5VAM47dTTzcM6c8",
        "fecha de extracción": "2024-12-23 12:14:24",
        "contacto": "mailto:informes-fci@pucp.edu.pe"
    },
    {
        "nombre": "Reconsideración de permanencia denegada (2° instancia)",
        "link": "https://forms.gle/7R5VAM47dTTzcM6c8",
        "fecha de extracción": "2024-12-23 12:14:24",
        "contacto": "mailto:informes-fci@pucp.edu.pe"
    }
]

# Convert the text into numerical vectors that Pinecone can index
embeddings = pc.inference.embed(
    model="multilingual-e5-large",
    inputs=[d['nombre'] for d in data],
    parameters={"input_type": "passage", "truncate": "END"}
)

print(embeddings)

# Create a serverless index
index_name = "example-index"

if not pc.has_index(index_name):
    pc.create_index(
        name=index_name,
        dimension=1024,
        metric="cosine",
        spec=ServerlessSpec(
            cloud='aws', 
            region='us-east-1'
        ) 
    ) 

# Wait for the index to be ready
while not pc.describe_index(index_name).status['ready']:
    time.sleep(1)

# Target the index where you'll store the vector embeddings
index = pc.Index("example-index")

# Prepare the records for upsert
# Each contains an 'id', the embedding 'values', and the original text as 'metadata'
records = []
for idx, (d, embedding) in enumerate(zip(data, embeddings)):
    records.append({
        "id": str(idx),
        "values": embedding['values'],
        "metadata": d
    })

# Upsert the records into the index
index.upsert(
    vectors=records,
    namespace="example-namespace"
)

time.sleep(10)  # Wait for the upserted vectors to be indexed

print(index.describe_index_stats())

# Define your query
query = "Hay algo relacionado con reconocimiento de cursos?"

# Convert the query into a numerical vector that Pinecone can search with
query_embedding = pc.inference.embed(
    model="multilingual-e5-large",
    inputs=[query],
    parameters={
        "input_type": "query"
    }
)

# Search the index for the three most similar vectors
results = index.query(
    namespace="example-namespace",
    vector=query_embedding[0].values,
    top_k=3,
    include_values=False,
    include_metadata=True
)

print(results)