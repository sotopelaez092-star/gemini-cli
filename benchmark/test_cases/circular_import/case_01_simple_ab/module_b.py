# Module B - imports A at top level (creates circular import!)
from module_a import ClassA

class ClassB:
    def do_work(self, data):
        # Needs to call back to A
        a = ClassA()
        return a.callback(data)
