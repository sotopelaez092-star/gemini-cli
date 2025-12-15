"""全局注册表"""
from typing import Dict, Any, Callable, List
from functools import wraps

class ServiceRegistry:
    """服务注册表 - 单例"""
    _instance = None
    _services: Dict[str, Any] = {}
    _middlewares: List[Callable] = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register(self, name: str, service: Any):
        """注册服务"""
        self._services[name] = service

    def get(self, name: str) -> Any:
        """获取服务"""
        return self._services.get(name)

    def add_middleware(self, middleware: Callable):
        """添加中间件"""
        self._middlewares.append(middleware)

    def get_middlewares(self) -> List[Callable]:
        """获取所有中间件"""
        return self._middlewares

    def reset(self):
        """重置注册表"""
        self._services = {}
        self._middlewares = []


def service(name: str):
    """
    服务装饰器

    Bug: 这个装饰器在类定义时就注册服务
    但此时 ServiceRegistry 可能还没有正确初始化
    """
    def decorator(cls):
        # Bug: 在装饰时立即创建实例并注册
        # 这会导致依赖问题，因为其他服务可能还没注册
        registry = ServiceRegistry()
        instance = cls()  # 创建实例
        registry.register(name, instance)
        return cls
    return decorator
