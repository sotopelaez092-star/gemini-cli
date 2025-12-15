"""应用服务"""
from config.settings import AppConfig, DatabaseConfig, CacheConfig
from database.connection import DatabaseConnection
from cache.redis_cache import RedisCache

class AppService:
    def __init__(self, config: AppConfig):
        self.config = config
        self.db = DatabaseConnection(config.database)
        self.cache = RedisCache(config.cache)

    def initialize(self):
        """初始化所有服务"""
        self.db.connect()
        self.cache.connect()
        return True

    def get_data(self, key: str):
        """获取数据，先查缓存再查数据库"""
        cached = self.cache.get(key)
        if cached:
            return cached
        return self.db.execute(f"SELECT * FROM data WHERE key = '{key}'")
