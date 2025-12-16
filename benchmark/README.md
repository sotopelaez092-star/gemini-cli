# Gemini CLI Cross-File Python Debug Benchmark

测试 Gemini CLI 对 Python 跨文件错误的修复能力。

## 支持的错误类型

| 错误类型 | 描述 | 难度 |
|---------|------|-----|
| `name_error` | 跨文件符号拼写错误 | Easy-Medium |
| `import_error` | 模块路径错误 | Medium |
| `attribute_error` | 类方法/属性名拼写错误 | Easy-Medium |
| `type_error` | 函数参数不匹配 | Medium |
| `key_error` | 字典字段名错误 | Easy |
| `circular_import` | A→B→A 循环导入 | Hard |

## 快速开始

```bash
cd benchmark

# 运行所有测试
./run.sh

# 只测试特定错误类型
./run.sh --error-type name_error

# 并行运行（注意：可能影响 API 限流）
./run.sh --parallel 2

# 自定义超时时间
./run.sh --timeout 180
```

## 目录结构

```
benchmark/
├── test_cases/
│   ├── name_error/
│   │   ├── case_01/
│   │   │   ├── main.py          # 包含错误的入口文件
│   │   │   ├── utils.py         # 被引用的模块
│   │   │   └── metadata.json    # 测试用例元数据
│   │   └── case_02/
│   ├── import_error/
│   ├── attribute_error/
│   ├── type_error/
│   ├── key_error/
│   └── circular_import/
├── results/
│   ├── results_YYYYMMDD_HHMMSS.json    # 详细结果
│   ├── summary_YYYYMMDD_HHMMSS.json    # 统计摘要
│   └── workspaces/                      # 测试工作目录
├── scripts/
│   ├── run_benchmark.py         # 主测试脚本
│   └── analyze_results.py       # 结果分析脚本
├── run.sh                       # 快捷运行脚本
└── README.md
```

## 添加新测试用例

1. 在对应错误类型目录创建新 case 目录：

```bash
mkdir -p test_cases/name_error/case_03
```

2. 创建测试文件（确保跨文件依赖）：

```python
# main.py - 包含错误
from utils import calculat_total  # 故意拼错
result = calculat_total([1,2,3])
```

```python
# utils.py - 正确的实现
def calculate_total(numbers):
    return sum(numbers)
```

3. 添加 metadata.json：

```json
{
  "error_type": "NameError",
  "case_id": "name_error_03",
  "description": "描述这个测试用例",
  "error_file": "main.py",
  "error_message": "预期的错误消息",
  "expected_fix": "预期的修复方式",
  "difficulty": "easy|medium|hard"
}
```

## 输出指标

| 指标 | 说明 |
|-----|------|
| `success_rate` | 修复成功率 (%) |
| `avg_duration_ms` | 平均修复时间 (ms) |
| `avg_tokens` | 平均 token 消耗 |
| `tool_calls` | 工具调用次数 |

## 分析结果

```bash
# 查看最新结果的详细分析
python scripts/analyze_results.py --results-dir ./results

# 对比多次运行
python scripts/analyze_results.py --results-dir ./results --compare

# 生成 Markdown 报告
python scripts/analyze_results.py --results-dir ./results --markdown report.md
```

## 示例输出

```
======================================
BENCHMARK SUMMARY
======================================
Total Cases: 8
Passed: 6
Failed: 2
Success Rate: 75.0%
Average Duration: 15234ms
Average Tokens: 12500

By Error Type:
--------------------------------------
  NameError:
    Success Rate: 100.0% (2/2)
    Avg Duration: 8500ms
    Avg Tokens: 8000
  ImportError:
    Success Rate: 100.0% (1/1)
    Avg Duration: 12000ms
    Avg Tokens: 10000
  CircularImport:
    Success Rate: 0.0% (0/1)
    Avg Duration: 35000ms
    Avg Tokens: 25000
======================================
```

## 注意事项

1. **API 限流**：并行运行可能触发 API 限流，建议 `--parallel 1`
2. **超时设置**：复杂错误（如循环导入）可能需要更长时间
3. **工作目录**：每次测试会复制测试用例到 `results/workspaces/`
4. **代理设置**：如需代理，在运行前设置环境变量：
   ```bash
   export https_proxy=http://127.0.0.1:7890
   ./run.sh
   ```
