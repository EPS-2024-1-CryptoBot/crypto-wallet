from pymongo import MongoClient

class MongoConnector():
	def __init__(self, connection_string='mongodb://mongo:27017/'):

		self.connection_string = connection_string
		self.connect()

		self.db = self.client['users']
		self.collection = self.db['user_events']

	def connect(self):
		print(f"ATTEMPTING TO CONNECT TO MONGODB")
		self.client = MongoClient(self.connection_string)
		print(f"SUCCESSFULLY CONNECTED TO MONGODB")

	def insert_data(self, document):
		self.collection.insert_one(document)
		print(f"SUCCESSFULLY INSERTED DOCUMENT INTO MONGODB IN COLLECTION {self.collection}")

	def retrieve_data(self, _filter={}):
		return self.collection.find(_filter)