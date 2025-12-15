"""测试用例 - 验证装饰器状态和服务注册顺序问题是否修复"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def reset_registry():
    """重置注册表"""
    from core.registry import ServiceRegistry
    ServiceRegistry._instance = None
    ServiceRegistry._services = {}
    ServiceRegistry._middlewares = []

def test_service_registration_order():
    """
    测试服务注册顺序

    问题: user_service 依赖 logger_service
    但 services/__init__.py 中先导入 user_service

    预期: 所有服务都能正确注册并使用
    """
    reset_registry()

    # 这行导入会触发装饰器执行
    # 如果顺序不对，会抛出 RuntimeError
    from services import UserService, LoggerService

    from core.registry import ServiceRegistry
    registry = ServiceRegistry()

    # 验证服务都已注册
    logger = registry.get("logger")
    user = registry.get("user")

    assert logger is not None, "Logger service should be registered"
    assert user is not None, "User service should be registered"

    return True

def test_user_api_operations():
    """测试用户 API 操作"""
    reset_registry()

    # 触发服务注册
    from services import UserService, LoggerService
    from api.user_api import UserAPI

    api = UserAPI()

    # 注册用户
    result = api.register_user({"username": "testuser"})
    assert result["status"] == "success"

    # 获取用户信息
    user_info = api.get_user_info(1)
    assert user_info["id"] == 1

    return True

if __name__ == "__main__":
    try:
        test_service_registration_order()
        print("test_service_registration_order: OK")

        test_user_api_operations()
        print("test_user_api_operations: OK")

        print("PASS")
        sys.exit(0)
    except Exception as e:
        print(f"FAIL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
