import logging
import os
# import sqlite3 as sqlite
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
            db = conn.get_database("bookstore")  # 替换为你要使用的数据库名称

            user_collection = db.get_collection("user")  # 替换为你要创建的集合名称

            # 如果需要，可以添加索引，这里举个例子
            user_collection.create_index("user_id")
            # conn.execute(
            #     "CREATE TABLE IF NOT EXISTS user ("
            #     "user_id TEXT PRIMARY KEY, password TEXT NOT NULL, "
            #     "balance INTEGER NOT NULL, token TEXT, terminal TEXT);"
            # )
            user_store_collection = db.get_collection("user_store")
            user_store_collection.create_index([("user_id", pymongo.ASCENDING), ("store_id", pymongo.ASCENDING)])
            # conn.execute(
            #     "CREATE TABLE IF NOT EXISTS user_store("
            #     "user_id TEXT, store_id, PRIMARY KEY(user_id, store_id));"
            # )

            store_collection = db.get_collection("store")
            store_collection.create_index([("store_id", pymongo.ASCENDING), ("book_id", pymongo.ASCENDING)])
            # conn.execute(
            #     "CREATE TABLE IF NOT EXISTS store( "
            #     "store_id TEXT, book_id TEXT, book_info TEXT, stock_level INTEGER,"
            #     " PRIMARY KEY(store_id, book_id))"
            # )
            new_order_collection = db.get_collection("new_order")
            new_order_collection.create_index("order_id", unique=True)
            # conn.execute(
            #     "CREATE TABLE IF NOT EXISTS new_order( "
            #     "order_id TEXT PRIMARY KEY, user_id TEXT, store_id TEXT)"
            # )
            new_order_detail_collection = db.get_collection("new_order_detail")
            new_order_detail_collection.create_index([("order_id", pymongo.ASCENDING), ("book_id", pymongo.ASCENDING)])
            # conn.execute(
            #     "CREATE TABLE IF NOT EXISTS new_order_detail( "
            #     "order_id TEXT, book_id TEXT, count INTEGER, price INTEGER,  "
            #     "PRIMARY KEY(order_id, book_id))"
            # )

        except PyMongoError as e:
            logging.error(e)
            # conn.rollback()

    # def get_db_conn(self) -> sqlite.Connection:
    #     return sqlite.connect(self.database)
    def get_db_conn(self) -> pymongo.MongoClient:
        client = pymongo.MongoClient("mongodb://localhost:27017/")  # 替换为实际的 MongoDB 连接地址
        return client


database_instance: Store = None
# global variable for database sync
init_completed_event = threading.Event()


def init_database(db_path):
    global database_instance
    database_instance = Store(db_path)


def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()
