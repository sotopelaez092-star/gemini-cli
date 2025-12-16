from abc import ABC, abstractmethod

class Shape(ABC):
    def __init__(self, factory):
        self.factory = factory  # Reference back to factory

    @abstractmethod
    def area(self):
        pass

    def create_sibling(self, shape_type, **kwargs):
        """Create another shape using the same factory."""
        return self.factory.create(shape_type, **kwargs)
