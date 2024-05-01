import threading
from datetime import datetime, timedelta
from be.model import error, db_conn


class OrderAutoCancel(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def cancel_unpaid_orders(self):
        try:
            new_orders = self.conn['bookstore']["new_order"]
            unpaid_order_cursor = new_orders.find({"status": "unpaid"})
            
            current_time = datetime.now()
            earliest_time = current_time - timedelta(minutes=1)

            for order in unpaid_order_cursor:
                order_time = datetime.fromisoformat(order["created_at"])
                if order_time < earliest_time:
                    new_orders.update_one(
                        {"order_id": order["order_id"]},
                        {"$set": {"status": "cancelled"}}
                    )
        except Exception as e:
            print(f"Error canceling unpaid orders: {str(e)}")


if __name__ == "__main__":
    order_auto_cancel = OrderAutoCancel()