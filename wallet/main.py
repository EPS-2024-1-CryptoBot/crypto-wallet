from fastapi import FastAPI
from pydantic import BaseModel
from mangum import Mangum
from mongo_connector import MongoConnector

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

@app.post("/upload")
async def upload(user: User):
    db = MongoConnector()
    await db.insert_data(dict(user))
    return {"status": 200, "message": "Data uploaded successfully!", "data": user}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")