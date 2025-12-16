# Module A - imports Module B at top level (causes circular import)
from module_b import ClassB

class ClassA:
    def __init__(self):
        self.helper = ClassB()

    def process(self):
        return self.helper.do_something("from A")

    def callback(self, data):
        return f"A received: {data}"
