import json
from datetime import datetime
import pymongo
from be.model import error
from be.model import db_conn
from base64 import b64decode
from bson.binary import Binary
from pymongo.errors import PyMongoError

class Seller(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def add_book(
            self,
            user_id: str,
            store_id: str,
            book_id: str,
            book_json_str: str,
            stock_level: int,
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)
            
            store_collection = self.conn['bookstore']['store']

            store_data = {
                "store_id": store_id,
                "book_id": book_id,
                "price" : json.loads(book_json_str)['price'],
                "stock_level": stock_level
            }


            store_collection.insert_one(store_data)
        
        except PyMongoError as e:        
            return 528, "{}".format(str(e))
        except BaseException as e:
            # print(e)
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_stock_level(
            self, user_id: str, store_id: str, book_id: str, add_stock_level: int
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)

            store_collection = self.conn['bookstore']['store']
            filter_query = {"store_id": store_id, "book_id": book_id}
            update_query = {"$inc": {"stock_level": add_stock_level}}

            store_collection.update_one(filter_query, update_query)
            
        except PyMongoError as e:     
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):   
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)
            
            user_store_collection = self.conn['bookstore']['user_store']
            user_store_collection.insert_one({"store_id": store_id, "user_id": user_id})
        
        except PyMongoError as e:           
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def ship_order(self, store_id: str, order_id: str) -> (int, str):
        try:
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)

            new_orders = self.conn['bookstore']['new_order']
            new_order_info = new_orders.find_one({"order_id": order_id})
            
            if new_order_info["status"] != "paid":                     
                return error.error_status_fail(order_id)

            new_orders.update_one({"order_id": order_id},{"$set": {"status": "shipped"}})
            
        except PyMongoError as e:           
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

