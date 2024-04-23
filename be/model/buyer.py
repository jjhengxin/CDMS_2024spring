import sqlite3 as sqlite
import uuid
import json
import logging
from be.model import db_conn
from be.model import error
from pymongo.errors import PyMongoError


class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(
        self, user_id: str, store_id: str, id_and_count: list[tuple[str, int]]
    ) -> (int, str, str):
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            for book_id, count in id_and_count:
                # cursor = self.conn.execute(
                #     "SELECT book_id, stock_level, book_info FROM store "
                #     "WHERE store_id = ? AND book_id = ?;",
                #     (store_id, book_id),
                # )
                result = self.conn['bookstore']['store'].find_one(
                    {"store_id": store_id, "book_id": book_id},
                    {"book_id": 1, "stock_level": 1, "book_info": 1}
                )
                if not result:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                # stock_level = result["stock_level"]
                # book_info = result["book_info"]
                # book_info_json = (book_info)
                # price = book_info_json.get("price")

                stock_level = result["stock_level"]
                book_info = json.loads(result["book_info"])
                price = book_info.get("price")

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

                # cursor = self.conn.execute(
                #     "UPDATE store set stock_level = stock_level - ? "
                #     "WHERE store_id = ? and book_id = ? and stock_level >= ?; ",
                #     (count, store_id, book_id, count),
                # )
                query = {
                    "$and": [
                        {"store_id": store_id},
                        {"book_id": book_id},
                        {"stock_level": {"$gte": count}}
                    ]
                }
                new_values = {"$set": {"stock_level": stock_level-1}}
                result = self.conn['bookstore']['store'].update_one(query, new_values)
                if result.modified_count == 0:
                    return error.error_stock_level_low(book_id) + (order_id,)
                # if cursor.rowcount == 0:
                #     return error.error_stock_level_low(book_id) + (order_id,)

                new_order_detail_info = {
                    "order_id": uid,
                    "book_id": book_id,
                    "count": count,
                    "price": price
                }
                self.conn['bookstore']['new_order_detail'].insert_one(new_order_detail_info)
                # self.conn.execute(
                #     "INSERT INTO new_order_detail(order_id, book_id, count, price) "
                #     "VALUES(?, ?, ?, ?);",
                #     (uid, book_id, count, price),
                # )
            new_order_info = {
                "order_id": uid,
                "store_id": store_id,
                "user_id": user_id
            }
            self.conn['bookstore']['new_order'].insert_one(new_order_info)
            # self.conn.execute(
            #     "INSERT INTO new_order(order_id, store_id, user_id) "
            #     "VALUES(?, ?, ?);",
            #     (uid, store_id, user_id),
            # )
            # self.conn.commit()
            order_id = uid
        except PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        # except BaseException as e:
        #     logging.info("530, {}".format(str(e)))
        #     return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> tuple[int, str]:
        conn = self.conn
        try:
            # cursor = conn.execute(
            #     "SELECT order_id, user_id, store_id FROM new_order WHERE order_id = ?",
            #     (order_id,),
            # )
            # row = cursor.fetchone()
            # if row is None:
            #     return error.error_invalid_order_id(order_id)

            result = conn['bookstore']['new_order'].find_one({"order_id": order_id}, {"order_id": 1, "user_id": 1, "store_id": 1})
            if result is None:
                return error.error_invalid_order_id(order_id)

            order_id = result["order_id"]
            buyer_id = result["user_id"]
            store_id = result["store_id"]

            if buyer_id != user_id:
                return error.error_authorization_fail()

            # cursor = conn.execute(
            #     "SELECT balance, password FROM user WHERE user_id = ?;", (buyer_id,)
            # )
            # row = cursor.fetchone()
            # if row is None:
            #     return error.error_non_exist_user_id(buyer_id)
            
            result = conn['bookstore']['user'].find_one({"user_id": buyer_id}, {"balance": 1, "password": 1})
            if result is None:
                return error.error_invalid_order_id(order_id)
            balance = result['balance']
            if password != result['password']:
                return error.error_authorization_fail()

            # 查询卖家信息
            seller_info = conn['bookstore']['user_store'].find_one({"store_id": store_id})
            if seller_info is None:
                return error.error_non_exist_store_id(store_id)
            seller_id = seller_info['user_id']

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            # 查询订单详情
            order_details_cursor = conn['bookstore']['new_order_detail'].find({"order_id": order_id})
            total_price = 0
            for detail in order_details_cursor:
                count = detail['count']
                price = detail['price']
                total_price += price * count

            # cursor = conn.execute(
            #     "SELECT store_id, user_id FROM user_store WHERE store_id = ?;",
            #     (store_id,),
            # )
            # row = cursor.fetchone()
            # if row is None:
            #     return error.error_non_exist_store_id(store_id)

            # seller_id = row[1]

            # if not self.user_id_exist(seller_id):
            #     return error.error_non_exist_user_id(seller_id)

            # cursor = conn.execute(
            #     "SELECT book_id, count, price FROM new_order_detail WHERE order_id = ?;",
            #     (order_id,),
            # )
            # total_price = 0
            # for row in cursor:
            #     count = row[1]
            #     price = row[2]
            #     total_price = total_price + price * count

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            # 更新买家余额
            buyer_update_result = conn['bookstore']['user'].update_one(
                {"user_id": buyer_id, "balance": {"$gte": total_price}},
                {"$inc": {"balance": -total_price}}
            )
            if buyer_update_result.modified_count == 0:
                return error.error_not_sufficient_funds(order_id)

            # 更新卖家余额
            seller_update_result = conn['bookstore']['user'].update_one(
                {"user_id": seller_id},
                {"$inc": {"balance": total_price}}
            )
            if seller_update_result.modified_count == 0:
                return error.error_non_exist_user_id(seller_id)

            # 删除订单
            delete_order_result = conn['bookstore']['new_order'].delete_one({"order_id": order_id})
            if delete_order_result.deleted_count == 0:
                return error.error_invalid_order_id(order_id)

            # 删除订单详情
            delete_order_detail_result = conn['bookstore']['new_order_detail'].delete_many({"order_id": order_id})
            if delete_order_detail_result.deleted_count == 0:
                return error.error_invalid_order_id(order_id)

            # cursor = conn.execute(
            #     "UPDATE user set balance = balance - ?"
            #     "WHERE user_id = ? AND balance >= ?",
            #     (total_price, buyer_id, total_price),
            # )
            # if cursor.rowcount == 0:
            #     return error.error_not_sufficient_funds(order_id)

            # cursor = conn.execute(
            #     "UPDATE user set balance = balance + ?" "WHERE user_id = ?",
            #     (total_price, seller_id),
            # )

            # if cursor.rowcount == 0:
            #     return error.error_non_exist_user_id(seller_id)

            # cursor = conn.execute(
            #     "DELETE FROM new_order WHERE order_id = ?", (order_id,)
            # )
            # if cursor.rowcount == 0:
            #     return error.error_invalid_order_id(order_id)

            # cursor = conn.execute(
            #     "DELETE FROM new_order_detail where order_id = ?", (order_id,)
            # )
            # if cursor.rowcount == 0:
            #     return error.error_invalid_order_id(order_id)

            # conn.commit()

        except PyMongoError as e:
            return 528, "{}".format(str(e))

        # except BaseException as e:
        #     return 530, "{}".format(str(e))

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> tuple[int, str]:
        conn = self.conn
        try:
            # 查询用户密码
            user_password_result = conn['bookstore']['user'].find_one({"user_id": user_id}, {"password": 1})
            if user_password_result is None:
                return error.error_authorization_fail()

            if user_password_result['password'] != password:
                return error.error_authorization_fail()

            # 更新用户余额
            update_balance_result = conn['bookstore']['user'].update_one(
                {"user_id": user_id},
                {"$inc": {"balance": add_value}}
            )
            if update_balance_result.modified_count == 0:
                return error.error_non_exist_user_id(user_id)

            # cursor = self.conn.execute(
            #     "SELECT password  from user where user_id=?", (user_id,)
            # )
            # row = cursor.fetchone()
            # if row is None:
            #     return error.error_authorization_fail()

            # if row[0] != password:
            #     return error.error_authorization_fail()

            # cursor = self.conn.execute(
            #     "UPDATE user SET balance = balance + ? WHERE user_id = ?",
            #     (add_value, user_id),
            # )
            # if cursor.rowcount == 0:
            #     return error.error_non_exist_user_id(user_id)

            # self.conn.commit()
        except PyMongoError as e:
            return 528, "{}".format(str(e))
        # except BaseException as e:
        #     return 530, "{}".format(str(e))

        return 200, "ok"
