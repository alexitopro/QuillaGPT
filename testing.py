from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
import os
from dotenv import load_dotenv

#cargar la variable de entorno
load_dotenv()

#inicializar Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

#cargar el modelo de embedding: en este caso usamos all mini lm l12 v2 de HuggingFace
model = SentenceTransformer('sentence-transformers/all-MiniLM-L12-v2')

index_name = "quillagpt-index"
index = pc.Index(index_name)

query = "Cual es el procedimiento para el reclamo de notas?"
query_embedding = model.encode([query])[0].tolist()
results = index.query(
    namespace = "quillagpt-namespace",
    vector = query_embedding,
    top_k = 2,
    include_values = False,
    include_metadata = True
)
print(results)

# from openai import OpenAI

# client = OpenAI(
#   base_url = "https://integrate.api.nvidia.com/v1",
#   api_key = os.getenv("OPENAI_API_KEY")
# )

# completion = client.chat.completions.create(
#   model="meta/llama-3.3-70b-instruct",
#   messages=[{"role":"user","content":"Say hello."}],
#   temperature=0.2,
#   top_p=0.7,
#   max_tokens=4096,
#   stream=True
# )

# for chunk in completion:
#   if chunk.choices[0].delta.content is not None:
#     print(chunk.choices[0].delta.content, end="")