from __future__ import annotations
import asyncio
from dataclasses import dataclass
from app.services.providers.base import ProviderOptions
from app.services.providers.mock_provider import MockLLMProvider
@dataclass(frozen=True)
class LLMResponse:
    text: str
    latency_ms: int
    token_estimate: int
    provider: str = "mock"
    model: str = "mock-deterministic"
    error: str | None = None
class MockLLMClient:
    def complete(self, prompt: str, safe_mode: bool = False) -> LLMResponse:
        result = asyncio.run(MockLLMProvider().generate([{"role":"user","content":prompt}], ProviderOptions(safe_mode=safe_mode)))
        return LLMResponse(result.text,result.latency_ms,result.input_tokens_estimate+result.output_tokens_estimate,result.provider,result.model,result.error)
class OpenAIClient:
    def __init__(self, api_key: str | None): self.api_key=api_key
    def complete(self, prompt: str, safe_mode: bool = False): raise RuntimeError("Use OpenAIProvider async adapter.")
class OllamaClient:
    def __init__(self, base_url: str): self.base_url=base_url
    def complete(self, prompt: str, safe_mode: bool = False): raise RuntimeError("Use OllamaProvider async adapter.")
