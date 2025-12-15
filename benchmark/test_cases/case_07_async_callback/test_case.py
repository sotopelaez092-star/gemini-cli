"""测试用例 - 验证异步回调顺序问题是否修复"""
import sys
import os
import asyncio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_email_task_with_callback():
    """
    测试邮件任务带回调

    预期流程:
    1. 提交邮件任务
    2. 处理任务（发送邮件）
    3. 更新任务状态为 completed
    4. 触发回调

    Bug: 回调在步骤 2 之前就被触发了
    """
    from core.task_queue import TaskQueue
    from services.email_service import EmailService
    from services.notification_service import NotificationService

    # 设置
    task_queue = TaskQueue()
    email_service = EmailService()
    notification_service = NotificationService(task_queue)

    # 注册处理器
    task_queue.register_handler("send_email", email_service.get_handler())

    # 提交任务
    task = await task_queue.submit(
        task_id="email_001",
        handler_name="send_email",
        payload={
            "to": "user@example.com",
            "subject": "Test Email",
            "body": "Hello World"
        }
    )

    # 注册回调
    task_queue.register_callback("email_001", notification_service.on_email_task_complete)

    # 处理任务
    await task_queue.process("email_001")

    # 验证
    assert task.status == "completed", f"Expected 'completed', got '{task.status}'"
    assert len(notification_service.get_notifications()) == 1
    assert notification_service.get_notifications()[0]["task_id"] == "email_001"

    return True

def test_sync_wrapper():
    """同步包装器"""
    return asyncio.run(test_email_task_with_callback())

if __name__ == "__main__":
    try:
        if test_sync_wrapper():
            print("PASS")
            sys.exit(0)
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)
