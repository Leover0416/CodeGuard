import json

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from codeguard.reviewer import PRReviewer

app = typer.Typer(help="CodeGuard AI — GitHub PR 智能 Review 助手")
console = Console()


@app.command()
def review(
    pr_url: str = typer.Argument(..., help="GitHub PR URL"),
    json_out: bool = typer.Option(False, "--json", help="输出 JSON"),
) -> None:
    """分析指定 GitHub PR 并生成 Review 报告。"""
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
                    },
                    "review": result.model_dump(),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    console.print(Panel(f"[bold]{pr_ctx.title}[/bold]\n{pr_ctx.url}", title="PR"))
    console.print(Markdown(f"### 变更摘要\n{result.summary}"))
    console.print(Markdown(f"### 影响范围\n{result.impact_scope}"))
    console.print(
        f"\n**总体建议:** {result.overall_verdict}  |  {result.confidence_note}\n"
    )

    if result.risks:
        risk_table = Table(title="风险项")
        risk_table.add_column("严重度")
        risk_table.add_column("文件")
        risk_table.add_column("类别")
        risk_table.add_column("说明")
        for r in result.risks:
            risk_table.add_row(
                r.severity,
                r.file,
                r.category,
                f"{r.description}\n[dim]{r.suggestion}[/dim]",
            )
        console.print(risk_table)

    if result.suggestions:
        sug_table = Table(title="Review 建议")
        sug_table.add_column("优先级")
        sug_table.add_column("文件")
        sug_table.add_column("评论")
        for s in result.suggestions:
            sug_table.add_row(s.priority, s.file, s.comment)
        console.print(sug_table)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
