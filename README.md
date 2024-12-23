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