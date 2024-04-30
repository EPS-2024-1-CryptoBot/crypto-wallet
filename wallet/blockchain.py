import datetime
import hashlib
import json

import requests
from encryption import Cryptography

mongo_paths = {
    "blockchain": ["cbu_crypto", "blockchain"],
    "transactions": ["cbu_crypto", "transactions"],
}


class Blockchain:
    def __init__(self, mongo_conn, user):
        self.mongo_conn = mongo_conn
        self.user = user
        self.encryption = Cryptography()

        self.retrieve_user_keys()
        self.retrieve_blockchain()
        self.retrieve_transactions()
        self.retrieve_users_in_chain()

        if self.chain == []:
            self.encryption.generate_keys()
            self.create_block(proof=1, previous_hash="0")  # Genesis block


    def retrieve_user_keys(self):
        user_keys = self.mongo_conn.retrieve_data(
            *mongo_paths["blockchain"], {"user": self.user}
        )
        if user_keys != []:
            user_keys = user_keys.pop().get("keys", [])
            self.encryption.load_keys(user_keys.get("public_key"), user_keys.get("private_key"))

    def retrieve_users_in_chain(self):
        chains = self.mongo_conn.retrieve_data(*mongo_paths["blockchain"], {})
        self.users = [
            user_chain.get("user", [])
            for user_chain in chains
            if user_chain.get("user", []) != self.user or True # REMOVERRRRR
        ]
        return self.users

    def retrieve_blockchain(self):
        self.mongo_chain = self.mongo_conn.retrieve_data(
            *mongo_paths["blockchain"], {"user": self.user}
        )
        self.chain = (
            [] if not self.mongo_chain else self.mongo_chain.pop().get("chain", [])
        )

    def retrieve_transactions(self):
        self.mongo_transactions = self.mongo_conn.retrieve_data(
            *mongo_paths["transactions"]
        )
        self.transactions = (
            [] if not self.mongo_transactions else self.mongo_transactions
        )

    def create_block(self, proof, previous_hash):
        self.retrieve_transactions()
        block = {
            "index": len(self.chain) + 1,
            "timestamp": str(datetime.datetime.now()),
            "proof": proof,
            "previous_hash": previous_hash,
            "transactions": self.transactions,
        }
        self.chain.append(block)
        self.retrieve_users_in_chain()

        response = {"user": self.user, "chain": self.chain, "keys": self.encryption.keys}
        if previous_hash == "0": # Genesis block
            self.mongo_conn.insert_data(*mongo_paths["blockchain"], response)
        else:
            self.mongo_conn.delete_data(*mongo_paths["transactions"], {})
            self.transactions = self.retrieve_transactions()
            self.mongo_conn.update_data_with_lock(
                *mongo_paths["blockchain"], {"user": self.user}, response
            )
        return response

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(
                str(new_proof**2 - previous_proof**2).encode()
            ).hexdigest()
            if hash_operation[:5] == "00f00":
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self):
        previous_block = self.chain[0]
        block_index = 1
        while block_index < len(self.chain):
            block = self.chain[block_index]
            if block["previous_hash"] != self.hash(previous_block):
                return False
            
            previous_proof = previous_block["proof"]
            proof = block["proof"]
            hash_operation = hashlib.sha256(
                str(proof**2 - previous_proof**2).encode()
            ).hexdigest()
            if hash_operation[:5] != "00f00":
                return False
            
            for transaction in block["transactions"]:
                transaction_hex = self.hash(
                    block=json.dumps(
                        obj=transaction["transaction"],
                        sort_keys=True,
                    )
                )
                if not self.encryption.verify_signature(
                    message=transaction_hex,
                    signature=transaction["transaction_data"]["signature"],
                    public_key=transaction["transaction_data"]["public_key"],
                ):
                    return False
            
            previous_block = block
            block_index += 1
        return True

    def add_transaction(self, amount, sender=None, receiver=None):
        sender = sender or self.user
        receiver = receiver or self.user

        transaction = {"sender": sender, "receiver": receiver, "amount": amount}
        transaction_hex = self.hash(
            block=json.dumps(
                obj=transaction,
                sort_keys=True,
            )
        )

        transaction_data = {}
        transaction_data["signature"] = self.encryption.sign(message=transaction_hex, private_key=self.encryption.keys.get("private_key"))
        transaction_data["public_key"] = self.encryption.keys.get("public_key")
        
        previous_block = self.get_previous_block()
        self.mongo_conn.insert_data(*mongo_paths["transactions"], {"transaction": transaction, "transaction_data": transaction_data})
        self.retrieve_transactions()

        return previous_block["index"] + 1

    def get_balance(self, user):
        self.retrieve_blockchain()
        balance = 0
        print(user)
        for block in self.chain:
            for transaction in block.get("transactions"):
                data = transaction.get("transaction")
                if user == data.get("sender"):
                    balance -= data.get("amount")
                if user == data.get("receiver"):
                    balance += data.get("amount")
        print(balance)
        return balance