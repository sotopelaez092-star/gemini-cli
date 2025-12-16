# Shape Factory - imports all shape classes
from shapes.circle import Circle
from shapes.rectangle import Rectangle

class ShapeFactory:
    def __init__(self):
        self._shapes = {
            "circle": Circle,
            "rectangle": Rectangle
        }

    def create(self, shape_type, **kwargs):
        shape_class = self._shapes.get(shape_type)
        if shape_class:
            return shape_class(factory=self, **kwargs)
        raise ValueError(f"Unknown shape: {shape_type}")

    def get_available_shapes(self):
        return list(self._shapes.keys())
