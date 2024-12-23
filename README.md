# QuillaGPT
QuillaGPT is a chatbot that uses RAG capabilities to assist with the processes of the School of Science and Engineering at Pontificia Universidad Católica del Perú
## Usage
To run the app, you will need to have Python installed on your machine. You then create a new isolated Python environment inside the venv directory to avoid potential conflicts with other Python projects.
```
python3 -m venv venv
```
You then need to activate the virtual environment
```
source venv/bin/activate
```
You can install the required dependencies by running the following command in your terminal:
```
pip install -r requirements.txt
```
1. **Selenium** is used for automated browser interactions.
2. **LangChain** is a framework designed to simplify the development of applications powered by Large Language Models (LLMs).
3. **LangChain-community** contains pre-built components that are not part of the core LangChain package.
4. **LangChain-pinecone** allows integration of LangChain with Pinecone, a vector database for similarity search and retrieval.
5. **LangChain-core** contains components for managing prompts, chaining models and databases.
6. **LangChain-openai** allows integration of LangChain with OpenAI's GPT models.
7. **LangChain-text-splitters** provides utilities for splitting text into smaller, more manageable chunks, especially useful when working with large documents.
8. **Python-dotenv** helps manage environment variables by loading them from .env files into our Python environment.
9. **Unstructured** converts unstructured data into structured data that can be processed and analyzed.
10. **Streamlit** is a framework for building interactive web applications for data science and machine learning projects.
11. **Sentence-transformers** is used for getting access to the embeddings model
You then run scraper.py inside scraper folder to retrieve foundational data from the seletect sources
```
python3 scraper.py
```
You then create the embeddings and place them inside the Pinecone vector database
```
python3 create_embeddings.py
```
## Contributing
This repository is intended only for educational purposes.