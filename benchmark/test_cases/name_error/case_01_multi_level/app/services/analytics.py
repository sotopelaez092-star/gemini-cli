from app.core.metrics.processor import MetricsProcessor

class AnalyticsService:
    def __init__(self):
        self.processor = MetricsProcessor()

    def process_metrics(self, data):
        """Process metrics using the core processor."""
        return self.processor.calculate(data)

    def generate_report(self, data):
        """Generate analytics report."""
        metrics = self.process_metrics(data)
        return {"status": "success", "metrics": metrics}
