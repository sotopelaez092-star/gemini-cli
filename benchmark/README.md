# Gemini CLI 跨文件 Bug 修复基准测试

这是一个用于测试 AI 代码助手修复跨文件 Bug 能力的基准测试套件。

## 测试用例概览

| 编号 | Bug 类型                            | 难度      | 涉及文件数 |
| ---- | ----------------------------------- | --------- | ---------- |
| 01   | 循环导入 (Circular Import)          | Medium    | 2          |
| 02   | 接口签名不匹配 (Interface Mismatch) | Medium    | 3          |
| 03   | 竞态条件 (Race Condition)           | Hard      | 3          |
| 04   | 事件时序错误 (Event Timing)         | Hard      | 4          |
| 05   | 继承链断裂 (Inheritance Break)      | Medium    | 4          |
| 06   | 配置字段名不匹配 (Config Mismatch)  | Medium    | 4          |
| 07   | 异步回调顺序 (Async Callback Order) | Hard      | 3          |
| 08   | 装饰器状态/服务注册顺序             | Very Hard | 5          |

## 使用方法

### 1. 验证测试用例

首先验证所有测试用例的 bug 确实存在：

```bash
python run_benchmark.py --verify-only
```

预期输出：所有用例都显示 "✗ FAIL (bug exists)"

### 2. 运行基准测试

```bash
# 使用默认的 gemini 命令
python run_benchmark.py

# 指定 gemini 路径
python run_benchmark.py --gemini-path /path/to/gemini

# 多次运行每个用例（获取更稳定的统计数据）
python run_benchmark.py --runs 3

# 设置超时时间（秒）
python run_benchmark.py --timeout 600
```

### 3. 查看结果

结果会保存在 `results/` 目录下，JSON 格式，包含：

- 总体成功率
- 每个难度级别的成功率
- 每个用例的详细结果（耗时、输出等）

## 测试用例详情

### Case 01: 循环导入

```
order_service.py ←→ user_service.py
两个服务互相导入，导致 ImportError
```

**修复方式**: 延迟导入或重构依赖

### Case 02: 接口签名不匹配

```
User model 新增了 role 字段
但 UserService.create_user() 没有更新
UserAPI 尝试传递 role 参数但失败
```

**修复方式**: 更新函数签名，传递新字段

### Case 03: 竞态条件

```
AccountService.transfer() 存在读-改-写的竞态条件
并发转账时可能导致数据不一致
```

**修复方式**: 添加 threading.Lock 保护

### Case 04: 事件时序错误

```
OrderService 先发布事件，后保存数据
NotificationService 收到事件时查询数据库，但数据还没保存
```

**修复方式**: 先保存数据，再发布事件

### Case 05: 继承链断裂

```
JsonHandler.__init__() 没有调用 super().__init__()
导致父类的属性没有初始化
```

**修复方式**: 添加 super().**init**(config) 调用

### Case 06: 配置字段名不匹配

```
DatabaseConfig.url → connection_string (改名了)
CacheConfig.password → auth_token (改名了)
但使用这些配置的代码还在用旧名字
```

**修复方式**: 更新代码中的字段名引用

### Case 07: 异步回调顺序

```
TaskQueue.process() 在任务执行前就触发了回调
回调期望 task.status == "completed"，但此时还是 "pending"
```

**修复方式**: 在任务完成后再触发回调

### Case 08: 装饰器状态/服务注册顺序

```
@service 装饰器在类定义时立即创建实例
UserService 依赖 LoggerService
但导入顺序导致 UserService 先被实例化
```

**修复方式**:

1. 修改导入顺序（简单）
2. 延迟实例化（更好）

## 评估指标

1. **成功率** - 修复后测试是否通过
2. **修复时间** - 从开始到测试通过的时间
3. **按难度分层** - 不同难度的成功率

## 注意事项

- 每次测试会自动备份和恢复测试用例
- 竞态条件测试使用静态代码分析（检测是否有锁）
- 超时默认 5 分钟，可调整
