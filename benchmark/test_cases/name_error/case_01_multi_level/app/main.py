# Case 01: Multi-level package symbol reference with typo
# Difficulty: Medium
# The symbol is defined deep in the package hierarchy

from app.services.analytics import AnalyticsService

def run_analytics():
    service = AnalyticsService()
    # Error: 'proccess_metrics' is typo, should be 'process_metrics'
    # The correct function is in app/core/metrics/processor.py
    result = service.proccess_metrics([1, 2, 3, 4, 5])
    return result

if __name__ == "__main__":
    print(run_analytics())
