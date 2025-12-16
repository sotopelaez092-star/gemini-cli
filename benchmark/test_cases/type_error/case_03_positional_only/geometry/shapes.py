"""Geometry calculations with positional-only parameters for performance."""

import math

def calculate_area(shape, dim1, dim2=None, /):
    """Calculate area of a shape.

    Note: shape, dim1, dim2 are positional-only parameters (before /)
    for API consistency and potential performance optimization.

    Args:
        shape: Shape type ('rectangle', 'triangle', 'circle')
        dim1: First dimension (width for rectangle, base for triangle, radius for circle)
        dim2: Second dimension (height for rectangle/triangle, None for circle)

    Returns:
        Calculated area
    """
    if shape == "rectangle":
        if dim2 is None:
            raise ValueError("Rectangle requires two dimensions")
        return dim1 * dim2
    elif shape == "triangle":
        if dim2 is None:
            raise ValueError("Triangle requires base and height")
        return 0.5 * dim1 * dim2
    elif shape == "circle":
        return math.pi * dim1 ** 2
    else:
        raise ValueError(f"Unknown shape: {shape}")


def calculate_perimeter(shape, /, *dimensions):
    """Calculate perimeter of a shape."""
    if shape == "rectangle" and len(dimensions) == 2:
        return 2 * (dimensions[0] + dimensions[1])
    elif shape == "circle" and len(dimensions) == 1:
        return 2 * math.pi * dimensions[0]
    raise ValueError("Invalid arguments")
