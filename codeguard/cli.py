import json

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from codeguard.reviewer import PRReviewer

app = typer.Typer(help="CodeGuard — PR 风险雷达 Review 助手")
console = Console()


def _risk_color(level: str) -> str:
    return {
        "critical": "red",
        "high": "red",
        "medium": "yellow",
        "low": "dim",
    }.get(level, "white")


@app.command("review")
def review_cmd(
    pr_url: str = typer.Argument(..., help="GitHub PR URL"),
    json_out: bool = typer.Option(False, "--json", help="输出 JSON"),
) -> None:
    """分析 GitHub PR，生成风险雷达与 Review 路线图。"""
    try:
        pr_ctx, result = PRReviewer().review(pr_url)
    except Exception as exc:
        console.print(f"[red]错误:[/red] {exc}")
        raise typer.Exit(1) from exc

    if json_out:
        console.print(
            json.dumps(
                {
                    "pr": {
                        "url": pr_ctx.url,
                        "title": pr_ctx.title,
                        "author": pr_ctx.author,
                        "changed_files": pr_ctx.changed_files,
                        "additions": pr_ctx.additions,
                        "deletions": pr_ctx.deletions,
                    },
                    "review": result.model_dump(),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    r = result.radar
    console.print(Panel(f"[bold]{pr_ctx.title}[/bold]\n{pr_ctx.url}", title="PR"))
    console.print(
        Panel(
            f"[bold]风险评分[/bold] {r.risk_score}/100  |  "
            f"变更规模 {r.change_scale}  |  "
            f"[red]阻塞合并 {r.blocking_count}[/red]  |  "
            f"结论 {result.overall_verdict}\n"
            f"[dim]{r.top_focus_hint}[/dim]",
            title="风险雷达",
        )
    )
    console.print(Markdown(f"### 变更摘要\n{result.summary}"))
    console.print(Markdown(f"### 影响范围\n{result.impact_scope}"))
    if r.affected_modules:
        console.print(f"**影响模块:** {', '.join(r.affected_modules)}")

    if result.review_route:
        route = Table(title="Review 路线图（建议顺序）")
        route.add_column("#")
        route.add_column("文件")
        route.add_column("风险")
        route.add_column("原因")
        for step in result.review_route[:5]:
            route.add_row(
                str(step.order),
                step.file,
                f"[{_risk_color(step.risk_level)}]{step.risk_level}[/]",
                step.reason,
            )
        console.print(route)

    if result.file_rankings:
        rank = Table(title="高风险文件排行")
        rank.add_column("文件")
        rank.add_column("分数")
        rank.add_column("说明")
        for fr in result.file_rankings[:8]:
            rank.add_row(fr.file, str(fr.risk_score), fr.reason)
        console.print(rank)

    if result.blocking_issues:
        block = Table(title="阻塞合并问题")
        block.add_column("文件")
        block.add_column("问题")
        for b in result.blocking_issues:
            block.add_row(
                b.file,
                f"[bold]{b.title}[/bold]\n{b.description}\n[dim]证据: {b.evidence[:120]}…[/dim]",
            )
        console.print(block)

    if result.risk_findings:
        findings = Table(title="风险发现（含证据）")
        findings.add_column("级别")
        findings.add_column("文件")
        findings.add_column("说明")
        for f in result.risk_findings[:10]:
            findings.add_row(
                f.severity,
                f.file,
                f"{f.description}\n[dim]证据: {f.evidence[:100]}…[/dim]",
            )
        console.print(findings)

    if result.optional_comments:
        opt = Table(title="可选 Review Comment（非阻塞）")
        opt.add_column("文件")
        opt.add_column("建议")
        for c in result.optional_comments:
            opt.add_row(c.file, c.comment)
        console.print(opt)

    console.print(f"\n[dim]{result.confidence_note}[/dim]")


@app.command("serve")
def serve_cmd(
    host: str = typer.Option("127.0.0.1", help="监听地址"),
    port: int = typer.Option(8000, help="端口"),
    reload: bool = typer.Option(True, help="热重载"),
) -> None:
    """启动 Web 风险雷达界面。"""
    import uvicorn

    uvicorn.run("codeguard.api:app", host=host, port=port, reload=reload)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
