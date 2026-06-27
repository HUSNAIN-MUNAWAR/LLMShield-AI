from __future__ import annotations
import time
from typing import Any
from app.core.config import settings
from app.core.redaction import redact_text
from app.services.providers.base import ProviderOptions, ProviderResponse
class OpenAIProvider:
    name = "openai"
    def __init__(self, api_key: str | None = None, model: str | None = None, client: Any | None = None):
        self.api_key = api_key if api_key is not None else settings.openai_api_key
        self.model = model or settings.openai_model
        self._client = client
    async def health(self) -> dict[str, Any]:
        return {"provider": self.name, "configured": bool(self.api_key), "healthy": bool(self.api_key), "status": "configured" if self.api_key else "missing_api_key", "message": "configured" if self.api_key else "OPENAI_API_KEY is not configured", "model": self.model}
    async def generate(self, messages: list[dict[str,str]], options: ProviderOptions) -> ProviderResponse:
        if not self.api_key:
            return ProviderResponse(text="", provider=self.name, model=self.model, error="OPENAI_API_KEY is not configured.")
        start=time.perf_counter()
        try:
            client = self._client
            if client is None:
                from openai import AsyncOpenAI
                client = AsyncOpenAI(api_key=self.api_key, timeout=options.timeout_seconds)
            response = await client.chat.completions.create(model=options.model or self.model, messages=messages, temperature=options.temperature, max_tokens=options.max_output_tokens)
            text = response.choices[0].message.content or ""
            usage = getattr(response, "usage", None)
            return ProviderResponse(text=text, raw_response={"id": getattr(response,"id",None)}, latency_ms=int((time.perf_counter()-start)*1000), input_tokens_estimate=int(getattr(usage,"prompt_tokens",0) or sum(len(m.get("content","").split()) for m in messages)), output_tokens_estimate=int(getattr(usage,"completion_tokens",0) or len(text.split())), model=options.model or self.model, provider=self.name)
        except Exception as exc:
            return ProviderResponse(text="", provider=self.name, model=options.model or self.model, latency_ms=int((time.perf_counter()-start)*1000), error=redact_text(str(exc)))
