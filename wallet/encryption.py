import hashlib

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding


class Cryptography:
    def __init__(self):
        self.__private_key = None
        self.__public_key = None

    def generate_keys(self):
        self.__private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.__public_key = self.__private_key.public_key()

    def load_keys(self, public_key: hex, private_key: hex):
        self.__private_key = (
            serialization.load_pem_private_key(
                bytes.fromhex(private_key),
                password=None,
                backend=default_backend()
            )
        )
        self.__public_key = (
            serialization.load_pem_public_key(
                bytes.fromhex(public_key),
                backend=default_backend()
            )
        )

    @property
    def keys(self):
        return {
            "private_key": (
            self.__private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).hex()
        ),
            "public_key": (
            self.__public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).hex()
        ),
        }

    def sign(self, message, private_key):
        if private_key:
            print("Private key exists")
            key_to_verify = (
                serialization.load_pem_private_key(
                    bytes.fromhex(private_key),
                    password=None,
                    backend=default_backend()
                )
            )
        else:
            print("No private_key")
            key_to_verify = self.__private_key
        signature = key_to_verify.sign(
            message.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return signature.hex()

    def verify_signature(self, message, signature, public_key=None):
        if public_key:
            print("Public key exists")
            key_to_verify = (
                serialization.load_pem_public_key(
                    bytes.fromhex(public_key),
                    backend=default_backend()
                )
            )
        else:
            print("No public_key")
            key_to_verify = self.__public_key
        try:
            key_to_verify.verify(
                bytes.fromhex(signature),
                message.encode(),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False

if __name__ == "__main__":

    import json
    def hash(block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    c = Cryptography()
    c.generate_keys()

    msg = {
        "hello": {
            "message": "Hello from Lambda!"
        },
        "number": 423
    }
    msg_hex = hash(
        json.dumps(
            obj=msg,
            sort_keys=True,
        )
    )

    sig = c.sign(msg_hex, c.keys.get("private_key"))

    with open("keys.json", "w") as f:
        f.write(json.dumps({"data": {"normal": msg, "hex": msg_hex, "sig": sig}, "keys": c.keys}))

    with open("keys.json", "r") as f:
        file = json.loads(f.read())
        # c.load_keys(
        #     public_key=file["keys"]["public_key"],
        #     private_key=file["keys"]["private_key"]
        # )
        v = c.verify_signature(file["data"]["hex"], file["data"]["sig"], file["keys"]["public_key"])
        print(v)