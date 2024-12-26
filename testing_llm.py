from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = "quillagpt-index"
index = pc.Index(index_name)

# Load the model for embedding generation
model = SentenceTransformer('sentence-transformers/all-MiniLM-L12-v2')

# Query you want to search in the vector DB
query = "Cual es el procedimiento para el reclamo de notas?"
query_embedding = model.encode([query])[0].tolist()

# Query Pinecone index
results = index.query(
    namespace="quillagpt-namespace",
    vector=query_embedding,
    top_k=3,  # You can change this value to get more results
    include_values=False,
    include_metadata=True
)

# Extract relevant data from Pinecone results
retrieved_documents = [f"Metadata: {result['metadata']}" for result in results['matches']]

# Now connect to LLM (e.g., OpenAI or any LLM API)
client = OpenAI(
  base_url="https://integrate.api.nvidia.com/v1",
  api_key=os.getenv("OPENAI_API_KEY")
)

# Combine the retrieved documents as context for LLM
context = "\n".join(retrieved_documents)

# Send the query and context to the LLM
completion = client.chat.completions.create(
    model="meta/llama-3.3-70b-instruct",
    messages=[
        {"role": "system", "content": "Te llamas QuillaGPT y ayudas sobre procesos academico administrativos de la PUCP. Menciona sobre que fuente has sacado informacion y si es de la guia del panda menciona que pagina el usuario puede encontrar mas informacion. Asimismo, si hay algún link de interés, compártelo."},
        {"role": "user", "content": query},
        {"role": "assistant", "content": context}  # Pass the context as part of the conversation
    ],
    temperature=0.2,
    top_p=0.7,
    max_tokens=8192,
    stream=True
)

# Print the LLM response
for chunk in completion:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")