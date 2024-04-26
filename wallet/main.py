from fastapi import FastAPI
from pydantic import BaseModel
from mangum import Mangum
from mongo_connector import MongoConnector
import os
import requests
import json
import subprocess
from flask import Flask, request, jsonify  # envia/recebe as requisições
import sys

app = FastAPI()
handler = Mangum(app)

class User(BaseModel):
    name: str
    age: int

@app.get("/")
def read_root():
    """
    This is the root path of the API
    """
    return {"WalletAPI": "CryptoBot_UnB_2024.1"}

@app.get("/search")
def search(query: str):
    return {"Search": "You searched for {query}".format(query=query)}

@app.get("/home")
def home():
    return {"Welcome Home!": "You are always welcome here."}

@app.get("/google")
def google():
    url = "https://google.com.br"
    r = requests.get(url)
    print("html:", r. text)
    return {
        'statusCode': 200,
        'body': json.dumps ('Hello from Lambda!')
    }

@app.post("/upload")
def upload(user: User):
    print(user)
    db = MongoConnector(os.environ.get("MONGO_URI"))
    dados = dict(user)
    db.insert_data(dict(user))
    # return {"status": 200}
    return {"status": 200, "message": "Data uploaded successfully!", "data": dados}

@app.get("/start_nodes")
def start_nodes():
 # Inicia os três nós, especificando a porta de cada um
    start_node('node_01.py', 5001)  # Inicia o nó 1 na porta 5001
    start_node('node_02.py', 5002)  # Inicia o nó 2 na porta 5002
    start_node('node_03.py', 5003)  # Inicia o nó 3 na porta 5003
    return {"status": 200, "message": "Nodes started successfully!"}

def start_node(file, port):
    # Caminho do arquivo do nó
    node_path = f'blockchain/{file}'
    # Verifica se o arquivo existe antes de executar o subprocesso
    if os.path.exists(node_path):
        # Inicia um nó em um processo separado
        subprocess.Popen([sys.executable, node_path], env={"PORT": str(port)})
        print(f"Nó iniciado: {file} na porta {port}")
    else:
        print(f"Erro: Arquivo {file} não encontrado em {node_path}")


if __name__ == "__main__":
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    
