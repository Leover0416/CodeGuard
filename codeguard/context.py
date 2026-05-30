from codeguard.config import settings
from codeguard.models import PRContext


def build_review_context(pr: PRContext) -> str:
    """将 PR 元数据与 diff 拼装为 LLM 可消费的上下文，并做长度预算。"""
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
            f"\n> 按变更量排序后省略了 {omitted} 个较小改动的文件（可在配置中调高 MAX_FILES_IN_CONTEXT）"
        )

    return "\n".join(lines)
