# CodeGuard 设计说明（v0.2 风险雷达）

## 1. 模型选型

| 选择 | 理由 |
|------|------|
| 默认 `gpt-4o-mini` | 速度快、成本低，适合结构化 JSON |
| OpenAI 兼容 API | 可切换 DeepSeek / 通义 / 本地网关 |
| `temperature=0.2` + `json_object` | 降低幻觉，便于解析雷达 schema |

升级：大 PR 可对 Top3 文件二次调用更强模型细审。

## 2. 上下文获取

1. **GitHub PR API**：元数据 + `/files` patch（主证据源）
2. **启发式 brief**：按路径关键词（支付/库存/auth 等）与改动行数排序，辅助 LLM 排优先级（非最终结论）
3. **团队 rules**：`rules/default.md` 注入 prompt，落地规范检查
4. **长度预算**：文件数 / 单 patch / 总字符可配置

**证据链**：Prompt 强制 `evidence` 引用 diff；UI 单独展示证据块。

**暂未实现（扩展）**：全仓调用链、历史 PR、CI 日志 — 见 §4。

## 3. 误报控制

- 先路线后细节：默认突出 Top3，阻塞与可选评论分区
- `optional_comments` 上限 5 条
- 无证据不标 high/critical；不确定标注「需人工确认」
- `blocking_issues` 与 `optional_comments` 分离

## 4. 后续扩展

- 符号级调用链 / LSP
- Semgrep 等静态结果并入上下文
- GitHub App 自动行内评论
- 用户反馈闭环调优 prompt

## 5. 第三方依赖

FastAPI、httpx、Pydantic、Typer、Rich — 业务与 Prompt 原创。
