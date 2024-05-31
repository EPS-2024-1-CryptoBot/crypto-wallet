import os

from blockchain import Blockchain
from encryption import Cryptography
from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse
from mangum import Mangum
from mongo_connector import MongoConnector
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI()
handler = Mangum(app)
if not os.environ.get("TESTING"): # pragma: no cover
    mongodb = MongoConnector(os.environ.get("MONGO_URI"))
    blockchain = Blockchain(mongodb, os.environ.get("USER"))
    encryption = Cryptography()
else:
    mongodb = None
    blockchain = None
    encryption = None

included_routes = [
    "/get_chain",
    "/add_transaction",
    "/mine_block",
    "/validate_chain",
    "/get_balance",
    "/get_transactions"
]


class MiddleWare(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        global included_routes
        if request.url.path in included_routes:
            try:
                user = request.query_params.get("user")
                set_user(user)
            except:
                return JSONResponse(
                    {
                        "message": f"User can't be {type(user)} type",
                        "required_query_param": "user",
                    },
                    status_code=400,
                )

            global blockchain
            blockchain = Blockchain(mongodb, os.environ.get("USER"))

        response = await call_next(request)
        return response


app.add_middleware(MiddleWare)


class Transaction(BaseModel):
    receiver: str = Field(..., example="brasil")
    amount: float = Field(..., example="5")


@app.get("/")
def read_root():
    """
    This is the root path of the API
    """
    return {"WalletAPI": "CryptoBot_UnB_2024.1"}


## BLOCKCHAIN


def set_user(user: str):
    """
    This function sets the user in the environment variable and in the blockchain object.
    """
    os.environ["USER"] = user
    blockchain.user = user


@app.get("/get_chain", tags=["Blockchain"])
def get_chain(user : str = Query(None, description="User to get the blockchain from", example="fKhB1D6BBNMQpoGw7ogSwp4U8Z62")):
    """
    ```
    Retrieves the blockchain of a specific user.

    Query Params:
        user (str): User to get the blockchain from.

    Returns:
        JSONResponse: A JSON response containing:
            - "chain" (list): The blockchain of the specified user.
            - "length" (int): The length of the blockchain.
    ```
    """

    blockchain.retrieve_blockchain()
    response = {"chain": blockchain.chain, "length": len(blockchain.chain)}
    return JSONResponse(content=response, status_code=200)


@app.post("/add_transaction", tags=["Blockchain"])
def add_transaction(
    transaction: Transaction,
    user : str = Query(None, description="User to get the blockchain from", example="fKhB1D6BBNMQpoGw7ogSwp4U8Z62")
):
    """
    ```
    Adds a transaction to the blockchain.

    Parameters:
        transaction (Transaction): The transaction to be added to the blockchain.
        user (str): User to get the blockchain from.

    Returns:
        JSONResponse: A JSON response containing:
            - "message" (str): A message indicating the status of the transaction.
            - "transaction" (dict): The details of the added transaction.
    ```
    """
    transaction_dict = dict(transaction)
    blockchain_users = blockchain.retrieve_users_in_chain()

    sender_balance = blockchain.get_balance(blockchain.user)
    if sender_balance < transaction_dict["amount"]:
        return JSONResponse(
            content={
                "message": "Insufficient balance.",
                "user": blockchain.user,
                "balance:": sender_balance,
            },
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


@app.get("/mine_block", tags=["Blockchain"])
def mine_block(user : str = Query(None, description="User to get the blockchain from", example="fKhB1D6BBNMQpoGw7ogSwp4U8Z62")):
    """
    ```
    Mines a block in the blockchain.

    Query Params:
        user (str): User to get the blockchain from.

    Returns:
        dict: A dictionary containing:
            - "message" (str): A message indicating the success of mining.
            - "block" (dict): The mined block details.
    ```
    """
    blockchain.sync_chain()  # sync the chain before mining
    blockchain.retrieve_blockchain()  # retrieve the chain

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


@app.get("/validate_chain", tags=["Blockchain"])
def validate_chain(user : str = Query(None, description="User to get the blockchain from", example="fKhB1D6BBNMQpoGw7ogSwp4U8Z62")):
    """
    ````
    Validates the blockchain.

    Query Params:
        user (str): User to get the blockchain from.

    Returns:
        JSONResponse: A JSON response containing:
            - "message" (str): A message indicating the validity of the blockchain.
            - "chain" (list): The blockchain.
    ````
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


@app.get("/get_balance", tags=["Blockchain"])
def get_balance(user : str = Query(None, description="User to get the blockchain from", example="fKhB1D6BBNMQpoGw7ogSwp4U8Z62")):
    """
    ````
    Retrieves the balance of a specific user.

    Query Params:
        user (str): User to get the blockchain from.

    Returns:
        JSONResponse: A JSON response containing:
            - "balance" (float): The balance of the specified user.
    ````
    """
    response = {
        "balance": blockchain.get_balance(blockchain.user),
    }
    return JSONResponse(content=response, status_code=200)


@app.get("/get_transactions", tags=["Blockchain"])
def get_transactions(user : str = Query(None, description="User to get the blockchain from", example="fKhB1D6BBNMQpoGw7ogSwp4U8Z62")):
    """
    ```
    Retrieves the transactions of a specific user.

    Query Params:
        user (str): User to get the blockchain from.

    Returns:
        JSONResponse: A JSON response containing the transactions of the specified user.
    ```
    """

    user_transactions = blockchain.get_transactions(blockchain.user)
    return user_transactions

if __name__ == "__main__": # pragma: no cover
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
