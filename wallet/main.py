from fastapi import FastAPI
from mangum import Mangum
import uvicorn

app = FastAPI()
handler = Mangum(app)

@app.get("/")
def read_root():
    return {"WalletAPI": "CryptoBot_UnB_2024.1"}

@app.get("/search")
def search(query: str):
    return {"Search": "You searched for {query}".format(query=query)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")