import re

from codeguard.models import FileChange, PRContext

# 路径关键词 → 加权，用于辅助 LLM 前的变更规模与敏感文件提示
SENSITIVE_PATTERNS: list[tuple[re.Pattern[str], int, str]] = [
    (re.compile(r"(auth|login|password|token|secret|credential)", re.I), 25, "认证/密钥"),
    (re.compile(r"(pay|payment|order|checkout|billing)", re.I), 22, "支付/订单"),
    (re.compile(r"(stock|inventory|warehouse)", re.I), 20, "库存"),
    (re.compile(r"(migration|schema|ddl)", re.I), 18, "数据库迁移"),
    (re.compile(r"(callback|webhook)", re.I), 16, "外部回调"),
    (re.compile(r"(controller|api|route|handler)", re.I), 12, "API 入口"),
    (re.compile(r"(service|repository|dao)", re.I), 10, "业务逻辑"),
]


def classify_change_scale(pr: PRContext) -> str:
    total = pr.additions + pr.deletions
    n = pr.changed_files
    if total > 2000 or n > 40:
        return "xl"
    if total > 800 or n > 20:
        return "large"
    if total > 200 or n > 8:
        return "medium"
    return "small"


def score_file(filename: str, change: FileChange) -> tuple[int, list[str]]:
    score = min(40, (change.additions + change.deletions) // 3)
    tags: list[str] = []
    for pattern, weight, label in SENSITIVE_PATTERNS:
        if pattern.search(filename):
            score += weight
            tags.append(label)
    return min(100, score), tags


def build_heuristic_brief(pr: PRContext) -> str:
    scale = classify_change_scale(pr)
    scored: list[tuple[int, str, list[str]]] = []
    for f in pr.files:
        s, tags = score_file(f.filename, f)
        scored.append((s, f.filename, tags))
    scored.sort(reverse=True)

    lines = [
        "## 变更规模（规则预估）",
        f"- scale: {scale} (+{pr.additions}/-{pr.deletions}, {pr.changed_files} files)",
        "",
        "## 敏感路径提示（供排序参考，非最终结论）",
    ]
    for s, name, tags in scored[:12]:
        tag_str = ", ".join(tags) if tags else "常规改动"
        lines.append(f"- [{s:3d}] {name} — {tag_str}")
    if not pr.files:
        lines.append("- (无文件变更)")
    return "\n".join(lines)
