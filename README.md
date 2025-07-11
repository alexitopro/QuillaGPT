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
You then run the FastApi server before the main web application inside the fastapi folder
```
uvicorn main:app --reload
```
Finally, run the main web application inside quilla-gpt folder
```
streamlit run main.py
```
## Contributing
This repository is intended only for educational purposes.