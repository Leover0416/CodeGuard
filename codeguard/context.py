from codeguard.config import settings
from codeguard.heuristics import build_heuristic_brief
from codeguard.models import PRContext
from codeguard.rules import load_team_rules


def build_review_context(pr: PRContext) -> tuple[str, str, str]:
    """返回 (主上下文, 团队规则段, 启发式段) 供 prompt 拼装。"""
    lines: list[str] = [
        "# Pull Request",
        f"URL: {pr.url}",
        f"Title: {pr.title}",
        f"Author: {pr.author}",
        f"Branch: {pr.head_branch} -> {pr.base_branch}",
        f"Stats: +{pr.additions} -{pr.deletions}, {pr.changed_files} files",
        "",
        "## Description",
        pr.body.strip() or "(无 PR 描述)",
        "",
        "## File Changes",
    ]

    files = sorted(
        pr.files,
        key=lambda f: (f.additions + f.deletions),
        reverse=True,
    )[: settings.max_files_in_context]

    total_chars = 0
    for f in files:
        patch = f.patch or "(binary or large file — patch omitted by GitHub)"
        if len(patch) > settings.max_patch_chars_per_file:
            patch = (
                patch[: settings.max_patch_chars_per_file]
                + "\n... [patch truncated] ..."
            )

        block = (
            f"\n### {f.filename} ({f.status}, +{f.additions}/-{f.deletions})\n"
            f"```diff\n{patch}\n```\n"
        )
        if total_chars + len(block) > settings.max_total_context_chars:
            lines.append(
                f"\n... 另有 {len(pr.files) - len(files)} 个文件因上下文长度限制未包含 ..."
            )
            break
        lines.append(block)
        total_chars += len(block)

    if len(pr.files) > len(files):
        omitted = len(pr.files) - len(files)
        lines.append(
            f"\n> 按变更量排序后省略了 {omitted} 个较小改动的文件"
        )

    main_ctx = "\n".join(lines)
    rules = load_team_rules()
    rules_section = (
        "## 团队 Review 规则\n" + rules if rules else "(未配置团队规则文件)"
    )
    heuristic_section = build_heuristic_brief(pr)
    return main_ctx, rules_section, heuristic_section
