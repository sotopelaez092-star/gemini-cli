"""测试用例 - 验证配置字段名不匹配是否修复"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database_connection():
    """测试数据库连接"""
    from config.settings import DatabaseConfig
    from database.connection import DatabaseConnection

    config = DatabaseConfig(
        connection_string="postgresql://localhost:5432/testdb",
        pool_size=10,
        timeout=60
    )

    db = DatabaseConnection(config)
    result = db.connect()
    assert "Connected" in result
    return True

def test_cache_connection():
    """测试缓存连接"""
    from config.settings import CacheConfig
    from cache.redis_cache import RedisCache

    config = CacheConfig(
        host="localhost",
        port=6379,
        auth_token="secret123"
    )

    cache = RedisCache(config)
    result = cache.connect()
    assert "redis://" in result
    return True

def test_full_app_service():
    """测试完整应用服务"""
    from config.settings import AppConfig, DatabaseConfig, CacheConfig
    from services.app_service import AppService

    config = AppConfig(
        database=DatabaseConfig(connection_string="postgresql://localhost/db"),
        cache=CacheConfig(host="localhost", port=6379, auth_token="secret"),
        debug=True
    )

    service = AppService(config)
    service.initialize()

    data = service.get_data("test_key")
    assert data is not None
    return True

if __name__ == "__main__":
    try:
        test_database_connection()
        print("test_database_connection: OK")

        test_cache_connection()
        print("test_cache_connection: OK")

        test_full_app_service()
        print("test_full_app_service: OK")

        print("PASS")
        sys.exit(0)
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)
