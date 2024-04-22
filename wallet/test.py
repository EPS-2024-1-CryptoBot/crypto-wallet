from mongo_connector import MongoConnector

db = MongoConnector("mongodb://localhost:27017/teste")
db.insert_data({"name": "John Doe", "age": 25})