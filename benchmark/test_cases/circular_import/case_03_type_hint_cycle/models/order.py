from typing import List
from models.order_item import OrderItem  # Needed for type hint

class Order:
    def __init__(self, order_id: int):
        self.order_id = order_id
        self.items: List[OrderItem] = []

    def add_item(self, name: str, quantity: int, price: float):
        item = OrderItem(name=name, quantity=quantity, price=price, order=self)
        self.items.append(item)

    @property
    def total(self) -> float:
        return sum(item.subtotal for item in self.items)
