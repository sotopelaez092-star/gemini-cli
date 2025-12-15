"""Redis 缓存"""
from config.settings import CacheConfig

class RedisCache:
    def __init__(self, config: CacheConfig):
        self.config = config
        self._client = None

    def connect(self):
        """连接 Redis"""
        host = self.config.host
        port = self.config.port
        # Bug: 使用了旧的字段名 password，但配置已经改成 auth_token
        password = self.config.password  # AttributeError

        connection_info = f"redis://{host}:{port}"
        if password:
            connection_info += f" with auth"

        self._client = connection_info
        return self._client

    def get(self, key: str):
        """获取缓存"""
        if not self._client:
            self.connect()
        return f"Value for {key}"

    def set(self, key: str, value: str, ttl: int = 3600):
        """设置缓存"""
        if not self._client:
            self.connect()
        return True
