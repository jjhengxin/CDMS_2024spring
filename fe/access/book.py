import os
import sqlite3 as sqlite
import random
import simplejson as json
import pymongo
import base64

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
    tags: [str]
    pictures: [bytes]

    def __init__(self):
        self.tags = []
        self.pictures = []


# class BookDB:
#     def __init__(self, large: bool = False):
#         parent_path = os.path.dirname(os.path.dirname(__file__))
#         self.db_s = os.path.join(parent_path, "data/book.db")
#         self.db_l = os.path.join(parent_path, "data/book_lx.db")
#         if large:
#             self.book_db = self.db_l
#         else:
#             self.book_db = self.db_s

#     def get_book_count(self):
#         conn = sqlite.connect(self.book_db)
#         cursor = conn.execute("SELECT count(id) FROM book")
#         row = cursor.fetchone()
#         return row[0]
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
        cursor = collection.find().skip(start).limit(size)
    # def get_book_info(self, start, size) -> list[Book]:
    #     books = []
    #     conn = sqlite.connect(self.book_db)
    #     cursor = conn.execute(
    #         "SELECT id, title, author, "
    #         "publisher, original_title, "
    #         "translator, pub_year, pages, "
    #         "price, currency_unit, binding, "
    #         "isbn, author_intro, book_intro, "
    #         "content, tags, picture FROM book ORDER BY id "
    #         "LIMIT ? OFFSET ?",
    #         (size, start),
    #     )
    #     for row in cursor:
    #         book = Book()
    #         book.id = row[0]
    #         book.title = row[1]
    #         book.author = row[2]
    #         book.publisher = row[3]
    #         book.original_title = row[4]
    #         book.translator = row[5]
    #         book.pub_year = row[6]
    #         book.pages = row[7]
    #         book.price = row[8]

    #         book.currency_unit = row[9]
    #         book.binding = row[10]
    #         book.isbn = row[11]
    #         book.author_intro = row[12]
    #         book.book_intro = row[13]
    #         book.content = row[14]
    #         tags = row[15]

    #         pictures = row[16]

    #         for tag in tags.split("\n"):
    #             if tag.strip() != "":
    #                 book.tags.append(tag)
            #for i in range(0, random.randint(0, 9)):
        for doc in cursor:
            book = Book()
            # book.id = str(doc["_id"])
            # book.title = doc["title"]
            # book.author = doc["author"]
            # book.publisher = doc["publisher"]
            # book.original_title = doc["original_title"]
            # book.translator = doc["translator"]
            # book.pub_year = doc["pub_year"]
            # book.pages = doc["pages"]
            # book.price = doc["price"]
            # book.currency_unit = doc["currency_unit"]
            # book.binding = doc["binding"]
            # book.isbn = doc["isbn"]
            # book.author_intro = doc["author_intro"]
            # book.book_intro = doc["book_intro"]
            # book.content = doc["content"]
            # tags = str(doc["tags"])
            # pictures = str(doc["picture"])
            book.id = doc.get("id")
            book.title = doc.get("title")
            book.author = doc.get("author")
            book.publisher = doc.get("publisher")
            book.original_title = doc.get("original title")
            book.translator = doc.get("translator")
            book.pub_year = doc.get("pub year")
            book.pages = doc.get("pages")
            book.price = doc.get("price")
            book.currency_unit = doc.get("currency unit")
            book.binding = doc.get("binding")
            book.isbn = doc.get("isbn")
            book.author_intro = doc.get("author intro")
            book.book_intro = doc.get("book intro")
            book.content = doc.get("content")
            pictures = str(doc.get("picture"))
            tags = doc.get("tags")

            for tag in tags.split("\n"):
                if tag.strip() != "":
                    book.tags.append(tag)

            if pictures:        
                for picture in pictures: 
                    encode_str = base64.b64encode(picture.encode()).decode("utf-8")
                    book.pictures.append(encode_str)
                    # # encode_str = picture.decode_base64().decode("utf-8")
                    # # 将整数转换为字节串
                    # picture_bytes = picture.to_bytes((picture.bit_length() + 7) // 8, 'big')

                    # # 将字节串解码为 UTF-8 格式的字符串
                    # encode_str = base64.b64decode(picture_bytes).decode("utf-8")
                    # book.pictures.append(encode_str)
            books.append(book)
            # print(tags.decode('utf-8'))

            # print(book.tags, len(book.picture))
            # print(book)
            # print(tags)

        return books
