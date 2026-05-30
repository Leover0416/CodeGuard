from codeguard.heuristics import classify_change_scale, score_file
from codeguard.models import (
    BlockingIssue,
    FileRanking,
    PRContext,
    ReviewResult,
    ReviewRouteStep,
)


def enrich_review_result(pr: PRContext, result: ReviewResult) -> ReviewResult:
    """合并规则预估、补全雷达指标与 Review 路线。"""
    scale = classify_change_scale(pr)
    if result.radar.change_scale not in ("small", "medium", "large", "xl"):
        result.radar.change_scale = scale
    elif result.radar.change_scale == "small" and scale in ("medium", "large", "xl"):
        result.radar.change_scale = scale

    result.radar.blocking_count = len(result.blocking_issues)

    if not result.file_rankings and pr.files:
        result.file_rankings = _rankings_from_heuristics(pr)

    if not result.review_route:
        result.review_route = _route_from_rankings(result.file_rankings)

    if result.radar.risk_score <= 0:
        result.radar.risk_score = _aggregate_risk_score(result)

    if not result.radar.affected_modules and pr.files:
        result.radar.affected_modules = _infer_modules(pr)

    return result


def _rankings_from_heuristics(pr: PRContext) -> list[FileRanking]:
    items: list[FileRanking] = []
    for f in pr.files:
        score, tags = score_file(f.filename, f)
        level = _score_to_level(score)
        reason = f"变更 +{f.additions}/-{f.deletions}"
        if tags:
            reason += f"；涉及 {', '.join(tags)}"
        items.append(
            FileRanking(file=f.filename, risk_score=score, risk_level=level, reason=reason)
        )
    items.sort(key=lambda x: x.risk_score, reverse=True)
    return items[:10]


def _route_from_rankings(rankings: list[FileRanking]) -> list[ReviewRouteStep]:
    steps: list[ReviewRouteStep] = []
    for i, r in enumerate(rankings[:5], start=1):
        steps.append(
            ReviewRouteStep(
                order=i,
                file=r.file,
                reason=r.reason,
                risk_level=r.risk_level,
            )
        )
    return steps


def _aggregate_risk_score(result: ReviewResult) -> int:
    if result.file_rankings:
        top = sum(r.risk_score for r in result.file_rankings[:3]) / 3
    else:
        top = 30
    block_boost = min(30, len(result.blocking_issues) * 12)
    critical = sum(1 for f in result.risk_findings if f.severity in ("critical", "high"))
    finding_boost = min(25, critical * 8)
    return int(min(100, top * 0.6 + block_boost + finding_boost))


def _score_to_level(score: int) -> str:
    if score >= 75:
        return "critical"
    if score >= 55:
        return "high"
    if score >= 35:
        return "medium"
    return "low"


def _infer_modules(pr: PRContext) -> list[str]:
    modules: set[str] = set()
    for f in pr.files:
        parts = f.filename.replace("\\", "/").split("/")
        if len(parts) >= 2:
            modules.add(parts[0])
        elif parts:
            modules.add(parts[0])
    return sorted(modules)[:8]
