"""测试用例 - 验证接口不匹配是否修复"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_create_user():
    """测试创建用户"""
    from api.user_api import UserAPI

    api = UserAPI()
    result = api.register_user({
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "role": "admin"
    })
    assert result["status"] == "success"
    return True

def test_user_has_role():
    """测试用户是否有 role 字段"""
    from api.user_api import UserAPI

    api = UserAPI()
    api.register_user({
        "id": 2,
        "username": "admin",
        "email": "admin@example.com",
        "role": "admin"
    })

    user_info = api.get_user_info(2)
    assert user_info["role"] == "admin", f"Expected role 'admin', got {user_info.get('role')}"
    return True

if __name__ == "__main__":
    try:
        if test_create_user() and test_user_has_role():
            print("PASS")
            sys.exit(0)
    except Exception as e:
        print(f"FAIL: {e}")
        sys.exit(1)
