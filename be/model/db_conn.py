from be.model import store


class DBConn:
    def __init__(self):
        self.client = self.conn = store.get_db_conn()
        
        self.db = self.client["bookstore"] 
        self.user_collection = self.db["user"]  
        self.store_collection = self.db["store"]  
        self.user_store_collection = self.db["user_store"] 
        self.order_collection = self.db["new_order"]                    

    def user_id_exist(self, user_id):
        query = {"user_id": user_id}
        user = self.user_collection.find_one(query)
        return user is not None

    def book_id_exist(self, store_id, book_id):
        query = {"store_id": store_id, "book_id": book_id}
        book = self.store_collection.find_one(query)
        return book is not None

    def store_id_exist(self, store_id):
        query = {"store_id": store_id}
        store = self.user_store_collection.find_one(query)
        return store is not None
    
    def order_id_exist(self, user_id, order_id):                    
        query = {"user_id": user_id, "order_id": order_id}
        order = self.order_collection.find_one(query)
        return order is not None
