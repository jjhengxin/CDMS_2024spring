import pymongo
import uuid
import json
import logging
from be.model import error
from be.model import db_conn
import base64

class Book(db_conn.DBConn):
    # ... 你现有的代码 ...
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def search_in_store_simple(self,store_id, query_str, page=1,per_page=10):
        try:
            store_collection = self.db["store"]
            book_collection = self.db["book"]

            query = {'store_id': store_id}
            res = store_collection.find(query, {"book_id": 1, "_id": 0})
            ids = []
            for i in res:
                ids += list(i.values())

            query = {
                "$and": [
                            {"id": {"$in": ids}},
                            {"$text": {"$search": query_str}}
                        ]
            }

            # 计算分页参数
            skip = (page - 1) * per_page
            limit = per_page

            # 使用 find 方法执行查询，并限制结果数量
            result = book_collection.find(query, {'_id': 0}).skip(skip).limit(limit)
            tmp = []
            for i in result:
                pics=[]
                for picture in i['pictures']:
                    encode_str = base64.b64encode(picture).decode("utf-8")
                    pics.append(encode_str)
                i['pictures'] = pics
                # if len(i['pictures']) != 0:
                #     picture = i['picture']
                #     encode_str = base64.b64encode(picture).decode("utf-8")
                #     i['picture'] = encode_str
                tmp.append(i)
            result = tmp

        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, result

    def search_all_simple(self, query_str, page=1,per_page=10):
        try:
            book_collection = self.db["book"]

            query = {"$text": {"$search": query_str}}


            # 计算分页参数
            skip = (page - 1) * per_page
            limit = per_page

            # 使用 find 方法执行查询，并限制结果数量
            result = book_collection.find(query, {'_id': 0}).skip(skip).limit(limit)
            tmp = []
            for i in result:
                pics=[]
                for picture in i['pictures']:
                    encode_str = base64.b64encode(picture).decode("utf-8")
                    pics.append(encode_str)
                i['pictures'] = pics
                # if len(i['pictures']) != 0:
                #     picture = i['picture']
                #     encode_str = base64.b64encode(picture).decode("utf-8")
                #     i['picture'] = encode_str
                tmp.append(i)
            result = tmp

        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, result


    def search_in_store(self, store_id, title, author, publisher, isbn, content, tags, book_intro, page=1, per_page=10):
        try:
            store_collection = self.db["store"]
            book_collection = self.db["book"]

            query = {'store_id': store_id}
            res = store_collection.find(query, {"book_id": 1, "_id": 0})
            ids = []
            for i in res:
                ids += list(i.values())

            qs_dict = {
                'title': title,
                'author': author,
                'publisher': publisher,
                'isbn': isbn,
                'content': content,
                'tags': tags,
                'book_intro': book_intro
            }
            qs_dict1 = {}
            for key, value in qs_dict.items():
                if len(value) != 0:
                    qs_dict1[key] = value
            qs_dict = qs_dict1

            qs_list = [{key: {"$regex": value}} for key, value in qs_dict.items()]
            query = {
                "$and": [
                            {"id": {"$in": ids}},
                        ] + qs_list
            }

            # 计算分页参数
            skip = (page - 1) * per_page
            limit = per_page
            print(3)
            # 使用 find 方法执行查询，并限制结果数量
            result = book_collection.find(query, {'_id': 0}).skip(skip).limit(limit)
            tmp = []
            for i in result:
                pics=[]
                for picture in i['pictures']:
                    encode_str = base64.b64encode(picture).decode("utf-8")
                    pics.append(encode_str)
                i['pictures'] = pics
                # if len(i['pictures']) != 0:
                #     picture = i['picture']
                #     encode_str = base64.b64encode(picture).decode("utf-8")
                #     i['picture'] = encode_str
                tmp.append(i)
            result = tmp
            print(4)

        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, result

    def search_all(self,title,author,publisher,isbn,content,tags,book_intro,page=1,per_page=10):
        try:
            book_collection = self.db["book"]

            qs_dict={
                'title': title,
                'author': author,
                'publisher': publisher,
                'isbn': isbn,
                'content': content,
                'tags': tags,
                'book_intro': book_intro
            }
            qs_dict1={}
            for key,value in qs_dict.items():
                if len(value)!=0:
                    qs_dict1[key]=value
            qs_dict=qs_dict1
            qs_list=[{key:{"$regex": value}} for key,value in qs_dict.items()]
            if len(qs_list)==0:
                query={}
            else:
                query = {
                    "$and": qs_list
                }
            # 计算分页参数
            skip = (page - 1) * per_page
            limit = per_page

            # 使用 find 方法执行查询，并限制结果数量
            result = book_collection.find(query, {'_id': 0}).skip(skip).limit(limit)
            tmp = []
            for i in result:
                pics=[]
                for picture in i['pictures']:
                    encode_str = base64.b64encode(picture).decode("utf-8")
                    pics.append(encode_str)
                i['pictures'] = pics
                # if len(i['pictures']) != 0:
                #     picture = i['picture']
                #     encode_str = base64.b64encode(picture).decode("utf-8")
                #     i['picture'] = encode_str
                tmp.append(i)
            result = tmp

        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))


        return 200,result