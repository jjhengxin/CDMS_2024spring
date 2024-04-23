import jwt
import time
import logging
# import sqlite3 as sqlite
import pymongo
import pymongo.errors
from pymongo.errors import PyMongoError

from be.model import error
from be.model import db_conn

# encode a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }


def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    return encoded


# decode a JWT to a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }
def jwt_decode(encoded_token, user_id: str) -> str:
    decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
    return decoded


class User(db_conn.DBConn):
    token_lifetime: int = 3600  # 3600 second

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def __check_token(self, user_id, db_token, token) -> bool:
        try:
            if db_token != token:
                return False
            jwt_text = jwt_decode(encoded_token=token, user_id=user_id)
            ts = jwt_text["timestamp"]
            if ts is not None:
                now = time.time()
                if self.token_lifetime > now - ts >= 0:
                    return True
        except jwt.exceptions.InvalidSignatureError as e:
            logging.error(str(e))
            return False

    def register(self, user_id: str, password: str):
        try:
            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            # 插入用户信息到 "user" 集合中
            user_info = {
                "user_id": user_id,
                "password": password,
                "balance": 0,
                "token": token,
                "terminal": terminal
            }
            
            # 本地进行连接（self.conn返回client），然后进入到bookstore数据库，的user集合。这里bookstore数据库存疑！
            self.user_collection.insert_one(user_info)
            # self.conn.execute(
            #     "INSERT into user(user_id, password, balance, token, terminal) "
            #     "VALUES (?, ?, ?, ?, ?);",
            #     (user_id, password, 0, token, terminal),
            # )
            # self.conn.commit()PyMongoError
        except PyMongoError:
            return error.error_exist_user_id(user_id)
        return 200, "ok"

    def check_token(self, user_id: str, token: str) -> tuple[int, str]:
        # 查询用户信息中的 token 字段
        result = self.conn['bookstore']['user'].find_one({"user_id": user_id}, {"token": 1})

        if result is None:
            return error.error_authorization_fail()

        db_token = result.get("token")
        if not db_token or not self.__check_token(user_id, db_token, token):
            return error.error_authorization_fail()
        
        # cursor = self.conn.execute("SELECT token from user where user_id=?", (user_id,))
        # row = cursor.fetchone()
        # if row is None:
        #     return error.error_authorization_fail()
        # db_token = row[0]
        if not self.__check_token(user_id, db_token, token):
            return error.error_authorization_fail()
        return 200, "ok"

    def check_password(self, user_id: str, password: str) -> (int, str):
        result = self.conn['bookstore']['user'].find_one({"user_id": user_id})
        if result is None or result.get("password") != password:
            return error.error_authorization_fail()
        else:
            return 200, "ok"

    def login(self, user_id: str, password: str, terminal: str) -> tuple[int, str, str]:
        token = ""
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message, ""

            token = jwt_encode(user_id, terminal)
            # 定义查询条件
            query = {"user_id": user_id}

            # 定义更新内容
            new_values = {"$set": {"token": token, "terminal": terminal}}
            result =  self.conn['bookstore']['user'].update_one(query, new_values)
            if result.modified_count == 0:
                return error.error_authorization_fail() + ("",)
            # cursor = self.conn.execute(
            #     "UPDATE user set token= ? , terminal = ? where user_id = ?",
            #     (token, terminal, user_id),
            # )
            # if cursor.rowcount == 0:
            #     return error.error_authorization_fail() + ("",)
            
        except PyMongoError as e:
            return 528, "{}".format(str(e)), ""
        # except BaseException as e:
        #     return 530, "{}".format(str(e)), ""
        return 200, "ok", token

    def logout(self, user_id: str, token: str) -> bool:
        try:
            code, message = self.check_token(user_id, token)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            dummy_token = jwt_encode(user_id, terminal)
            # 定义查询条件
            query = {"user_id": user_id}

            # 定义更新内容
            new_values = {"$set": {"token": dummy_token, "terminal": terminal}}
            result =  self.conn['bookstore']['user'].update_one(query, new_values)
            if result.modified_count == 0:
                return error.error_authorization_fail() + ("",)
            
            # cursor = self.conn.execute(
            #     "UPDATE user SET token = ?, terminal = ? WHERE user_id=?",
            #     (dummy_token, terminal, user_id),
            # )
            # if cursor.rowcount == 0:
            #     return error.error_authorization_fail()

            # self.conn.commit()
        except PyMongoError as e:
            return 528, "{}".format(str(e))
        # except BaseException as e:
        #     return 530, "{}".format(str(e))
        return 200, "ok"

    def unregister(self, user_id: str, password: str) -> (int, str):
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message
            
            # 定义查询条件
            query = {"user_id": user_id}

            result =  self.user_collection.delete_one(query)
            if result.deleted_count == 1:
                pass
            else :
                return error.error_authorization_fail() 
            
            # cursor = self.conn.execute("DELETE from user where user_id=?", (user_id,))
            # if cursor.rowcount == 1:
            #     self.conn.commit()
            # else:
            #     return error.error_authorization_fail()
        except PyMongoError as e:
            return 528, "{}".format(str(e))
        # except BaseException as e:
        #     return 530, "{}".format(str(e))
        return 200, "ok"

    def change_password(
        self, user_id: str, old_password: str, new_password: str
    ) -> bool:
        try:
            code, message = self.check_password(user_id, old_password)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)

            # 定义查询条件
            query = {"user_id": user_id}

            # 定义更新内容
            new_values = {"$set": {"password": new_password, "token": token, "terminal": terminal}}
            result =  self.conn['bookstore']['user'].update_one(query, new_values)
            if result.modified_count == 0:
                return error.error_authorization_fail() + ("",)
            # cursor = self.conn.execute(
            #     "UPDATE user set password = ?, token= ? , terminal = ? where user_id = ?",
            #     (new_password, token, terminal, user_id),
            # )
            # if cursor.rowcount == 0:
            #     return error.error_authorization_fail()

            
        except PyMongoError as e:
            return 528, "{}".format(str(e))
        # except BaseException as e:
        #     return 530, "{}".format(str(e))
        return 200, "ok"
