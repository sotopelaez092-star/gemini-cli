"""数据处理器 - 中间层"""
from core.base_handler import BaseHandler
from typing import Any, Dict, List

class DataHandler(BaseHandler):
    """数据处理器基类"""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.processed_count = 0

    def _validate_config(self):
        """验证数据处理配置"""
        if "batch_size" not in self.config:
            self.config["batch_size"] = 100

    def _setup(self):
        """设置数据处理器"""
        self.batch_size = self.config["batch_size"]

    def handle(self, data: Any) -> Any:
        """处理单条数据"""
        result = self._process(data)
        self.processed_count += 1
        return result

    def handle_batch(self, data_list: List[Any]) -> List[Any]:
        """批量处理"""
        return [self.handle(item) for item in data_list]

    def _process(self, data: Any) -> Any:
        """实际处理逻辑 - 子类应该覆盖"""
        return data
