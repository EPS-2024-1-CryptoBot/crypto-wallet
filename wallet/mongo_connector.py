from pymongo import MongoClient # pragma: no cover
from log import get_logger # pragma: no cover


class MongoConnector: # pragma: no cover

    def __init__(self, connection_string="mongodb://mongo:27017/"):
        self.__connection_string = connection_string
        self.__logger = get_logger(self.__class__.__name__)
        self.connect()

    def switch(self, db_name, collection_name):
        self.attach_db(db_name)
        self.attach_collection(collection_name)

    def attach_db(self, db_name):
        self.db = self.client[db_name]
        return self.db

    def attach_collection(self, collection_name):
        self.collection = self.db[collection_name]
        return self.collection

    def connect(self):
        self.__logger.debug(f"ATTEMPTING TO CONNECT TO MONGODB")
        self.client = MongoClient(self.__connection_string)
        self.__logger.info(f"SUCCESSFULLY CONNECTED TO MONGODB")

    def insert_data(self, db, collection, document):
        self.switch(db, collection)
        if collection == 'blockchain':
            document['_id'] = document['user']
        try:
            self.collection.insert_one(document)
            self.__logger.info(
                f"SUCCESSFULLY INSERTED DOCUMENT INTO MONGODB IN COLLECTION {collection}"
            )
        except Exception as e:
            self.__logger.error(
                f"FAILED TO INSERT DOCUMENT INTO MONGODB IN COLLECTION {collection}"
            )
            self.__logger.error(f"ERROR: {e}")

    def delete_data(self, db, collection, _filter):
        self.switch(db, collection)
        self.collection.delete_many(_filter)
        self.__logger.info(
            f"SUCCESSFULLY DELETED DOCUMENT FROM MONGODB IN COLLECTION {collection}"
        )

    def retrieve_data(self, db, collection, _filter={}):
        self.switch(db, collection)
        response = list(self.collection.find(_filter, projection={"_id": False}))
        return response

    def update_data_with_lock(self, db, collection, _filter, update_value):
        self.switch(db, collection)
        if collection == 'blockchain':
            update_value['_id'] = update_value['user']
        _filter["locked"] = {"$exists": False}
        self.collection.update_one(_filter, {"$set": {"locked": True}})
        _filter.pop("locked", None)
        self.collection.replace_one(_filter, update_value)
        self.collection.update_one(_filter, {"$unset": {"locked": ""}})
        self.__logger.info(
            f"SUCCESSFULLY UPDATED DOCUMENT IN MONGODB IN COLLECTION {collection}"
        )


if __name__ == "__main__": # pragma: no cover
    import json
    mongo = MongoConnector("mongodb://mongo:27017/")
    dados = mongo.retrieve_data("cbu_crypto", "blockchain")
    with open("eblockchain.json", "w") as f:
        f.write(json.dumps(dados, indent=4))

    # mongo.insert_data("wallet", "users", {"name": "John", "age": 25})
    # print(list(mongo.retrieve_data("wallet", "users")))

    # print(mongo.retrieve_data("cbu_crypto", "transactions"))
