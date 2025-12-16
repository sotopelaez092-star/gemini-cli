# Case 04: Wrong argument type passed
# Difficulty: Medium
# Function expects list but dict is passed

from data_processing import aggregate_values

def main():
    # Data from API response
    data = {
        "sales": 1500,
        "returns": 200,
        "expenses": 800
    }

    # Error: aggregate_values expects a list of numbers, not a dict
    total = aggregate_values(data)
    print(f"Total: {total}")

if __name__ == "__main__":
    main()
