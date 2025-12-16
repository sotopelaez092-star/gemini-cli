# Module A - imports B at top level
from module_b import ClassB

class ClassA:
    def __init__(self):
        self.b = ClassB()

    def process(self):
        return self.b.do_work("data from A")

    def callback(self, data):
        return f"A processed: {data}"
