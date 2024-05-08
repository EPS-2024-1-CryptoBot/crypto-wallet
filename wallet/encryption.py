from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()
handler = Mangum(app)

@app.get("/")
def root():
    return {"RSA Key Generator": "CryptoBot_UnB_2024.1"}

@app.get("/keygen/rsa")
def rsa_keygen():
    c = Cryptography()
    c.generate_keys()
    return c.keys


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

    def sign(self, message, private_key):
        if private_key:
            print("Private key exists")
            key_to_verify = serialization.load_pem_private_key(
                bytes.fromhex(private_key), password=None, backend=default_backend()
            )
        else:
            print("No private_key")
            key_to_verify = self.__private_key
        signature = key_to_verify.sign(
            message.encode(), padding.PKCS1v15(), hashes.SHA256()
        )
        return signature.hex()

    def verify_signature(self, message, signature, public_key=None):
        if public_key:
            print("Public key exists")
            key_to_verify = serialization.load_pem_public_key(
                bytes.fromhex(public_key), backend=default_backend()
            )
        else:
            print("No public_key")
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9000, log_level="info")