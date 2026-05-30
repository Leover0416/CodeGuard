# CodeGuard AI — GitHub PR 智能 Review 助手

> 编程比赛题目三：输入 GitHub PR，自动产出变更摘要、风险识别与 Review 建议。

## 功能

- 解析 GitHub PR 链接，拉取 PR 描述与文件级 diff
- **变更摘要**与影响范围说明
- **风险代码识别**（安全 / Bug / 性能 / 可维护性等，带严重度）
- **Review 建议**（可直接贴到 PR 的评论文案）
- 总体结论：`approve` / `comment` / `request_changes`

提供 **Web 界面**（录 demo 用）与 **CLI** 两种使用方式。

## 快速开始

### 1. 环境要求

- Python 3.11+
- [GitHub Personal Access Token](https://github.com/settings/tokens)（建议 `public_repo` 或 `repo`）
- OpenAI 兼容 API Key（OpenAI / DeepSeek / 其他网关）

### 2. 安装

```bash
cd "CodeGuard Ai"
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
cp .env.example .env
# 编辑 .env 填入 GITHUB_TOKEN 与 OPENAI_API_KEY
```

### 3. Web 演示（推荐录视频）

```bash
uvicorn codeguard.api:app --reload --host 0.0.0.0 --port 8000
```

浏览器打开 http://127.0.0.1:8000 ，粘贴 PR 链接后点击「开始 Review」。

### 4. 命令行

```bash
codeguard review "https://github.com/psf/requests/pull/1"
codeguard review "https://github.com/psf/requests/pull/1" --json
```

## 配置说明

| 变量 | 说明 |
|------|------|
| `GITHUB_TOKEN` | GitHub API 认证，避免速率限制 |
| `OPENAI_API_KEY` | LLM API 密钥 |
| `OPENAI_BASE_URL` | 兼容接口地址，默认 OpenAI 官方 |
| `OPENAI_MODEL` | 模型名，默认 `gpt-4o-mini` |
| `MAX_FILES_IN_CONTEXT` | 送入模型的最大文件数 |
| `MAX_PATCH_CHARS_PER_FILE` | 单文件 patch 字符上限 |
| `MAX_TOTAL_CONTEXT_CHARS` | 总上下文字符上限 |

## 架构

```
PR URL → GitHub API (metadata + files patch)
       → Context Builder (排序 + 截断)
       → LLM (JSON structured review)
       → Web / CLI 展示
```

详细设计见 [docs/DESIGN.md](docs/DESIGN.md)（模型选型、上下文策略、扩展方向）。

## 项目结构

```
codeguard/          # 核心逻辑
  github.py         # PR 拉取
  context.py        # 上下文拼装
  llm.py            # LLM 调用
  reviewer.py       # 编排
  api.py            # FastAPI
  cli.py            # Typer CLI
web/                # 前端静态页
docs/DESIGN.md      # 比赛设计说明
```

## Demo 视频建议脚本

1. 展示 README 与 `.env` 配置（打码 Key）
2. 启动 `uvicorn`，打开首页
3. 粘贴一个真实开源 PR 链接（建议选改动适中、有讨论价值的）
4. 展示摘要、风险、建议与总体结论
5. 可选：演示 CLI `--json` 输出

## 依赖与致谢

本项目为比赛期间原创实现，主要依赖：

| 库 | 用途 | 协议 |
|----|------|------|
| [FastAPI](https://fastapi.tiangolo.com/) | HTTP API | MIT |
| [httpx](https://www.python-httpx.org/) | HTTP 客户端 | BSD |
| [Pydantic](https://docs.pydantic.dev/) | 数据校验 | MIT |
| [Typer](https://typer.tiangolo.com/) | CLI | MIT |
| [Rich](https://rich.readthedocs.io/) | 终端美化 | MIT |
| [Uvicorn](https://www.uvicorn.org/) | ASGI 服务器 | BSD |

业务逻辑与 Prompt 均为本项目自行编写，未拷贝第三方 Review 产品代码。

## 比赛提交提醒

- 请在题目放出后 **24 小时内** 将本仓库公开链接填入表单
- 开发过程中请 **持续 commit / PR**，避免最后一天一次性上传
- 每个 PR 请写清改动说明；若复用以往代码片段，在 PR 中注明来源

## License

MIT
