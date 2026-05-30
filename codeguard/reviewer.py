from codeguard.context import build_review_context
from codeguard.github import GitHubClient, normalize_pr_input
from codeguard.llm import LLMClient, parse_review_result
from codeguard.models import PRContext, ReviewResult
from codeguard.postprocess import enrich_review_result
from codeguard.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


class PRReviewer:
    def review(self, pr_input: str) -> tuple[PRContext, ReviewResult]:
        ref, url = normalize_pr_input(pr_input)

        with GitHubClient() as gh:
            pr_ctx = gh.fetch_pr_context(ref, pr_url=url)

        main_ctx, rules_section, heuristic_section = build_review_context(pr_ctx)
        user_prompt = USER_PROMPT_TEMPLATE.format(
            context=main_ctx,
            team_rules_section=rules_section,
            heuristic_section=heuristic_section,
        )

        with LLMClient() as llm:
            raw = llm.complete_json(SYSTEM_PROMPT, user_prompt)

        result = parse_review_result(raw)
        result = enrich_review_result(pr_ctx, result)
        return pr_ctx, result
