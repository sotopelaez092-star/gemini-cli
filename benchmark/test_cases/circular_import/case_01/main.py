# Case 01: Circular Import - A imports B, B imports A
from module_a import ClassA

def main():
    a = ClassA()
    result = a.process()
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
