class Order:
    """Order with items, quantities and prices."""

    def __init__(self, items, quantities, prices):
        self.items = items
        self.quantities = quantities
        self.prices = prices
        self._discount = 0

    @property
    def total(self):
        """Calculate total price (property, not method)."""
        subtotal = sum(q * p for q, p in zip(self.quantities, self.prices))
        return subtotal * (1 - self._discount)

    @property
    def item_count(self):
        """Total number of items."""
        return sum(self.quantities)

    def apply_discount(self, percent):
        """Apply discount percentage."""
        self._discount = percent / 100

    def add_item(self, item, quantity, price):
        """Add an item to order."""
        self.items.append(item)
        self.quantities.append(quantity)
        self.prices.append(price)
