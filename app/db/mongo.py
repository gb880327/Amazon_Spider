#!python3
from pymongo import MongoClient


class MongoDB(object):
    db = None

    def __init__(self, host, port, db_name):
        client = MongoClient(host=host, port=port)
        self.db = client[db_name]

    def get_collection(self,collection):
        return self.db[collection]

