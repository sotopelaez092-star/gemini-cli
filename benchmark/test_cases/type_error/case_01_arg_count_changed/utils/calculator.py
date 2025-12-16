"""Financial calculators - Updated API (v2.0)

Breaking change: calculate_compound_interest now uses monthly compounding by default
and no longer accepts compounds_per_year parameter.
Use calculate_compound_interest_custom for custom compounding periods.
"""

def calculate_compound_interest(principal, rate, years):
    """Calculate compound interest with monthly compounding (default).

    Args:
        principal: Initial investment amount
        rate: Annual interest rate (as decimal, e.g., 0.05 for 5%)
        years: Number of years

    Returns:
        Final amount after compound interest
    """
    n = 12  # Monthly compounding (fixed)
    return principal * (1 + rate/n) ** (n * years)


def calculate_compound_interest_custom(principal, rate, years, compounds_per_year):
    """Calculate compound interest with custom compounding period.

    Args:
        principal: Initial investment amount
        rate: Annual interest rate (as decimal)
        years: Number of years
        compounds_per_year: Number of times interest is compounded per year

    Returns:
        Final amount after compound interest
    """
    return principal * (1 + rate/compounds_per_year) ** (compounds_per_year * years)


def calculate_simple_interest(principal, rate, years):
    """Calculate simple interest."""
    return principal * (1 + rate * years)
