"""账户服务 - 包含竞态条件 bug"""
import time
from database.connection import Database

class AccountService:
    def __init__(self):
        self.db = Database()

    def create_account(self, account_id: str, balance: float):
        """创建账户"""
        self.db.set(account_id, {"id": account_id, "balance": balance})

    def get_balance(self, account_id: str) -> float:
        """获取余额"""
        account = self.db.get(account_id)
        return account["balance"] if account else 0

    def transfer(self, from_id: str, to_id: str, amount: float) -> bool:
        """
        转账 - Bug: 存在竞态条件
        读取-修改-写入操作没有原子性保护
        """
        # 读取两个账户
        from_account = self.db.get(from_id)
        to_account = self.db.get(to_id)

        if not from_account or not to_account:
            return False

        if from_account["balance"] < amount:
            return False

        # Bug: 这里存在竞态条件
        # 模拟网络延迟，使竞态条件更容易触发
        time.sleep(0.01)

        # 修改余额
        new_from_balance = from_account["balance"] - amount
        new_to_balance = to_account["balance"] + amount

        # 写回数据库 - 可能覆盖其他并发操作的结果
        self.db.update(from_id, "balance", new_from_balance)
        self.db.update(to_id, "balance", new_to_balance)

        return True
