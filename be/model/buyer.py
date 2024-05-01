import uuid
import json
from datetime import datetime

import pymongo

from be.model import db_conn
from be.model import error
from pymongo.errors import PyMongoError


class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(
            self, user_id: str, store_id: str, id_and_count: [(str, int)]
    ) -> (int, str, str):
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            for book_id, count in id_and_count:
                store_collection = self.db["store"]            
                store_data = store_collection.find_one({"store_id": store_id, "book_id": book_id})  
                if store_data is None:     
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level = store_data["stock_level"]
                price = store_data["price"]

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)
                
                
                query = {
                    "$and": [
                        {"store_id": store_id},
                        {"book_id": book_id},
                        {"stock_level": {"$gte": count}}
                    ]
                }
                new_values = {"$set": {"stock_level": stock_level-1}}
                result = self.conn['bookstore']['store'].update_one(query, new_values)                           
                
                new_order_detail_info = {
                    "order_id": uid,
                    "book_id": book_id,
                    "count": count,
                    "price": price
                }
                self.conn['bookstore']['new_order_detail'].insert_one(new_order_detail_info)
                            
                
            new_order_info = {
                "order_id": uid,
                "store_id": store_id,
                "user_id": user_id,
                "status": "unpaid",
                "created_at": datetime.now().isoformat()
            }
            self.conn['bookstore']['new_order'].insert_one(new_order_info)
            order_id = uid
            
        except PyMongoError as e:
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:
            order_data = self.conn['bookstore']['new_order'].find_one({"order_id": order_id})
            
            buyer_id = order_data["user_id"]
            store_id = order_data["store_id"]
            status_id = order_data["status"]
            
            user_collection = self.db["user"]         
            user_data = user_collection.find_one({"user_id": user_id})

            if password != user_data["password"]:
                return error.error_authorization_fail()
            balance = user_data["balance"]            
            
            seller_info = self.conn['bookstore']['user_store'].find_one({"store_id": store_id})
            seller_id = seller_info['user_id']     
            
            order_details_cursor = self.conn['bookstore']['new_order_detail'].find({"order_id": order_id})
            total_price = 0
            for detail in order_details_cursor:
                count = detail['count']
                price = detail['price']
                total_price += price * count

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            buyer_update_result = self.conn['bookstore']['user'].update_one(
                {"user_id": buyer_id, "balance": {"$gte": total_price}},
                {"$inc": {"balance": -total_price}}
            )

            self.conn['bookstore']['new_order'].update_one({"order_id": order_id},{"$set": {"status": "paid"}})

        except PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def receive_order(self, user_id: str, order_id: str) -> (int, str):
        try:
            new_orders = self.conn['bookstore']['new_order']
            new_order_info = new_orders.find_one({"order_id": order_id})

            if new_order_info["status"] != "shipped":                         
                return error.error_status_fail(order_id)

            new_orders.update_one({"order_id": order_id},{"$set": {"status": "received"}})
            
        except PyMongoError as e:           
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"
    

    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            user_password_result = self.conn['bookstore']['user'].find_one({"user_id": user_id}, {"password": 1})
            if user_password_result is None:
                return error.error_authorization_fail()

            if user_password_result['password'] != password:
                return error.error_authorization_fail()
                  
            update_balance_result = self.conn['bookstore']['user'].update_one(
                {"user_id": user_id},
                {"$inc": {"balance": add_value}}
            )
            
        except PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def get_buyer_orders(self, user_id: str) -> (int, str, list):
        try:
        
            new_orders = self.conn['bookstore']['new_order']
            orders = new_orders.find({"user_id": user_id})
            buyer_orders = []
            for order in orders:
                buyer_orders.append({'store_id': order["store_id"],
                                     'order_id': order["order_id"],
                                     'status': order["status"]})
                
        except PyMongoError as e:
            return 528, "{}".format(str(e)), []
        except BaseException as e:
            return 530, "{}".format(str(e)), []
        
        return 200, "ok", buyer_orders

    def cancel_order(self, user_id: str, order_id: str) -> (int, str):
        try:
            if not self.order_id_exist(user_id, order_id):                                  
                return error.error_non_exist_order_id(order_id)
            
            new_orders = self.conn['bookstore']['new_order']
            order_info = new_orders.find_one({"order_id": order_id})

            if order_info["status"] == "paid":
                users = self.conn['bookstore']["user"]
                user_info = users.find_one({"user_id": user_id})
                
                order_details = self.conn['bookstore']["new_order_detail"]
                order_detail = order_details.find({"order_id": order_id})
                
                order_price = 0
                for book_detail in order_detail:
                    count = book_detail["count"]
                    price = book_detail["price"]
                    order_price += price * count

                user_balance = user_info["balance"]
                user_balance += order_price
                users.update_one({"user_id": user_id},{"$set": {"balance": user_balance}})
            new_orders.update_one({"order_id": order_id},{"$set": {"status": "cancelled"}})
            
        except PyMongoError as e:           
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

