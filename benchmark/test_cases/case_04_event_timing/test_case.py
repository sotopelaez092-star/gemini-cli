"""测试用例 - 验证事件时序问题是否修复"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def reset_singletons():
    """重置单例"""
    from events.event_bus import EventBus
    from repository.order_repository import OrderRepository
    EventBus._instance = None
    OrderRepository._instance = None
    OrderRepository._orders = {}

def test_order_creation_with_notification():
    """
    测试创建订单时通知服务能正确处理

    预期: 创建订单后，通知服务能查到订单并发送通知
    Bug: 事件在订单保存前发布，通知服务查不到订单
    """
    reset_singletons()

    from services.notification_service import NotificationService
    from services.order_service import OrderService

    # 先初始化通知服务（设置监听器）
    notification_service = NotificationService()

    # 创建订单服务
    order_service = OrderService()

    # 创建订单 - 这里会触发事件
    order = order_service.create_order(user_id=1, product_id=100, quantity=2)

    # 验证通知是否发送
    notifications = notification_service.get_notifications()
    assert len(notifications) == 1, f"Expected 1 notification, got {len(notifications)}"
    assert notifications[0]["order_id"] == order["id"]

    return True

if __name__ == "__main__":
    try:
        if test_order_creation_with_notification():
            print("PASS")
            sys.exit(0)
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)
