"""基础处理器"""
from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseHandler(ABC):
    """所有处理器的基类"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self._initialized = False

    def initialize(self):
        """初始化处理器"""
        self._validate_config()
        self._setup()
        self._initialized = True

    @abstractmethod
    def _validate_config(self):
        """验证配置 - 子类必须实现"""
        pass

    @abstractmethod
    def _setup(self):
        """设置处理器 - 子类必须实现"""
        pass

    @abstractmethod
    def handle(self, data: Any) -> Any:
        """处理数据 - 子类必须实现"""
        pass

    def is_ready(self) -> bool:
        """检查是否准备就绪"""
        return self._initialized
