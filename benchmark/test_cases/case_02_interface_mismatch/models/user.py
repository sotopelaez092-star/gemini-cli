"""用户模型"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class User:
    id: int
    username: str
    email: str
    created_at: datetime
    # Bug: 新增了 role 字段，但其他文件还没更新
    role: str = "user"
    is_active: bool = True
