# Case 04: Circular import in factory pattern
# Difficulty: Hard
# Factory creates objects that reference the factory

from factory.shape_factory import ShapeFactory

def main():
    factory = ShapeFactory()
    circle = factory.create("circle", radius=5)
    print(f"Area: {circle.area()}")

if __name__ == "__main__":
    main()
