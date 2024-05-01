import os
import sqlite3 as sqlite
import random
import simplejson as json
import pymongo
import base64
from fe import conf
from pymongo import MongoClient
from urllib.parse import urljoin
import requests

class Book:
    id: str
    title: str
    author: str
    publisher: str
    original_title: str
    translator: str
    pub_year: str
    pages: int
    price: int
    currency_unit: str
    binding: str
    isbn: str
    author_intro: str
    book_intro: str
    content: str
    tags: str
    pictures: [bytes]

    def __init__(self):
        self.pictures = []


def search_in_store(store_id,title,author,publisher,isbn,content,tags,book_intro,page=1,per_page=10):
    json ={
            'store_id':store_id,
            'title': title,
            'author': author,
            'publisher': publisher,
            'isbn': isbn,
            'content': content,
            'tags': tags,
            'book_intro': book_intro,
            'page': page,
            "per_page": per_page
        }
    url = urljoin(urljoin(conf.URL, "book/"), "search_in_store")
    r = requests.post(url, json=json)
    return r.status_code,r.json()

def search_all(title,author,publisher,isbn,content,tags,book_intro,page=1,per_page=10):
    json ={
            'title': title,
            'author': author,
            'publisher': publisher,
            'isbn': isbn,
            'content': content,
            'tags': tags,
            'book_intro': book_intro,
            'page': page,
            "per_page": per_page
        }
    url = urljoin(urljoin(conf.URL, "book/"), "search_all")
    r = requests.post(url, json=json)
    return r.status_code,r.json()


class BookDB:
    def __init__(self, large: bool = False):
        parent_path = os.path.dirname(os.path.dirname(__file__))
        self.db_s = os.path.join(parent_path, "data/book.db")
        self.db_l = os.path.join(parent_path, "data/book_lx.db")
        if large:
            self.book_db = self.db_l
        else:
            self.book_db = self.db_s

        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["bookstore"]

    def get_book_count(self):
        collection = self.db["book"]
        count = collection.count_documents({})
        return count
    
    def get_book_info(self, start, size):
        books = []
        collection = self.db["book"]

        start_doc = collection.find_one(skip=start, sort=[('_id', pymongo.ASCENDING)])
        if not start_doc:
            return [] 

        query = {"_id": {"$gte": start_doc["_id"]}}
        cursor = collection.find(query, {"_id": 0}).sort("_id", pymongo.ASCENDING).limit(size)
        rows = list(cursor)

        for doc in rows:
            book = Book()
            book.id = doc.get("id")
            book.title = doc.get("title")
            book.author = doc.get("author")
            book.publisher = doc.get("publisher")
            book.original_title = doc.get("original_title")
            book.translator = doc.get("translator")
            book.pub_year = doc.get("pub_year")
            book.pages = doc.get("pages")
            book.price = doc.get("price")
            book.currency_unit = doc.get("currency_unit")
            book.binding = doc.get("binding")
            book.isbn = doc.get("isbn")
            book.author_intro = doc.get("author_intro")
            book.book_intro = doc.get("book_intro")
            book.content = doc.get("content")
            pictures = str(doc.get("picture"))
            book.tags = doc.get("tags")

            books.append(book)

        return books
