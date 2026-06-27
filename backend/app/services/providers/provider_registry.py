from __future__ import annotations
from app.services.providers.mock_provider import MockLLMProvider
from app.services.providers.openai_provider import OpenAIProvider
from app.services.providers.ollama_provider import OllamaProvider
def get_provider(name: str | None = None):
    n=(name or "mock").lower()
    if n in {"mock","mockllm","mock_llm"}: return MockLLMProvider()
    if n=="openai": return OpenAIProvider()
    if n=="ollama": return OllamaProvider()
    raise ValueError(f"Unsupported provider: {name}")
def provider_names() -> list[str]: return ["mock","openai","ollama"]
