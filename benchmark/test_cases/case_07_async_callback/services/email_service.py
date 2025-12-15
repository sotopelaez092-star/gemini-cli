"""邮件服务"""
import asyncio

class EmailService:
    def __init__(self):
        self.sent_emails = []

    async def send_email(self, payload: dict) -> dict:
        """发送邮件"""
        await asyncio.sleep(0.01)  # 模拟网络延迟
        email = {
            "to": payload["to"],
            "subject": payload["subject"],
            "body": payload["body"],
            "sent": True
        }
        self.sent_emails.append(email)
        return email

    def get_handler(self):
        """获取处理器函数"""
        return self.send_email
