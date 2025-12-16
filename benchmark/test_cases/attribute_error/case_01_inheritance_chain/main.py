# Case 01: Method typo in inheritance chain
# Difficulty: Hard
# Need to trace through multiple inheritance levels to find correct method name

from models.admin_user import AdminUser

def main():
    admin = AdminUser("admin", "admin@example.com", "superadmin")
    # Error: 'get_permsissions' has typo, should be 'get_permissions'
    # Method is defined in base class (BaseUser), need to trace inheritance
    perms = admin.get_permsissions()
    print(f"Permissions: {perms}")

if __name__ == "__main__":
    main()
