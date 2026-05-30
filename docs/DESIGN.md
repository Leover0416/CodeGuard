# CodeGuard AI 设计说明

> 比赛提交要求：说明模型选型、上下文获取、后续扩展方向。

## 1. 模型选型

| 维度 | 选择 | 理由 |
|------|------|------|
| 默认模型 | `gpt-4o-mini`（可配置） | 成本低、速度快，适合 diff 级审查；结构化 JSON 输出稳定 |
| 接口协议 | OpenAI Chat Completions + `response_format: json_object` | 便于统一接入 OpenAI / DeepSeek / 通义 / 本地 vLLM 等兼容网关 |
| Temperature | 0.2 | 降低幻觉，减少无依据的「编造风险」 |

**升级路径**：对大型 PR 可改为「摘要模型 + 深度模型」两阶段：先用 mini 做文件级 triage，再对高风险文件用更强模型细审。

## 2. 上下文获取策略

```
用户 PR URL
    → GitHub REST API（PR 元数据 + /pulls/{id}/files 带 patch）
    → 按变更行数排序，优先保留大改动文件
    → 单文件 patch 截断 + 总上下文字符预算
    → 拼装为 Markdown（标题、描述、逐文件 diff）
    → LLM System/User Prompt
```

**设计要点**：

- **只审 diff**：不把整仓灌进模型，控制 token 与噪声。
- **PR 描述纳入上下文**：帮助理解意图，减少误报。
- **预算可配置**：`MAX_FILES_IN_CONTEXT`、`MAX_PATCH_CHARS_PER_FILE`、`MAX_TOTAL_CONTEXT_CHARS` 适配不同模型窗口。
- **GitHub Token**：匿名 60 次/小时易触限；建议配置 `GITHUB_TOKEN` 保证 demo 稳定。

**已知局限**（诚实标注，利于评委信任）：

- 二进制/超大文件 GitHub 不返回 patch，需人工补充。
- 跨文件调用链、运行时行为需结合 CI/测试报告（见扩展）。

## 3. 误报与漏报控制

- Prompt 要求：无 diff 证据不标 high/critical；不确定则降级并标注「需人工确认」。
- 结构化输出：`risks[]` 与 `suggestions[]` 分离，便于 UI 过滤。
- `overall_verdict` + `confidence_note` 显式表达把握程度。

## 4. 后续扩展

1. **仓库上下文增强**：对改动符号做 ripgrep / LSP，拉取被调用方定义。
2. **规则引擎预检**：Semgrep、Bandit、ESLint 结果作为 LLM 输入，降低幻觉。
3. **GitHub App**：在 PR 上自动评论，支持 `request_changes` 与行级 suggestion。
4. **多平台**：GitLab、Gitee API 适配同一 `Reviewer` 抽象。
5. **反馈闭环**：用户对误报点踩，微调 prompt 或训练 ranker。
6. **缓存**：同一 PR SHA 缓存报告，加快重复打开。

## 5. 第三方依赖

见根目录 `README.md`「依赖与致谢」：FastAPI、httpx、Pydantic、Typer、Rich；无复制第三方业务代码。
