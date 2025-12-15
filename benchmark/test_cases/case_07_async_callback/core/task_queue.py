"""任务队列"""
import asyncio
from typing import Callable, Any, Dict, List
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Task:
    id: str
    handler: str
    payload: Dict[str, Any]
    status: str = "pending"
    result: Any = None
    error: str = None
    created_at: datetime = field(default_factory=datetime.now)

class TaskQueue:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.handlers: Dict[str, Callable] = {}
        self.callbacks: Dict[str, List[Callable]] = {}

    def register_handler(self, name: str, handler: Callable):
        """注册任务处理器"""
        self.handlers[name] = handler

    def register_callback(self, task_id: str, callback: Callable):
        """注册任务完成回调"""
        if task_id not in self.callbacks:
            self.callbacks[task_id] = []
        self.callbacks[task_id].append(callback)

    async def submit(self, task_id: str, handler_name: str, payload: dict) -> Task:
        """提交任务"""
        task = Task(id=task_id, handler=handler_name, payload=payload)
        self.tasks[task_id] = task
        return task

    async def process(self, task_id: str):
        """
        处理任务

        Bug: 回调触发顺序问题
        回调在任务状态更新之前被调用
        """
        task = self.tasks.get(task_id)
        if not task:
            return

        handler = self.handlers.get(task.handler)
        if not handler:
            task.status = "failed"
            task.error = f"Handler {task.handler} not found"
            return

        try:
            # Bug: 先触发回调
            await self._trigger_callbacks(task_id, task)

            # 后执行任务和更新状态
            result = await handler(task.payload)
            task.result = result
            task.status = "completed"

        except Exception as e:
            task.status = "failed"
            task.error = str(e)

    async def _trigger_callbacks(self, task_id: str, task: Task):
        """触发回调"""
        callbacks = self.callbacks.get(task_id, [])
        for callback in callbacks:
            await callback(task)
