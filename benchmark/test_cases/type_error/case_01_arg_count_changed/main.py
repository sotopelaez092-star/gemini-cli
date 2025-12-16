# Case 01: Function signature changed - argument count
# Difficulty: Medium
# Function was refactored, now takes fewer arguments

from utils.calculator import calculate_compound_interest

def main():
    principal = 1000
    rate = 0.05
    years = 10
    compounds_per_year = 12

    # Error: Function signature changed, no longer takes compounds_per_year
    # Old: calculate_compound_interest(principal, rate, years, compounds_per_year)
    # New: calculate_compound_interest(principal, rate, years) - uses monthly by default
    result = calculate_compound_interest(principal, rate, years, compounds_per_year)
    print(f"Final amount: ${result:.2f}")

if __name__ == "__main__":
    main()
