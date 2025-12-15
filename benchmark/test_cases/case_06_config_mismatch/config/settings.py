"""配置设置"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class DatabaseConfig:
    # Bug: 字段名从 url 改成了 connection_string，但其他文件还在用旧名字
    connection_string: str  # 原来叫 url
    pool_size: int = 5
    timeout: int = 30

@dataclass
class CacheConfig:
    host: str
    port: int
    # Bug: 原来叫 password，改成了 auth_token
    auth_token: Optional[str] = None

@dataclass
class AppConfig:
    database: DatabaseConfig
    cache: CacheConfig
    debug: bool = False
