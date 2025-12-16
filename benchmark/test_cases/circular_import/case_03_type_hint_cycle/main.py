# Case 03: Circular import caused by type hints
# Difficulty: Hard
# Type annotations create import cycle

from models.order import Order

def main():
    order = Order(order_id=1)
    order.add_item("Widget", 2, 10.00)
    print(f"Order total: ${order.total}")

if __name__ == "__main__":
    main()
