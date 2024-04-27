import hashlib

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding


class Cryptography:
    def __init__(self):
        self.private_key = None
        self.public_key = None

    def verify(self, encryption, public_key, hash):
        alleged_public_key = (
            serialization.load_pem_public_key(
                bytes.fromhex(public_key),
                backend=default_backend()
            )
        )
        msg = self.decrypt(bytes.fromhex(encryption), alleged_public_key)
        return msg == hash

    def load_keys(self, public_key, private_key):
        self.private_key = (
            serialization.load_pem_private_key(
                private_key,
                password=None,
                backend=default_backend()
            )
        )
        self.public_key = (
            serialization.load_pem_public_key(
                public_key,
                backend=default_backend()
            )
        )

    @property
    def keys(self):
        return {
            "private_key": (
            self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        ),
            "public_key": (
            self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        ),
        }

    def generate_keys(self):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()

    def encrypt(self, message, public_key=None):
        public_key = public_key or self.public_key
        encrypted = public_key.encrypt(
            message.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return encrypted

    def decrypt(self, encrypted, private_key=None):
        private_key = private_key or self.private_key
        decrypted = private_key.decrypt(
            encrypted,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted.decode()
    
    def sign(self, message, private_key=None):
        private_key = private_key or self.private_key
        signature = private_key.sign(
            message.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature

    def verify_signature(self, message, signature, public_key=None):
        alleged_public_key = (
            serialization.load_pem_public_key(
                public_key,
                backend=default_backend()
            )
        )
        public_key = alleged_public_key or public_key or self.public_key
        try:
            public_key.verify(
                signature,
                message.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False

if __name__ == "__main__":
    crypto = Cryptography()
    crypto.generate_keys()

    message = "Hello, this is a secret message!"

    # Sign the message
    signature = crypto.sign(message)
    print("Signature:", signature, type(signature))

    # Verify the signature
    verified = crypto.verify_signature(message, signature)
    print("Signature verified:", verified)
