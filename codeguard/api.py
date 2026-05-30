from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from codeguard.reviewer import PRReviewer

WEB_DIR = Path(__file__).resolve().parent.parent / "web"

app = FastAPI(
    title="CodeGuard AI",
    description="GitHub PR 智能 Code Review 助手",
    version="0.1.0",
)


class ReviewRequest(BaseModel):
    pr_url: str = Field(..., examples=["https://github.com/owner/repo/pull/1"])


class ReviewResponse(BaseModel):
    pr_title: str
    pr_url: str
    author: str
    changed_files: int
    additions: int
    deletions: int
    review: dict


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    html = (WEB_DIR / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(html)


@app.post("/api/review", response_model=ReviewResponse)
def api_review(body: ReviewRequest) -> ReviewResponse:
    try:
        pr_ctx, result = PRReviewer().review(body.pr_url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return ReviewResponse(
        pr_title=pr_ctx.title,
        pr_url=pr_ctx.url,
        author=pr_ctx.author,
        changed_files=pr_ctx.changed_files,
        additions=pr_ctx.additions,
        deletions=pr_ctx.deletions,
        review=result.model_dump(),
    )


if WEB_DIR.exists():
    app.mount("/static", StaticFiles(directory=WEB_DIR / "static"), name="static")
