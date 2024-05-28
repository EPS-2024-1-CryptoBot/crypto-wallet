import datetime
import hashlib
import json
import os

from encryption import Cryptography
from postgres_conn import PostgresConnector

mongo_paths = {
    "blockchain": ["cbu_crypto", "blockchain"],
    "transactions": ["cbu_crypto", "transactions"],
}


class Blockchain:
    def __init__(self, mongo_conn, user):
        self.mongo_conn = mongo_conn
        self.user = user
        self.encryption = Cryptography()
        self.psql = PostgresConnector()
        self.psql.establish_connection()

        self.retrieve_user_keys()
        self.retrieve_blockchain()
        self.retrieve_transactions()
        self.retrieve_users_in_chain()

        if self.chain == []:
            self.encryption.generate_keys()
            self.create_block(proof=1, previous_hash="0")  # Genesis block

    def retrieve_user_keys(self):
        user_keys = self.psql.execute_query(
            f"SELECT public_key, private_key FROM \"user\" WHERE firebase_uid = '{self.user}'"
        )
        if user_keys != []:
            __public_key, private_encrypted_key = user_keys.pop()
            __private_key = self.encryption.retrieve_pvk(
                pvk_chunks=private_encrypted_key
            )
            self.encryption.load_keys(
                public_key=__public_key, private_key=__private_key
            )

    def retrieve_users_in_chain(self):
        chains = self.mongo_conn.retrieve_data(*mongo_paths["blockchain"], {})
        self.users = [
            user_chain.get("user", [])
            for user_chain in chains
            if user_chain.get("user", []) != self.user or True  # REMOVERRRRR
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

        verified_transactions = []
        for transaction in self.transactions:
            transaction_data = transaction["transaction_data"]
            transaction_hex = self.hash(
                block=json.dumps(
                    obj=transaction["transaction"],
                    sort_keys=True,
                )
            )
            if self.encryption.verify_signature(
                message=transaction_hex,
                signature=transaction_data["signature"],
                public_key=transaction_data["public_key"],
            ):
                verified_transactions.append(transaction)
            else:
                print("Invalid transaction detected and ignored.")

        block = {
            "index": len(self.chain) + 1,
            "timestamp": str(datetime.datetime.now()),
            "proof": proof,
            "previous_hash": previous_hash,
            "transactions": verified_transactions,
        }
        self.chain.append(block)
        self.retrieve_users_in_chain()

        response = {
            "user": self.user,
            "chain": self.chain,
        }
        if previous_hash == "0":  # Genesis block
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
            if hash_operation.startswith("0000"):
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
            if not hash_operation.startswith("0000"):
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
        transaction_data["signature"] = self.encryption.sign(
            message=transaction_hex, private_key=self.encryption.keys.get("private_key")
        )
        transaction_data["public_key"] = self.encryption.keys.get("public_key")

        previous_block = self.get_previous_block()
        self.mongo_conn.insert_data(
            *mongo_paths["transactions"],
            {"transaction": transaction, "transaction_data": transaction_data},
        )
        self.retrieve_transactions()

        return previous_block["index"] + 1

    def get_balance(self, user):
        self.retrieve_blockchain()
        balance = 0
        for block in self.chain:
            for transaction in block.get("transactions"):
                data = transaction.get("transaction")
                if user == data.get("sender"):
                    balance -= data.get("amount")
                if user == data.get("receiver"):
                    balance += data.get("amount")
        return balance

    def sync_chain(self):
        self.retrieve_users_in_chain()
        for user in self.users:
            if user != self.user:
                user_chain = self.mongo_conn.retrieve_data(
                    *mongo_paths["blockchain"], {"user": user}
                )
                user_chain = user_chain.pop().get("chain", [])
                metrics = self.get_chain_metrics(user_chain)
                if metrics["length"] > len(self.chain):
                    # print("\nSincronizando blockchain...", user, end='')
                    self.chain = metrics["blocks"]
                    response = {
                        "user": self.user,
                        "chain": self.chain,
                    }
                    self.mongo_conn.update_data_with_lock(
                        *mongo_paths["blockchain"], {"user": self.user}, response
                    )

    def get_valid_blocks(self, chain):
        valid_blocks = []
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block["previous_hash"] == self.hash(previous_block):
                valid_blocks.append(block)
            previous_block = block
            block_index += 1
        return valid_blocks

    def get_chain_metrics(self, chain):
        valid_blocks = self.get_valid_blocks(chain)
        valid_chain_metrics = {
            "length": len(valid_blocks),
            "blocks": valid_blocks,
        }

        return valid_chain_metrics
    
    def get_transactions(self, user):
        self.retrieve_blockchain()
        print(user, self.chain)

        user_transactions = []
        for block in self.chain:
            print(1)
            for transaction in block.get("transactions"):
                print(transaction)
                data = transaction.get("transaction")
                if user == data.get("sender") or user == data.get("receiver"):
                    user_transactions.append(data)

        return user_transactions
