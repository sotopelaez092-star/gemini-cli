class Product:
    """Product model with renamed price attribute."""

    def __init__(self, product_id, name, price):
        self.product_id = product_id
        self.name = name
        self.price = price  # Note: was previously 'prce', now renamed to 'price'
        self.currency = "USD"

    def get_formatted_price(self):
        return f"{self.currency} {self.price:.2f}"

    def apply_discount(self, percent):
        self.price = self.price * (1 - percent / 100)
        return self.price
