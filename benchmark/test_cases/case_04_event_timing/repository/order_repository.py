"""订单仓库"""

class OrderRepository:
    _instance = None
    _orders = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def save(self, order: dict):
        """保存订单"""
        self._orders[order["id"]] = order

    def get(self, order_id: int) -> dict:
        """获取订单"""
        return self._orders.get(order_id)

    def reset(self):
        """重置数据"""
        self._orders = {}
