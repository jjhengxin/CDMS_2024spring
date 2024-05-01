import pymongo
import uuid
import json
import logging
from be.model import error
from be.model import db_conn
import base64

class Book(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def search_in_store(self, store_id, title, author, publisher, isbn, content, tags, book_intro, page=1, per_page=10):
        try:
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            
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

            skip = (page - 1) * per_page
            limit = per_page

            cursor = book_collection.find(query, {'_id': 0}).skip(skip).limit(limit)
            result = []
            for doc in cursor:
                book = {}
                book['id'] = doc.get("id")
                book['title'] = doc.get("title")
                book['author'] = doc.get("author")
                book['publisher'] = doc.get("publisher")
                book['original_title'] = doc.get("original_title")
                book['translator'] = doc.get("translator")
                book['pub_year'] = doc.get("pub_year")
                book['pages'] = doc.get("pages")
                book['price'] = doc.get("price")
                book['currency_unit'] = doc.get("currency_unit")
                book['binding'] = doc.get("binding")
                book['isbn'] = doc.get("isbn")
                book['author_intro'] = doc.get("author_intro")
                book['book_intro'] = doc.get("book_intro")
                book['content'] = doc.get("content")
                book['tags'] = doc.get("tags")

                result.append(book)

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

            skip = (page - 1) * per_page
            limit = per_page

            cursor = book_collection.find(query, {'_id': 0}).skip(skip).limit(limit)
            result = []
            for doc in cursor:
                book = {}
                book['id'] = doc.get("id")
                book['title'] = doc.get("title")
                book['author'] = doc.get("author")
                book['publisher'] = doc.get("publisher")
                book['original_title'] = doc.get("original_title")
                book['translator'] = doc.get("translator")
                book['pub_year'] = doc.get("pub_year")
                book['pages'] = doc.get("pages")
                book['price'] = doc.get("price")
                book['currency_unit'] = doc.get("currency_unit")
                book['binding'] = doc.get("binding")
                book['isbn'] = doc.get("isbn")
                book['author_intro'] = doc.get("author_intro")
                book['book_intro'] = doc.get("book_intro")
                book['content'] = doc.get("content")
                book['tags'] = doc.get("tags")

                result.append(book)

        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))


        return 200,result
