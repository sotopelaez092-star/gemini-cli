"""测试用例 - 验证循环导入是否修复"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_import():
    """测试是否能正常导入"""
    try:
        from services.order_service import OrderService
        from services.user_service import UserService
        return True
    except ImportError as e:
        print(f"Import Error: {e}")
        return False

def test_functionality():
    """测试功能是否正常"""
    from services.order_service import OrderService
    from services.user_service import UserService

    user_service = UserService()
    order_service = OrderService()

    # 测试获取用户
    user = user_service.get_user(1)
    assert user["id"] == 1

    # 测试创建订单
    order = order_service.create_order(1, 100, 2)
    assert order["user_id"] == 1

    # 测试获取用户及订单
    user_with_orders = user_service.get_user_with_orders(1)
    assert "orders" in user_with_orders

    return True

if __name__ == "__main__":
    if test_import() and test_functionality():
        print("PASS")
        sys.exit(0)
    else:
        print("FAIL")
        sys.exit(1)
