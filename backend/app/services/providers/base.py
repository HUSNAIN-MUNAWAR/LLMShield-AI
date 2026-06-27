from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Protocol
@dataclass(frozen=True)
class ProviderOptions:
    model: str | None = None
    temperature: float = 0.0
    max_output_tokens: int = 512
    timeout_seconds: float = 30.0
    safe_mode: bool = True
@dataclass(frozen=True)
class ProviderResponse:
    text: str
    raw_response: dict[str, Any] = field(default_factory=dict)
    latency_ms: int = 0
    input_tokens_estimate: int = 0
    output_tokens_estimate: int = 0
    model: str = "unknown"
    provider: str = "unknown"
    error: str | None = None
class LLMProvider(Protocol):
    name: str
    async def generate(self, messages: list[dict[str, str]], options: ProviderOptions) -> ProviderResponse: ...
    async def health(self) -> dict[str, Any]: ...
