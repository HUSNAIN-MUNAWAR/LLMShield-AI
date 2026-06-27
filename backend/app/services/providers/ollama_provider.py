from __future__ import annotations
import time
from typing import Any
import httpx
from app.core.config import settings
from app.core.redaction import redact_text
from app.services.providers.base import ProviderOptions, ProviderResponse
class OllamaProvider:
    name = "ollama"
    def __init__(self, base_url: str | None = None, model: str | None = None):
        self.base_url=(base_url or settings.ollama_base_url).rstrip("/")
        self.model=model or settings.ollama_model
    async def health(self) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                r = await client.get(f"{self.base_url}/api/tags"); r.raise_for_status(); data=r.json() if hasattr(r, "json") else {}
                return {"provider": self.name, "configured": True, "healthy": True, "status": "ok", "message": "Ollama is reachable", "model": self.model, "models": [m.get("name") for m in data.get("models",[])][:10]}
        except Exception as exc:
            return {"provider": self.name, "configured": False, "healthy": False, "status": "unreachable", "message": "Ollama is not reachable", "model": self.model, "error": redact_text(str(exc))}
    async def generate(self, messages: list[dict[str,str]], options: ProviderOptions) -> ProviderResponse:
        start=time.perf_counter(); prompt="\n".join(f"{m.get('role','user')}: {m.get('content','')}" for m in messages)
        try:
            async with httpx.AsyncClient(timeout=options.timeout_seconds) as client:
                r = await client.post(f"{self.base_url}/api/generate", json={"model": options.model or self.model, "prompt": prompt, "stream": False, "options": {"temperature": options.temperature, "num_predict": options.max_output_tokens}})
                r.raise_for_status(); data=r.json(); text=str(data.get("response",""))
                return ProviderResponse(text=text, raw_response={"done": data.get("done")}, latency_ms=int((time.perf_counter()-start)*1000), input_tokens_estimate=max(1,len(prompt.split())), output_tokens_estimate=max(1,len(text.split())), model=options.model or self.model, provider=self.name)
        except Exception as exc:
            return ProviderResponse(text="", provider=self.name, model=options.model or self.model, latency_ms=int((time.perf_counter()-start)*1000), error=redact_text(str(exc)))
