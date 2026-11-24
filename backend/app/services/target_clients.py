from __future__ import annotations
import asyncio
from dataclasses import dataclass
from typing import Any
import httpx
from app.core.config import settings
from app.core.redaction import redact_text
from app.core.url_safety import validate_target_url
from app.services.llm_clients import LLMResponse, MockLLMClient
from app.services.providers.base import ProviderOptions
from app.services.providers.provider_registry import get_provider
@dataclass(frozen=True)
class TargetConfig:
    id: str
    name: str
    type: str
    endpoint_url: str | None = None
    safe_mode: bool = False
    config: dict[str, Any] | None = None
class TargetClient:
    def __init__(self): self.mock=MockLLMClient()
    def send_prompt(self, target: TargetConfig, prompt: str) -> LLMResponse:
        if len(prompt)>settings.max_prompt_chars: return LLMResponse("",0,0,"target",None,"prompt_too_large")
        cfg=target.config or {}
        if target.type in {"mock_llm","local_vulnerable_chatbot","local_rag_demo","local_agent_demo"}:
            provider_name=cfg.get("provider","mock")
            if provider_name=="mock": return self.mock.complete(prompt=prompt, safe_mode=target.safe_mode)
            result=asyncio.run(get_provider(provider_name).generate([{"role":"user","content":prompt}], ProviderOptions(model=cfg.get("model"), temperature=float(cfg.get("temperature",0.0)), max_output_tokens=int(cfg.get("max_output_tokens",512)), timeout_seconds=float(cfg.get("timeout_seconds",settings.scan_timeout_seconds)), safe_mode=target.safe_mode)))
            return LLMResponse(result.text,result.latency_ms,result.input_tokens_estimate+result.output_tokens_estimate,result.provider,result.model,result.error)
        if target.type=="custom_http" and target.endpoint_url:
            safety=validate_target_url(target.endpoint_url, allow_private=settings.enable_demo_targets)
            if not safety.allowed: return LLMResponse("",0,0,"custom_http",None,"endpoint_blocked")
            try:
                with httpx.Client(timeout=settings.scan_timeout_seconds) as client:
                    r=client.post(target.endpoint_url, json={"prompt":prompt}, headers={"X-LLMShield-Authorized-Test":"true"})
                    r.raise_for_status()
                    content=r.content
                    if len(content) > settings.max_response_bytes:
                        return LLMResponse("",0,0,"custom_http",None,"response_too_large")
                    data=r.json() if "application/json" in r.headers.get("content-type","") else {"text":content.decode(errors="replace")}
                    text=str(data.get("response") or data.get("text") or "").strip()
                    if not text:
                        return LLMResponse("",0,0,"custom_http",None,"empty_response")
                    return LLMResponse(redact_text(text), int(r.elapsed.total_seconds()*1000), len(prompt.split())+len(text.split()), "custom_http")
            except Exception as exc:
                return LLMResponse("",0,0,"custom_http",None,f"request_failed: {redact_text(str(exc))[:160]}")
        raise ValueError(f"Unsupported or incomplete target configuration: {target.type}")
