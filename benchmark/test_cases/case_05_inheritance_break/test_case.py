"""测试用例 - 验证继承链断裂是否修复"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_json_handler_initialization():
    """
    测试 JsonHandler 的初始化

    预期: JsonHandler 应该能正常初始化并调用 is_ready()
    Bug: 由于没有调用 super().__init__()，_initialized 属性不存在
    """
    from handlers.json_handler import JsonHandler

    handler = JsonHandler({"indent": 4})
    handler.initialize()

    # 这里会失败，因为 _initialized 属性不存在
    assert handler.is_ready() == True, "Handler should be ready after initialization"
    return True

def test_json_handler_processing():
    """测试 JsonHandler 的处理功能"""
    from handlers.json_handler import JsonHandler

    handler = JsonHandler({"indent": 2})
    handler.initialize()

    data = {"name": "test", "value": 123}
    result = handler.handle(data)

    assert isinstance(result, str)
    assert "name" in result
    assert "test" in result
    return True

def test_csv_handler_works():
    """确认 CsvHandler 正常工作（作为对比）"""
    from handlers.csv_handler import CsvHandler

    handler = CsvHandler({"delimiter": ","})
    handler.initialize()

    assert handler.is_ready() == True

    data = {"name": "test", "value": "123"}
    result = handler.handle(data)
    assert "test" in result
    return True

if __name__ == "__main__":
    try:
        tests = [
            test_csv_handler_works,
            test_json_handler_initialization,
            test_json_handler_processing,
        ]

        for test in tests:
            test()
            print(f"{test.__name__}: OK")

        print("PASS")
        sys.exit(0)
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)
