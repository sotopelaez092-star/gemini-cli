# Services package
# Bug: 导入顺序会影响服务注册顺序
# user_service 依赖 logger_service，但导入顺序可能不对

from services.user_service import UserService
from services.logger_service import LoggerService
