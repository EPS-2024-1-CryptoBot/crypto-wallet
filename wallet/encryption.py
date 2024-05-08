import os

from typing import Union, List
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from pydantic import BaseModel
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()
handler = Mangum(app)
backend_pvt_k = os.environ.get("BACKEND_PVT_K")
backend_pub_k = os.environ.get("BACKEND_PUB_K")

class Encryption(BaseModel):
    message: str
    public_key: str

class Decryption(BaseModel):
    message: str
    private_key: Union[str, List[str]]

@app.get("/")
def root():
    return {"RSA Key Generator": "CryptoBot_UnB_2024.1"}

@app.get("/rsa/keygen")
def rsa_keygen(encrypt: bool):
    c = Cryptography()
    c.generate_keys()
    chunk = 190
    response = {
        "public_key": c.keys.get("public_key"),
        "private_encrypted_key": [c.encrypt(c.keys.get("private_key")[max(0,i-chunk):i], backend_pub_k) for i in range(chunk,len(c.keys.get("private_key")),chunk)] + [c.encrypt(c.keys.get("private_key")[-(len(c.keys.get("private_key"))%chunk):], backend_pub_k)],
    } if encrypt else {
        "public_key": c.keys.get("public_key"),
        "private_key": c.keys.get("private_key"),
    }
    return response

@app.post("/rsa/encrypt")
def encrypt_msg(encrypt: Encryption):
    c = Cryptography()
    return {"message": encrypt.message, "encrypted_message": c.encrypt(encrypt.message, encrypt.public_key)}

@app.post("/rsa/decrypt")
def decrypt_msg(decrypt: Decryption):
    c = Cryptography()
    pvk = c.retrieve_pvk(decrypt.private_key)
    return {"encrypted_message": decrypt.message, "decrypted_message": c.decrypt(decrypt.message, pvk)}


class Cryptography:
    def __init__(self):
        self.__private_key = None
        self.__public_key = None

    def generate_keys(self):
        self.__private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )
        self.__public_key = self.__private_key.public_key()

    def load_keys(self, public_key: hex, private_key: hex):
        self.__private_key = serialization.load_pem_private_key(
            bytes.fromhex(private_key), password=None, backend=default_backend()
        )
        self.__public_key = serialization.load_pem_public_key(
            bytes.fromhex(public_key), backend=default_backend()
        )

    @property
    def keys(self):
        return {
            "private_key": (
                self.__private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                ).hex()
            ),
            "public_key": (
                self.__public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo,
                ).hex()
            ),
        }

    def sign(self, message, private_key=None):
        if private_key:
            key_to_verify = serialization.load_pem_private_key(
                bytes.fromhex(private_key), password=None, backend=default_backend()
            )
        else:
            key_to_verify = self.__private_key
        signature = key_to_verify.sign(
            message.encode(), padding.PKCS1v15(), hashes.SHA256()
        )
        return signature.hex()

    def verify_signature(self, message, signature, public_key=None):
        if public_key:
            key_to_verify = serialization.load_pem_public_key(
                bytes.fromhex(public_key), backend=default_backend()
            )
        else:
            key_to_verify = self.__public_key
        try:
            key_to_verify.verify(
                bytes.fromhex(signature),
                message.encode(),
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
            return True
        except Exception:
            return False
        
    def encrypt(self, message, public_key=None):
        if public_key:
            key_to_verify = serialization.load_pem_public_key(
                bytes.fromhex(public_key), backend=default_backend()
            )
        else:
            print("No public_key")
            key_to_verify = self.__public_key
        encrypted_message = key_to_verify.encrypt(
            message.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            )
        )
        return encrypted_message.hex()

    def decrypt(self, encrypted_message, private_key=None):
        if private_key:
            key_to_verify = serialization.load_pem_private_key(
                bytes.fromhex(private_key), password=None, backend=default_backend()
            )
        else:
            key_to_verify = self.__private_key
        decrypted_message = key_to_verify.decrypt(
            bytes.fromhex(encrypted_message),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            )
        )
        return decrypted_message.decode()
    
    def retrieve_pvk(self, pvk_chunks):
        if isinstance(pvk_chunks, List):
            pvk = "".join([self.decrypt(pvk_chunk, backend_pvt_k) for pvk_chunk in pvk_chunks])
        else:
            pvk = pvk_chunks
        return pvk


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9000, log_level="info")