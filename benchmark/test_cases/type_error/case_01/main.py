# Case 01: TypeError - wrong number of arguments
from calculator import Calculator

def main():
    calc = Calculator()
    # Error: add() takes 2 positional arguments but 3 were given
    # The function signature changed from add(a, b, c) to add(a, b)
    result = calc.add(1, 2, 3)
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
