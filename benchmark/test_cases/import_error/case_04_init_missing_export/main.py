# Case 04: Symbol not exported in __init__.py
# Difficulty: Medium
# The class exists but is not exported from the package __init__.py

from payment import PaymentProcessor, RefundProcessor, PaymentValidator

def process_payment(amount):
    validator = PaymentValidator()
    if validator.validate(amount):
        processor = PaymentProcessor()
        return processor.process(amount)
    return None

if __name__ == "__main__":
    print(process_payment(100.00))
