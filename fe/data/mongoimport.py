import sqlite3
from pymongo import MongoClient

sqlite_db_path = 'C:\\data_management_sys\\AllStuRead\\Project_1\\bookstore\\fe\\data\\book_lx.db'
mongo_uri = 'mongodb://user:password@localhost:27017/'
mongo_db_name = 'bookstore'
collection_name = 'book'

conn = sqlite3.connect(sqlite_db_path)
cursor = conn.cursor()

client = MongoClient(mongo_uri)
db = client[mongo_db_name]
collection = db[collection_name]
 

query = "SELECT * FROM book"
cursor.execute(query)
rows = cursor.fetchall()

for row in rows:
    document = dict(zip([col[0] for col in cursor.description], row))
    collection.insert_one(document)

cursor.close()
conn.close()

