import math
from shapes.base import Shape
from factory.shape_factory import ShapeFactory  # Creates cycle!

class Circle(Shape):
    def __init__(self, factory: ShapeFactory, radius: float):
        super().__init__(factory)
        self.radius = radius

    def area(self):
        return math.pi * self.radius ** 2

    def create_bounding_box(self):
        """Create a rectangle that bounds this circle."""
        return self.create_sibling("rectangle", width=self.radius*2, height=self.radius*2)
