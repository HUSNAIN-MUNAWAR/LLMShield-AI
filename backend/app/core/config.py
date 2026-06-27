from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path

def _csv(name: str, default: str = "") -> list[str]:
    return [x.strip() for x in os.getenv(name, default).split(",") if x.strip()]

@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./llmshield.db")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY") or None
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1")
    enable_demo_targets: bool = os.getenv("ENABLE_DEMO_TARGETS", "true").lower() == "true"
    scan_timeout_seconds: int = int(os.getenv("SCAN_TIMEOUT_SECONDS", "30"))
    scan_execution_mode: str = os.getenv("SCAN_EXECUTION_MODE", "sync").lower()
    max_prompt_chars: int = int(os.getenv("MAX_PROMPT_CHARS", "6000"))
    max_response_bytes: int = int(os.getenv("MAX_RESPONSE_BYTES", "200000"))
    allow_private_targets: bool = os.getenv("ALLOW_PRIVATE_TARGETS", "false").lower() == "true"
    jwt_secret: str = os.getenv("JWT_SECRET", "dev-only-change-me")
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = int(os.getenv("ACCESS_TOKEN_MINUTES", "240"))
    refresh_token_minutes: int = int(os.getenv("REFRESH_TOKEN_MINUTES", "10080"))
    api_key_prefix: str = os.getenv("API_KEY_PREFIX", "lsk")
    api_prefix: str = "/api"
    project_root: Path = Path(__file__).resolve().parents[3]
    data_dir: Path = Path(__file__).resolve().parents[1] / "data"
    attack_pack_dir: Path = Path(__file__).resolve().parents[1] / "data" / "attack_packs"
    reports_dir: Path = Path(__file__).resolve().parents[1] / "data" / "reports"
    scan_logs_dir: Path = Path(__file__).resolve().parents[3] / "sample_outputs" / "jsonl"
    @property
    def endpoint_allowlist(self) -> list[str]:
        return _csv("ENDPOINT_ALLOWLIST", "localhost,127.0.0.1")
    @property
    def cors_origins(self) -> list[str]:
        return _csv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
settings = Settings()
