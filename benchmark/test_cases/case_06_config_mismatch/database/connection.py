"""数据库连接"""
from config.settings import DatabaseConfig

class DatabaseConnection:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._connection = None

    def connect(self):
        """建立连接"""
        # Bug: 使用了旧的字段名 url，但配置已经改成 connection_string
        url = self.config.url  # AttributeError: 'DatabaseConfig' object has no attribute 'url'
        self._connection = f"Connected to {url}"
        return self._connection

    def disconnect(self):
        """断开连接"""
        self._connection = None

    def execute(self, query: str):
        """执行查询"""
        if not self._connection:
            self.connect()
        return f"Executed: {query}"
