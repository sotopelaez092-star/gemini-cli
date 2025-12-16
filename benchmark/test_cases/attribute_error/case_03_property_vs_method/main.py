# Case 03: Property vs method confusion
# Difficulty: Medium

from models.order import Order

def main():
    order = Order(["item1", "item2"], quantities=[2, 3], prices=[10.0, 20.0])
    # Error: 'total' is a property, not a method - should not have ()
    # But user called it as total()
    print(f"Order total: ${order.total()}")

if __name__ == "__main__":
    main()
