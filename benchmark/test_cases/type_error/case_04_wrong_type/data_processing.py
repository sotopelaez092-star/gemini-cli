"""Data processing utilities."""

from typing import List, Dict, Union

def aggregate_values(values: List[Union[int, float]]) -> float:
    """Aggregate a list of numeric values.

    Args:
        values: List of numbers to aggregate

    Returns:
        Sum of all values

    Raises:
        TypeError: If values is not a list
    """
    if not isinstance(values, list):
        raise TypeError(f"Expected list, got {type(values).__name__}")
    return sum(values)


def aggregate_dict_values(data: Dict[str, Union[int, float]]) -> float:
    """Aggregate values from a dictionary.

    Args:
        data: Dictionary with numeric values

    Returns:
        Sum of all dictionary values
    """
    return sum(data.values())


def aggregate_nested(data: Dict[str, List[Union[int, float]]]) -> Dict[str, float]:
    """Aggregate nested data structure.

    Args:
        data: Dictionary mapping keys to lists of numbers

    Returns:
        Dictionary with aggregated values per key
    """
    return {key: sum(values) for key, values in data.items()}
