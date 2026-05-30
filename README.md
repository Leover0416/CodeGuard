# CodeGuard — PR 风险雷达 · AI Review 助手

> 编程比赛题目三：不是评论轰炸，而是帮 Reviewer **在 5 分钟内找到 PR 里最该看的 3 个地方**。

## 产品定位

传统 AI Review 容易生成大量低价值评论。CodeGuard 输出 **Review 决策面板**：

- **PR 风险评分**（0–100）与变更规模
- **Review 路线图** — 建议先看哪些文件、为什么
- **高风险文件排行**
- **阻塞合并问题**（带 diff 证据链）
- **可选 Review Comment**（默认收起，控制噪音）

## 功能一览

| 能力 | 说明 |
|------|------|
| 变更摘要 | 2–4 句话概括 PR 目的 |
| 风险雷达 | 评分、规模、影响模块、阻塞数量 |
| Review 路线 | 有序 3–5 步，突出 Top 3 |
| 证据链 | 每条风险/阻塞项引用 diff 原文 |
| 团队规则 | `rules/default.md` 可自定义 |

## 快速开始

```bash
cd "CodeGuard Ai"   # 或 clone: Leover0416/CodeGuard
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pip install -e .
cp .env.example .env
# 填入 GITHUB_TOKEN、OPENAI_API_KEY
```

### Web 演示（录视频推荐）

```bash
uvicorn codeguard.api:app --reload --port 8000
# http://127.0.0.1:8000
```

### CLI

```bash
codeguard review "https://github.com/owner/repo/pull/123"
codeguard review "https://github.com/owner/repo/pull/123" --json
```

## 配置

| 变量 | 说明 |
|------|------|
| `GITHUB_TOKEN` | 避免 API 限流 |
| `OPENAI_API_KEY` | LLM 密钥 |
| `OPENAI_BASE_URL` | 兼容 DeepSeek 等 |
| `OPENAI_MODEL` | 默认 `gpt-4o-mini` |
| `RULES_PATH` | 团队规则 Markdown 路径，默认识别 `rules/default.md` |

## 架构

```
PR URL → GitHub API (diff)
      → 启发式敏感路径提示 + 团队 rules
      → LLM 结构化 JSON（雷达 / 路线 / 证据）
      → 后处理补全指标
      → Web 决策面板 / CLI
```

设计说明：[docs/DESIGN.md](docs/DESIGN.md)

## 仓库结构

```
codeguard/
  heuristics.py   # 变更规模 & 敏感路径预估
  postprocess.py  # 雷达指标补全
  rules.py        # 团队规则加载
rules/default.md  # 可编辑 Review 规范
web/              # 风险雷达 UI
```

## 比赛提交

- 公开仓库：[github.com/Leover0416/CodeGuard](https://github.com/Leover0416/CodeGuard)
- 持续 commit / PR，避免最后一天一次性上传
- Demo 视频建议：展示雷达分 → 路线图 Top3 → 展开阻塞项与证据

## 依赖

FastAPI、httpx、Pydantic、Typer、Rich、Uvicorn — 详见 README 历史版本与 `pyproject.toml`。

## License

MIT
