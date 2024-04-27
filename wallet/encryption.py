from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding


class Cryptography:
    def __init__(self):
        self.private_key = None
        self.public_key = None

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

    def save_keys_file(self, private_key_file="private_key.pem", public_key_file="public_key.pem"):
        with open(private_key_file, "wb") as f:
            f.write(self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        with open(public_key_file, "wb") as f:
            f.write(self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))

    def load_keys_file(self, private_key_file="private_key.pem", public_key_file="public_key.pem"):
        with open(private_key_file, "rb") as f:
            self.private_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend()
            )
        with open(public_key_file, "rb") as f:
            self.public_key = serialization.load_pem_public_key(
                f.read(),
                backend=default_backend()
            )

    def encrypt(self, message):
        # Encrypt the message using the public key
        encrypted = self.public_key.encrypt(
            message.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return encrypted

    def decrypt(self, encrypted):
        decrypted = self.private_key.decrypt(
            encrypted,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted.decode()

if __name__ == "__main__":
    crypto = Cryptography()
    crypto.generate_keys()

    message = "Hello, this is a secret message!"
    encrypted_message = crypto.encrypt(message)
    print("Encrypted message:", encrypted_message)

    decrypted_message = crypto.decrypt(encrypted_message)
    print("Decrypted message:", decrypted_message)
