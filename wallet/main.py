from fastapi import FastAPI
from mangum import Mangum
import uvicorn

app = FastAPI()
handler = Mangum(app)

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
def search(query: str):
    return {"Welcome Home!": "You are always welcome here."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")