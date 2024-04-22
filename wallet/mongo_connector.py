from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv('../dev.env')

class MongoConnector():
	def __init__(self, connection_string='mongodb://wallet:pass@mongo:27017/'):

		self.connection_string = connection_string
		self.connect()

		self.db = self.client['users']
		self.collection = self.db['user_events']

	def connect(self):
		print(f"ATTEMPTING TO CONNECT TO MONGODB AT {self.connection_string}")
		self.client = MongoClient(self.connection_string)
		print(f"SUCCESSFULLY CONNECTED TO MONGODB AT {self.connection_string}")

	def insert_data(self, document):
		# print(document['date'])
		# existing_docs = self.retrieve_data(_filter={'date': document['date']})
		# print(existing_docs)
		self.collection.insert_one(document)
		print(f"SUCCESSFULLY INSERTED DOCUMENT INTO MONGODB IN COLLECTION {self.collection}")

	def retrieve_data(self, _filter={}):
		return self.collection.find(_filter)