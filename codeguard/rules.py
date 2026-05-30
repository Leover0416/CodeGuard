from pathlib import Path

from codeguard.config import settings

RULES_DIR = Path(__file__).resolve().parent.parent / "rules"


def load_team_rules() -> str:
    path = settings.rules_path or (RULES_DIR / "default.md")
    p = Path(path)
    if not p.is_file():
        return ""
    return p.read_text(encoding="utf-8").strip()
