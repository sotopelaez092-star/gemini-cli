# Case 01: Simple A -> B -> A circular import
# Difficulty: Medium

from module_a import ClassA

def main():
    a = ClassA()
    result = a.process()
    print(result)

if __name__ == "__main__":
    main()
