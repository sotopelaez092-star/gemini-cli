from shapes.base import Shape

class Rectangle(Shape):
    def __init__(self, factory, width: float, height: float):
        super().__init__(factory)
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height
