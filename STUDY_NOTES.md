# Gemini CLI 架构深度解析 - 学习笔记

## 一、项目整体架构

```
gemini-cli/
├── packages/
│   ├── cli/          # 前端 UI 层 (React + Ink)
│   ├── core/         # 核心业务逻辑层
│   ├── a2a-server/   # Agent-to-Agent 服务器
│   └── vscode-ide-companion/  # VS Code 集成
```

### 核心设计理念
- **关注点分离**: CLI 负责交互，Core 负责逻辑
- **依赖注入**: 通过 Config 对象传递依赖
- **策略模式**: 路由、工具执行等都采用策略模式

---

## 二、三层记忆机制 (与你设计的短期/中期/长期记忆对应)

### 2.1 记忆层级结构

| 层级 | 名称 | 位置 | 加载时机 | 对应你的设计 |
|------|------|------|----------|--------------|
| Tier 1 | Global Memory | `~/.gemini/GEMINI.md` | 会话启动时 | **长期记忆** |
| Tier 2 | Environment Memory | 项目根目录 `GEMINI.md` | 会话启动时 | **中期记忆** |
| Tier 3 | JIT Memory | 子目录 `GEMINI.md` | 访问路径时即时加载 | **短期/上下文记忆** |

### 2.2 核心实现代码解析

```typescript
// packages/core/src/services/contextManager.ts

export class ContextManager {
  private readonly loadedPaths: Set<string> = new Set();  // 防止重复加载
  private globalMemory: string = '';      // Tier 1
  private environmentMemory: string = ''; // Tier 2

  // Tier 1: 全局长期记忆
  async loadGlobalMemory(): Promise<string> {
    const result = await loadGlobalMemory(this.config.getDebugMode());
    this.markAsLoaded(result.files.map((f) => f.path));
    // ...
  }

  // Tier 2: 环境/项目级记忆
  async loadEnvironmentMemory(trustedRoots, extensionLoader): Promise<string> {
    const result = await loadEnvironmentMemory(trustedRoots, extensionLoader, ...);
    // ...
  }

  // Tier 3: JIT (Just-In-Time) 即时加载 - 关键创新！
  async discoverContext(accessedPath, trustedRoots): Promise<string> {
    // 当工具访问某个路径时，向上遍历查找 GEMINI.md
    const result = await loadJitSubdirectoryMemory(
      accessedPath,
      trustedRoots,
      this.loadedPaths,  // 避免重复加载已经加载过的
      ...
    );
    // ...
  }
}
```

### 2.3 记忆发现机制亮点

```typescript
// packages/core/src/utils/memoryDiscovery.ts

// 向上遍历查找 GEMINI.md 文件
async function findUpwardGeminiFiles(startDir, stopDir, debugMode): Promise<string[]> {
  const upwardPaths: string[] = [];
  let currentDir = path.resolve(startDir);

  while (true) {
    // 跳过全局 .gemini 目录 (避免重复)
    if (currentDir === globalGeminiDir) break;

    // 并行检查所有配置的文件名变体
    const accessChecks = geminiMdFilenames.map(async (filename) => {
      const potentialPath = path.join(currentDir, filename);
      try {
        await fs.access(potentialPath, fsSync.constants.R_OK);
        return potentialPath;
      } catch { return null; }
    });

    const foundPathsInDir = (await Promise.all(accessChecks))
      .filter((p) => p !== null);
    upwardPaths.unshift(...foundPathsInDir);  // 注意: unshift 保证顺序

    if (currentDir === resolvedStopDir || currentDir === path.dirname(currentDir)) {
      break;
    }
    currentDir = path.dirname(currentDir);
  }
  return upwardPaths;
}
```

### 2.4 MemoryTool - 主动记忆存储

```typescript
// packages/core/src/tools/memoryTool.ts

// 将事实追加到全局记忆文件的指定 section
function computeNewContent(currentContent: string, fact: string): string {
  const headerIndex = currentContent.indexOf(MEMORY_SECTION_HEADER);

  if (headerIndex === -1) {
    // 添加新的 section header
    return currentContent + `${separator}${MEMORY_SECTION_HEADER}\n${newMemoryItem}\n`;
  } else {
    // 在现有 section 末尾追加
    sectionContent += `\n${newMemoryItem}`;
    return `${beforeSectionMarker}\n${sectionContent.trimStart()}\n${afterSectionMarker}`;
  }
}
```

---

## 三、智能上下文压缩策略

### 3.1 压缩触发条件

```typescript
// packages/core/src/services/chatCompressionService.ts

export const DEFAULT_COMPRESSION_TOKEN_THRESHOLD = 0.5;  // 50% token limit
export const COMPRESSION_PRESERVE_THRESHOLD = 0.3;       // 保留最后 30%

async compress(chat, promptId, force, model, config, hasFailedAttempt) {
  const originalTokenCount = chat.getLastPromptTokenCount();

  // 自动压缩: 当 token 使用超过阈值时触发
  if (!force) {
    const threshold = await config.getCompressionThreshold() ?? 0.5;
    if (originalTokenCount < threshold * tokenLimit(model)) {
      return { newHistory: null, info: { compressionStatus: CompressionStatus.NOOP }};
    }
  }
  // ...
}
```

### 3.2 压缩切分点算法

```typescript
// 关键：找到合适的切分点，保证不会在函数调用中间切断

export function findCompressSplitPoint(contents: Content[], fraction: number): number {
  const charCounts = contents.map((c) => JSON.stringify(c).length);
  const totalCharCount = charCounts.reduce((a, b) => a + b, 0);
  const targetCharCount = totalCharCount * fraction;  // 要压缩的目标字符数

  let lastSplitPoint = 0;
  let cumulativeCharCount = 0;

  for (let i = 0; i < contents.length; i++) {
    const content = contents[i];

    // 只在用户消息处切分，且不能在 functionResponse 处切
    if (content.role === 'user' &&
        !content.parts?.some((part) => !!part.functionResponse)) {
      if (cumulativeCharCount >= targetCharCount) {
        return i;  // 找到切分点
      }
      lastSplitPoint = i;
    }
    cumulativeCharCount += charCounts[i];
  }

  // 边界情况处理...
  return lastSplitPoint;
}
```

### 3.3 压缩提示词模板 - XML 结构化摘要

```typescript
// packages/core/src/core/prompts.ts

export function getCompressionPrompt(): string {
  return `
You are the component that summarizes internal chat history into a given structure.

First, you will think through the entire history in a private <scratchpad>...

<state_snapshot>
    <overall_goal>
        <!-- 用户的高层目标 -->
    </overall_goal>

    <key_knowledge>
        <!-- 关键事实、约定、约束 -->
        <!-- - Build Command: \`npm run build\` -->
    </key_knowledge>

    <file_system_state>
        <!-- 文件操作记录 -->
        <!-- - CWD: \`/home/user/project\` -->
        <!-- - MODIFIED: \`src/auth.ts\` -->
    </file_system_state>

    <recent_actions>
        <!-- 最近的重要操作和结果 -->
    </recent_actions>

    <current_plan>
        <!-- 执行计划，标记完成状态 -->
        <!-- 1. [DONE] 识别所有使用旧 API 的文件 -->
        <!-- 2. [IN PROGRESS] 重构 UserProfile.tsx -->
    </current_plan>
</state_snapshot>
`.trim();
}
```

---

## 四、工具系统设计模式

### 4.1 工具抽象层次

```
DeclarativeTool (抽象基类)
    │
    ├── build(params) → ToolInvocation  // 验证参数，创建调用实例
    │
    └── BaseDeclarativeTool
            │
            ├── validateToolParams()     // JSON Schema 验证
            ├── validateToolParamValues() // 业务逻辑验证
            └── createInvocation()       // 创建具体调用实例

ToolInvocation (调用实例)
    ├── getDescription()              // 操作描述
    ├── toolLocations()               // 影响的文件路径
    ├── shouldConfirmExecute()        // 是否需要用户确认
    └── execute(signal, updateOutput) // 执行工具
```

### 4.2 工具确认流程 (Policy Engine)

```typescript
// packages/core/src/tools/tools.ts

async shouldConfirmExecute(abortSignal): Promise<ConfirmationDetails | false> {
  if (this.messageBus) {
    const decision = await this.getMessageBusDecision(abortSignal);

    switch (decision) {
      case 'ALLOW':  return false;              // 直接执行
      case 'DENY':   throw new Error('denied'); // 拒绝执行
      case 'ASK_USER': return this.getConfirmationDetails(abortSignal); // 询问用户
    }
  }
  return this.getConfirmationDetails(abortSignal);
}
```

### 4.3 工具类型分类

```typescript
export enum Kind {
  Read = 'read',      // 只读操作
  Edit = 'edit',      // 编辑文件
  Delete = 'delete',  // 删除操作
  Move = 'move',      // 移动操作
  Search = 'search',  // 搜索操作
  Execute = 'execute', // Shell 执行
  Think = 'think',    // 思考/记忆
  Fetch = 'fetch',    // 网络请求
  Other = 'other',
}

// 有副作用的操作类型
export const MUTATOR_KINDS: Kind[] = [Kind.Edit, Kind.Delete, Kind.Move, Kind.Execute];
```

---

## 五、Agent 子代理系统

### 5.1 Agent 执行器架构

```typescript
// packages/core/src/agents/executor.ts

class AgentExecutor<TOutput extends z.ZodTypeAny> {
  // 核心执行循环
  async run(inputs: AgentInputs, signal: AbortSignal): Promise<OutputObject> {
    while (true) {
      // 1. 检查终止条件
      const reason = this.checkTermination(startTime, turnCounter);
      if (reason) break;

      // 2. 执行单个回合
      const turnResult = await this.executeTurn(chat, currentMessage, ...);

      // 3. 处理回合结果
      if (turnResult.status === 'stop') {
        terminateReason = turnResult.terminateReason;
        break;
      }
      currentMessage = turnResult.nextMessage;
    }

    // 4. 恢复逻辑：超时/达到最大回合时给予最后机会
    if (needsRecovery) {
      const recoveryResult = await this.executeFinalWarningTurn(...);
      // ...
    }
  }
}
```

### 5.2 Agent 定义结构

```typescript
interface AgentDefinition<TOutput> {
  name: string;

  modelConfig: { model: string; };

  promptConfig: {
    systemPrompt?: string;
    query?: string;
    initialMessages?: Content[];
  };

  toolConfig?: {
    tools: (string | FunctionDeclaration | DeclarativeTool)[];
  };

  runConfig: {
    max_turns: number;
    max_time_minutes: number;
  };

  outputConfig?: {
    outputName: string;
    schema: z.ZodTypeAny;
  };

  processOutput?: (output: z.infer<TOutput>) => string;
}
```

### 5.3 完成任务的强制机制

```typescript
const TASK_COMPLETE_TOOL_NAME = 'complete_task';

// Agent 必须调用 complete_task 才能正常结束
// 如果模型停止调用工具但没有 complete_task，视为错误
if (functionCalls.length === 0) {
  return {
    status: 'stop',
    terminateReason: AgentTerminateMode.ERROR_NO_COMPLETE_TASK_CALL,
    finalResult: null,
  };
}
```

---

## 六、路由策略模式

### 6.1 策略接口

```typescript
// packages/core/src/routing/routingStrategy.ts

interface RoutingStrategy {
  readonly name: string;

  route(
    context: RoutingContext,
    config: Config,
    baseLlmClient: BaseLlmClient,
  ): Promise<RoutingDecision | null>;  // 返回 null 表示不适用
}

// 终端策略：必须返回决策，不能返回 null
interface TerminalStrategy extends RoutingStrategy {
  route(...): Promise<RoutingDecision>;  // 注意：不是 | null
}
```

### 6.2 组合策略 (责任链模式)

```typescript
// packages/core/src/routing/strategies/compositeStrategy.ts

class CompositeStrategy implements TerminalStrategy {
  // 策略列表，最后一个必须是 TerminalStrategy
  private strategies: [...RoutingStrategy[], TerminalStrategy];

  async route(context, config, baseLlmClient): Promise<RoutingDecision> {
    // 依次尝试非终端策略
    for (const strategy of nonTerminalStrategies) {
      try {
        const decision = await strategy.route(context, config, baseLlmClient);
        if (decision) {
          return this.finalizeDecision(decision, startTime);
        }
      } catch (error) {
        // 策略失败时继续下一个
        console.error(`Strategy '${strategy.name}' failed. Continuing...`);
      }
    }

    // 最终执行终端策略（保证返回结果）
    return await terminalStrategy.route(context, config, baseLlmClient);
  }
}
```

### 6.3 现有策略实现

| 策略 | 职责 |
|------|------|
| `OverrideStrategy` | 用户手动指定模型时生效 |
| `FallbackStrategy` | 降级模式时切换到备用模型 |
| `ClassifierStrategy` | 根据任务类型选择最优模型 |
| `DefaultStrategy` | 默认模型选择（终端策略） |

---

## 七、值得学习的设计亮点

### 7.1 消息总线模式

```typescript
// 解耦工具确认流程
interface MessageBus {
  publish(message: ToolConfirmationRequest): Promise<void>;
  subscribe(type: MessageBusType, handler: (msg) => void): void;
  unsubscribe(type: MessageBusType, handler): void;
}

// 工具执行请求确认
const request: ToolConfirmationRequest = {
  type: MessageBusType.TOOL_CONFIRMATION_REQUEST,
  toolCall: { name: 'shell', args: { command: 'rm -rf ...' } },
  correlationId: randomUUID(),
};
```

### 7.2 Hook 系统

```typescript
// 生命周期钩子
enum PreCompressTrigger {
  Manual = 'manual',  // 用户手动触发
  Auto = 'auto',      // 自动触发
}

// 压缩前触发钩子
if (hooksEnabled && messageBus) {
  await firePreCompressHook(messageBus, trigger);
}
```

### 7.3 流式输出处理

```typescript
// Agent 执行时的活动回调
const onActivity = (activity: SubagentActivityEvent): void => {
  if (activity.type === 'THOUGHT_CHUNK') {
    updateOutput(`🤖💭 ${activity.data['text']}`);
  }
};
```

---

## 八、对比你的三层记忆设计

| 特性 | 你的设计 | Gemini CLI |
|------|----------|------------|
| 短期记忆 | 当前会话上下文 | JIT Memory (Tier 3) + Chat History |
| 中期记忆 | 项目相关知识 | Environment Memory (Tier 2) |
| 长期记忆 | 跨项目的用户偏好 | Global Memory (Tier 1) |
| 压缩策略 | ? | XML 结构化摘要 + 保留最后 30% |
| 加载时机 | ? | 启动时 + JIT (访问时) |
| 防重复 | ? | `loadedPaths: Set<string>` |

**Gemini CLI 的创新点**：
1. **JIT 加载**：只在访问特定目录时才加载该目录的上下文，减少初始化开销
2. **向上遍历**：从访问路径向上查找，自动继承父目录的上下文
3. **结构化压缩**：使用 XML 格式保留关键信息的结构

---

## 九、推荐的学习路径

1. **入口点**: `packages/cli/src/gemini.tsx` - 理解启动流程
2. **核心循环**: `packages/core/src/core/client.ts` - 理解主 Agent 循环
3. **工具系统**: `packages/core/src/tools/` - 理解工具抽象
4. **记忆机制**: `packages/core/src/utils/memoryDiscovery.ts` - 理解三层记忆
5. **压缩策略**: `packages/core/src/services/chatCompressionService.ts`
6. **子代理**: `packages/core/src/agents/executor.ts` - 理解 Agent 编排
7. **路由策略**: `packages/core/src/routing/strategies/` - 理解策略模式
