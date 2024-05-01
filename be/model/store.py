import logging
import os
import pymongo
from pymongo.errors import PyMongoError
import threading

import pymongo.errors


class Store:
    database: str

    def __init__(self, db_path):
        self.database = os.path.join(db_path, "be.db")
        self.init_tables()

    def init_tables(self):
        try:
            conn = self.get_db_conn()
            db = conn.get_database("bookstore")  

            user_collection = db.get_collection("user") 

            user_collection.create_index("user_id",unique=True)
            user_store_collection = db.get_collection("user_store")
            user_store_collection.create_index([("user_id", pymongo.ASCENDING), ("store_id", pymongo.ASCENDING)])

            store_collection = db.get_collection("store")
            store_collection.create_index([("store_id", pymongo.ASCENDING), ("book_id", pymongo.ASCENDING)])
            new_order_collection = db.get_collection("new_order")
            new_order_collection.create_index("order_id", unique=True)
            new_order_detail_collection = db.get_collection("new_order_detail")
            new_order_detail_collection.create_index([("order_id", pymongo.ASCENDING), ("book_id", pymongo.ASCENDING)])

        except PyMongoError as e:
            logging.error(e)
        
    def get_db_conn(self) -> pymongo.MongoClient:
        client = pymongo.MongoClient("mongodb://localhost:27017/") 
        return client


database_instance: Store = None
init_completed_event = threading.Event()

def init_database(db_path):
    global database_instance
    database_instance = Store(db_path)

def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()




