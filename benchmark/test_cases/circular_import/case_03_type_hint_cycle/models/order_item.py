from models.order import Order  # Needed for type hint - creates cycle!

class OrderItem:
    def __init__(self, name: str, quantity: int, price: float, order: Order):
        self.name = name
        self.quantity = quantity
        self.price = price
        self.order = order  # Reference back to parent order

    @property
    def subtotal(self) -> float:
        return self.quantity * self.price

    def get_order_id(self) -> int:
        return self.order.order_id
