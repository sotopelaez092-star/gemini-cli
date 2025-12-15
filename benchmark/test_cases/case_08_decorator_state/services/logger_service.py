"""日志服务"""
from core.registry import service, ServiceRegistry
from typing import List

@service("logger")
class LoggerService:
    def __init__(self):
        self.logs: List[str] = []

    def log(self, message: str):
        """记录日志"""
        self.logs.append(message)
        print(f"[LOG] {message}")

    def get_logs(self) -> List[str]:
        """获取所有日志"""
        return self.logs
