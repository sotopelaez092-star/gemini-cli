class PaymentProcessor:
    def process(self, amount):
        return {"status": "success", "amount": amount, "transaction_id": "txn_123"}
