from be.model import store


class DBConn:
    def __init__(self):
        self.client = self.conn = store.get_db_conn()

        self.db = self.client["bookstore"]  # 切换到你的数据库
        self.user_collection = self.db["user"]  # 获取 users 集合
        self.store_collection = self.db["store"]  # 获取 store 集合
        self.user_store_collection = self.db["user_store"]  # 获取 user_store 集合

    def user_id_exist(self, user_id):
        # 查询用户是否存在
        query = {"user_id": user_id}
        user = self.user_collection.find_one(query)
        return user is not None

    def book_id_exist(self, store_id, book_id):
        # 查询书籍是否存在于指定店铺
        query = {"store_id": store_id, "book_id": book_id}
        book = self.conn['bookstore']['store'].find_one(query)
        return book is not None

    def store_id_exist(self, store_id):
        # 查询店铺是否存在
        query = {"store_id": store_id}
        store = self.user_store_collection.find_one(query)
        return store is not None