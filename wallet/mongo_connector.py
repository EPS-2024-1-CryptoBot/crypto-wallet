from pymongo import MongoClient
from log import get_logger


class MongoConnector:

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
        self.collection.insert_one(document)
        self.__logger.info(
            f"SUCCESSFULLY INSERTED DOCUMENT INTO MONGODB IN COLLECTION {self.collection}"
        )

    def retrieve_data(self, db, collection, _filter={}):
        self.switch(db, collection)
        return list(self.collection.find(_filter))

    def update_data_with_lock(self, db, collection, _filter, update_value):
        self.switch(db, collection)
        _filter["locked"] = {"$exists": False}
        self.collection.update_one(_filter, {"$set": {"locked": True}})
        _filter.pop("locked", None)
        self.collection.replace_one(_filter, update_value)
        self.collection.update_one(_filter, {"$unset": {"locked": ""}})
        self.__logger.info(
            f"SUCCESSFULLY UPDATED DOCUMENT IN MONGODB IN COLLECTION {self.collection}"
        )


if __name__ == "__main__":
    mongo = MongoConnector()

    mongo.insert_data("wallet", "users", {"name": "John", "age": 25})
    print(list(mongo.retrieve_data("wallet", "users")))
