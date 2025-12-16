# Case 03: Positional-only parameter violation
# Difficulty: Hard
# Function uses positional-only parameters (Python 3.8+)

from geometry.shapes import calculate_area

def main():
    # Error: 'width' and 'height' are positional-only parameters
    # Cannot be passed as keyword arguments
    area = calculate_area(shape="rectangle", width=10, height=5)
    print(f"Area: {area}")

if __name__ == "__main__":
    main()
