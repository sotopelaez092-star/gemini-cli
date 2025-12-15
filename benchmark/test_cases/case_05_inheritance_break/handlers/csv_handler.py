"""CSV 处理器"""
import csv
import io
from handlers.data_handler import DataHandler
from typing import Any, Dict, List

class CsvHandler(DataHandler):
    """
    CSV 数据处理器

    这个类正确实现了继承，作为对比
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)  # 正确调用父类
        self.delimiter = self.config.get("delimiter", ",")

    def _validate_config(self):
        """验证 CSV 配置"""
        super()._validate_config()
        if "headers" not in self.config:
            self.config["headers"] = []

    def _process(self, data: Dict[str, Any]) -> str:
        """将字典转换为 CSV 行"""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data.keys(), delimiter=self.delimiter)
        writer.writerow(data)
        return output.getvalue().strip()
