from pydantic import BaseModel, Field


class PRRef(BaseModel):
    owner: str
    repo: str
    number: int


class FileChange(BaseModel):
    filename: str
    status: str
    additions: int = 0
    deletions: int = 0
    patch: str | None = None


class PRContext(BaseModel):
    url: str
    title: str
    body: str
    author: str
    base_branch: str
    head_branch: str
    changed_files: int
    additions: int
    deletions: int
    files: list[FileChange]


class RiskItem(BaseModel):
    severity: str = Field(description="critical | high | medium | low")
    file: str
    line_hint: str = ""
    category: str = Field(description="security | bug | performance | maintainability | other")
    description: str
    suggestion: str


class ReviewSuggestion(BaseModel):
    file: str
    line_hint: str = ""
    comment: str
    priority: str = Field(default="normal", description="must_fix | should_fix | nice_to_have")


class ReviewResult(BaseModel):
    summary: str
    impact_scope: str
    risks: list[RiskItem]
    suggestions: list[ReviewSuggestion]
    overall_verdict: str = Field(description="approve | comment | request_changes")
    confidence_note: str = ""
