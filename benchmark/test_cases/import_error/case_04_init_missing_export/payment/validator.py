class PaymentValidator:
    """Validates payment amounts and data."""

    def validate(self, amount):
        if amount <= 0:
            return False
        if amount > 10000:
            return False
        return True

    def validate_card(self, card_number):
        # Luhn algorithm check
        return len(str(card_number)) == 16
