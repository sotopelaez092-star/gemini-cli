"""通知服务"""
from core.task_queue import TaskQueue, Task

class NotificationService:
    def __init__(self, task_queue: TaskQueue):
        self.task_queue = task_queue
        self.notifications = []

    async def on_email_task_complete(self, task: Task):
        """
        邮件任务完成回调

        Bug: 这个回调期望 task.status == "completed"
        但由于任务队列的 bug，回调在状态更新前被调用
        """
        if task.status != "completed":
            raise ValueError(f"Expected task status 'completed', got '{task.status}'")

        if task.result is None:
            raise ValueError("Task result should not be None")

        notification = {
            "type": "email_sent",
            "task_id": task.id,
            "result": task.result
        }
        self.notifications.append(notification)

    def get_notifications(self):
        return self.notifications
