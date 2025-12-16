# Case 02: AttributeError - accessing renamed property
from models.product import Product

def display_product(product_id):
    product = Product(product_id, "Laptop", 999.99)
    # Error: 'prce' should be 'price' (property was renamed)
    print(f"Product: {product.name}, Price: ${product.prce}")

if __name__ == "__main__":
    display_product(1)
