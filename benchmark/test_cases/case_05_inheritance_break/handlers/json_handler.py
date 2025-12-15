"""JSON 处理器"""
import json
from handlers.data_handler import DataHandler
from typing import Any, Dict

class JsonHandler(DataHandler):
    """
    JSON 数据处理器

    Bug: 继承链断裂
    1. 重写了 __init__ 但没有调用 super().__init__()
    2. 导致 BaseHandler 的属性没有初始化
    """

    def __init__(self, config: Dict[str, Any] = None):
        # Bug: 没有调用 super().__init__(config)
        self.config = config or {}
        self.indent = self.config.get("indent", 2)
        # 缺少: self._initialized = False

    def _process(self, data: Any) -> str:
        """将数据转换为 JSON 字符串"""
        return json.dumps(data, indent=self.indent)

    def parse(self, json_str: str) -> Any:
        """解析 JSON 字符串"""
        return json.loads(json_str)
