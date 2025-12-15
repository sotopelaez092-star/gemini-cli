"""转账 API"""
from services.account_service import AccountService
import threading

class TransferAPI:
    def __init__(self):
        self.account_service = AccountService()

    def setup_accounts(self):
        """初始化测试账户"""
        self.account_service.create_account("A", 1000.0)
        self.account_service.create_account("B", 1000.0)

    def do_transfer(self, from_id: str, to_id: str, amount: float) -> dict:
        """执行转账"""
        success = self.account_service.transfer(from_id, to_id, amount)
        return {
            "success": success,
            "from_balance": self.account_service.get_balance(from_id),
            "to_balance": self.account_service.get_balance(to_id)
        }

    def concurrent_transfers(self, num_transfers: int = 10):
        """并发转账测试"""
        threads = []

        def transfer_task():
            self.account_service.transfer("A", "B", 100)

        for _ in range(num_transfers):
            t = threading.Thread(target=transfer_task)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        return {
            "A_balance": self.account_service.get_balance("A"),
            "B_balance": self.account_service.get_balance("B")
        }
