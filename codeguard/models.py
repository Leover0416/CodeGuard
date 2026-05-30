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


class RadarDashboard(BaseModel):
    """PR 风险雷达决策面板核心指标。"""

    risk_score: int = Field(ge=0, le=100, description="0-100，越高越需优先 Review")
    change_scale: str = Field(description="small | medium | large | xl")
    affected_modules: list[str] = Field(default_factory=list)
    blocking_count: int = 0
    top_focus_hint: str = Field(
        default="优先关注 Review 路线图中的前 3 个文件",
        description="帮助 Reviewer 快速定位的提示",
    )


class FileRanking(BaseModel):
    file: str
    risk_score: int = Field(ge=0, le=100)
    risk_level: str = Field(description="critical | high | medium | low")
    reason: str


class ReviewRouteStep(BaseModel):
    order: int = Field(ge=1)
    file: str
    reason: str
    risk_level: str = Field(description="critical | high | medium | low")


class RiskFinding(BaseModel):
    severity: str = Field(description="critical | high | medium | low")
    file: str
    line_hint: str = ""
    category: str = Field(
        description="security | bug | performance | maintainability | concurrency | other"
    )
    description: str
    evidence: str = Field(description="必须引用 diff 中的原文片段作为依据")
    suggestion: str
    blocks_merge: bool = False


class BlockingIssue(BaseModel):
    file: str
    line_hint: str = ""
    title: str
    description: str
    evidence: str
    fix_suggestion: str


class OptionalComment(BaseModel):
    file: str
    line_hint: str = ""
    comment: str
    evidence: str = ""
    priority: str = Field(default="nice_to_have", description="should_fix | nice_to_have")


class ReviewResult(BaseModel):
    summary: str
    impact_scope: str
    radar: RadarDashboard
    file_rankings: list[FileRanking] = Field(default_factory=list)
    review_route: list[ReviewRouteStep] = Field(default_factory=list)
    risk_findings: list[RiskFinding] = Field(default_factory=list)
    blocking_issues: list[BlockingIssue] = Field(default_factory=list)
    optional_comments: list[OptionalComment] = Field(default_factory=list)
    overall_verdict: str = Field(description="approve | comment | request_changes")
    confidence_note: str = ""
