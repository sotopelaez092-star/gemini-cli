"""测试用例 - 验证竞态条件是否修复"""
import sys
import os
import ast
import inspect
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_has_lock_protection():
    """
    检测 transfer 方法是否有锁保护

    这是一种静态检测方式，检查代码中是否使用了 threading.Lock
    比运行时检测竞态条件更可靠
    """
    from services.account_service import AccountService

    # 获取 transfer 方法的源代码
    source = inspect.getsource(AccountService.transfer)

    # 检查是否使用了锁
    has_lock = any([
        "lock" in source.lower(),
        "Lock()" in source,
        "with self." in source and "lock" in source.lower(),
        "acquire()" in source,
        "RLock" in source,
    ])

    if not has_lock:
        print("FAIL: transfer() method has no lock protection")
        print("The method should use threading.Lock to protect concurrent access")
        return False

    return True

def test_concurrent_transfers_basic():
    """
    基本的并发转账测试

    即使竞态条件是概率性的，我们至少要确保基本功能正常
    """
    from database.connection import Database
    Database._instance = None

    from api.transfer_api import TransferAPI

    api = TransferAPI()
    api.setup_accounts()

    # 单次转账应该正常
    result = api.do_transfer("A", "B", 100)
    assert result["success"] == True, "Single transfer should succeed"

    return True

def test_concurrent_integrity():
    """
    并发完整性测试 - 多次运行以检测竞态条件
    """
    import threading
    from database.connection import Database

    failures = 0

    for run in range(10):
        # 重置
        Database._instance = None
        db = Database()
        db.data = {}

        from services.account_service import AccountService
        service = AccountService()
        service.create_account("X", 1000.0)
        service.create_account("Y", 1000.0)

        # 并发转账
        threads = []
        for _ in range(20):
            t = threading.Thread(target=lambda: service.transfer("X", "Y", 50))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # 检查总额
        total = service.get_balance("X") + service.get_balance("Y")
        if total != 2000:
            failures += 1

    # 如果有任何一次失败，说明有竞态条件
    if failures > 0:
        print(f"FAIL: {failures}/10 runs had integrity violations")
        return False

    return True

if __name__ == "__main__":
    try:
        # 优先检测是否有锁保护
        if not test_has_lock_protection():
            print("FAIL")
            sys.exit(1)

        # 基本功能测试
        if not test_concurrent_transfers_basic():
            print("FAIL")
            sys.exit(1)

        # 并发完整性测试
        if not test_concurrent_integrity():
            print("FAIL")
            sys.exit(1)

        print("PASS")
        sys.exit(0)
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)
