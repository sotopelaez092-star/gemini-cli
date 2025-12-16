# Module B - imports Module A at top level (causes circular import)
from module_a import ClassA

class ClassB:
    def __init__(self):
        pass

    def do_something(self, data):
        # Needs to call back to ClassA
        a = ClassA()
        return a.callback(data)
