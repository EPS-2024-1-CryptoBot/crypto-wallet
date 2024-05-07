import json
import os

import requests
from blockchain import Blockchain
from encryption import Cryptography
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from mangum import Mangum
from mongo_connector import MongoConnector
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI()
handler = Mangum(app)
mongodb = MongoConnector(os.environ.get("MONGO_URI"))
blockchain = Blockchain(mongodb, os.environ.get("USER"))
encryption = Cryptography()

included_routes = [
    "/get_chain",
    "/add_transaction",
    "/mine_block",
    "/validate_chain",
    "/get_balance",
]

class MiddleWare(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        global included_routes
        if request.url.path in included_routes:
            print(request.url.path=="/docs")
            try:
                user = request.query_params.get("user")
                set_user(user)
            except:
                return JSONResponse({"message": f"User can't be {type(user)} type", "required_query_param": "user"}, status_code=400)

            global blockchain
            blockchain = Blockchain(mongodb, os.environ.get("USER"))
            
        response = await call_next(request)
        return response

app.add_middleware(MiddleWare)


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

## BLOCKCHAIN

def set_user(user: str):
    os.environ["USER"] = user
    blockchain.user = user

@app.get("/get_chain")
def get_chain(user: str):
    blockchain.retrieve_blockchain()
    response = {"chain": blockchain.chain, "length": len(blockchain.chain)}
    return JSONResponse(content=response, status_code=200)


@app.post("/add_transaction")
def add_transaction(transaction: Transaction, user: str):
    transaction_dict = dict(transaction)
    blockchain_users = blockchain.retrieve_users_in_chain()

    sender_balance = get_balance("durso")  # TROCAR USER HARD CODED
    if sender_balance < transaction_dict["amount"]:
        return JSONResponse(
            content={"message": "Insufficient balance.", "Saldo:": sender_balance},
            status_code=400,
        )

    if transaction_dict["receiver"] in blockchain_users:
        index = blockchain.add_transaction(
            amount=transaction_dict["amount"],
            receiver=transaction_dict["receiver"],
        )
        response = {
            "message": f"This transaction will be included in the CBU blockchain in the block {index} when it is minerated by someone.",
            "transaction": transaction_dict,
        }
        return JSONResponse(content=response, status_code=200)
    else:
        response = {
            "message": "Receiver not found in the blockchain.",
            "blockchain_users": blockchain_users,
        }
        return JSONResponse(content=response, status_code=400)


@app.get("/mine_block")
def mine_block(user: str):
    blockchain.sync_chain()  # sync the chain before mining
    blockchain.retrieve_blockchain()  # retrieve the chain

    """ 
    Commented code below is the old way of validating the chain.
    Right now, the chain is being validated before mining.
    """
    # is_valid = blockchain.is_chain_valid()
    # if not is_valid:
    #     invalid_block_index = blockchain.get_invalid_block_index()
    #     blockchain.revalidate_chain(invalid_block_index)

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


@app.get("/validate_chain")
def validate_chain(user: str):
    """
    This endpoint validates the blockchain.
    """
    blockchain.retrieve_blockchain()
    blockchain.retrieve_transactions()
    is_valid = blockchain.is_chain_valid()
    response = {
        "message": (
            "The blockchain is valid." if is_valid else "The blockchain is not valid."
        ),
        "chain": blockchain.chain,
    }
    return JSONResponse(content=response, status_code=200)


@app.get("/get_balance")
def get_balance(user: str):
    return blockchain.get_balance(os.environ.get("USER"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
