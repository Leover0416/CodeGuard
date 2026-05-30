from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    github_token: str = ""
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"

    max_files_in_context: int = 30
    max_patch_chars_per_file: int = 8000
    max_total_context_chars: int = 120000

    @property
    def has_github_token(self) -> bool:
        return bool(self.github_token.strip())


settings = Settings()
