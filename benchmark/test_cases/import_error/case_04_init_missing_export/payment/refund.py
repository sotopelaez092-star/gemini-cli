class RefundProcessor:
    def refund(self, transaction_id, amount):
        return {"status": "refunded", "amount": amount}
