import os
import sys
import json
import requests
import subprocess

from fastapi.responses import JSONResponse
from mongo_connector import MongoConnector
from fastapi import FastAPI, Response
from blockchain import Blockchain
from pydantic import BaseModel
from mangum import Mangum


app = FastAPI()
handler = Mangum(app)
mongodb = MongoConnector(os.environ.get("MONGO_URI"))
blockchain = Blockchain(mongodb, os.environ.get("USER"))


class User(BaseModel):
    name: str
    age: int


class Transaction(BaseModel):
    receiver: str
    amount: float


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
    print("html:", r.text)
    return {"statusCode": 200, "body": json.dumps("Hello from Lambda!")}


@app.post("/upload")
def upload(user: User):
    print(user)
    db = MongoConnector(os.environ.get("MONGO_URI"))
    dados = dict(user)
    db.insert_data(dict(user))

    return {"status": 200, "message": "Data uploaded successfully!", "data": dados}


@app.get("/get_chain")
def get_chain():
    response = {"chain": blockchain.chain, "length": len(blockchain.chain)}
    return JSONResponse(content=response, status_code=200)


@app.post("/add_transaction")
def add_transaction(transaction: Transaction):
    transaction_dict = dict(transaction)
    blockchain_users = blockchain.retrieve_users_in_chain()
    if transaction_dict["receiver"] in blockchain_users:
        index = blockchain.add_transaction(
            amount=transaction_dict["amount"],
            receiver=transaction_dict["receiver"],
        )
        response = {
            "message": f"This transaction will be included in the CBU blockchain in the block {index} when it is minerated by someone.",
            "transaction": transaction_dict
        }
        return JSONResponse(content=response, status_code=200)
    else:
        response = {
            "message": "Receiver not found in the blockchain.",
            "blockchain_users": blockchain_users,
        }
        return JSONResponse(content=response, status_code=400)


@app.get("/mine_block")
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block["proof"]
    blockchain.add_transaction(sender="miner", amount=10)
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash).get("chain")[-1]
    response = {
        "message": "Congrats! You have minered a block!",
        "block": block,
    }
    return response


# @app.route("/connect_node", methods=["POST"])
# def connect_node():
#     json = request.get_json()
#     nodes = json.get("nodes")
#     if nodes is None:
#         return "Sem nós no arquivo.", 400
#     for node in nodes:
#         blockchain.add_node(node)
#     response = {
#         "message": "Todos nós conectados. O Blockchain contém os seguintes nós:",
#         "total_nodes": list(blockchain.nodes),
#     }
#     return jsonify(response), 201


# @app.route("/replace_chain", methods=["GET"])
# def replace_chain():
#     is_chain_replaced = blockchain.replace_chain()
#     if is_chain_replaced:
#         response = {
#             "message": "Os nós tinham cadeias diferentes, então foi substituída.",
#             "new_chain": blockchain.chain,
#         }
#     else:
#         response = {
#             "message": "Tudo certo, não houve substituição.",
#             "actual_chain": blockchain.chain,
#         }
#     return jsonify(response), 201


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
