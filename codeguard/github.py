import re
from urllib.parse import urlparse

import httpx

from codeguard.config import settings
from codeguard.models import FileChange, PRContext, PRRef

PR_URL_RE = re.compile(
    r"github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/pull/(?P<number>\d+)",
    re.IGNORECASE,
)


def parse_pr_url(url: str) -> PRRef:
    match = PR_URL_RE.search(url.strip())
    if not match:
        raise ValueError(
            "无法解析 PR 链接，请使用格式: https://github.com/owner/repo/pull/123"
        )
    return PRRef(
        owner=match.group("owner"),
        repo=match.group("repo"),
        number=int(match.group("number")),
    )


def _headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "CodeGuard-AI/0.1",
    }
    if settings.has_github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"
    return headers


class GitHubClient:
    def __init__(self) -> None:
        self._client = httpx.Client(
            base_url="https://api.github.com",
            headers=_headers(),
            timeout=60.0,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "GitHubClient":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def fetch_pr_context(self, ref: PRRef, *, pr_url: str) -> PRContext:
        pr = self._get_json(f"/repos/{ref.owner}/{ref.repo}/pulls/{ref.number}")
        files = self._fetch_all_files(ref)

        return PRContext(
            url=pr_url,
            title=pr.get("title") or "",
            body=pr.get("body") or "",
            author=(pr.get("user") or {}).get("login") or "unknown",
            base_branch=(pr.get("base") or {}).get("ref") or "",
            head_branch=(pr.get("head") or {}).get("ref") or "",
            changed_files=pr.get("changed_files") or len(files),
            additions=pr.get("additions") or 0,
            deletions=pr.get("deletions") or 0,
            files=files,
        )

    def _fetch_all_files(self, ref: PRRef) -> list[FileChange]:
        files: list[FileChange] = []
        page = 1
        while True:
            batch = self._get_json(
                f"/repos/{ref.owner}/{ref.repo}/pulls/{ref.number}/files",
                params={"per_page": 100, "page": page},
            )
            if not batch:
                break
            for item in batch:
                files.append(
                    FileChange(
                        filename=item.get("filename") or "",
                        status=item.get("status") or "modified",
                        additions=item.get("additions") or 0,
                        deletions=item.get("deletions") or 0,
                        patch=item.get("patch"),
                    )
                )
            if len(batch) < 100:
                break
            page += 1
        return files

    def _get_json(self, path: str, params: dict | None = None) -> object:
        resp = self._client.get(path, params=params)
        if resp.status_code == 403 and "rate limit" in resp.text.lower():
            raise RuntimeError(
                "GitHub API 速率受限。请配置 GITHUB_TOKEN 后重试。"
            )
        resp.raise_for_status()
        return resp.json()


def normalize_pr_input(value: str) -> tuple[PRRef, str]:
    value = value.strip()
    if value.isdigit():
        raise ValueError("请提供完整 PR URL，例如 https://github.com/owner/repo/pull/1")
    if "github.com" in value:
        ref = parse_pr_url(value)
        return ref, value
    # owner/repo#123 or owner/repo/pull/123
    m = re.match(r"(?P<owner>[^/]+)/(?P<repo>[^#/\s]+)#(?P<num>\d+)", value)
    if m:
        url = f"https://github.com/{m.group('owner')}/{m.group('repo')}/pull/{m.group('num')}"
        return parse_pr_url(url), url
    raise ValueError("无法识别的 PR 输入格式")
