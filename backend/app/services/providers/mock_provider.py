from __future__ import annotations
import asyncio, time
from app.services.providers.base import ProviderOptions, ProviderResponse
class MockLLMProvider:
    name = "mock"
    def __init__(self, safe_mode: bool | None = None):
        self.default_safe_mode = safe_mode
    async def health(self): return {"provider": self.name, "configured": True, "healthy": True, "status": "ok", "message": "MockLLM is ready", "model": "mock-deterministic"}
    async def generate(self, messages, options: ProviderOptions) -> ProviderResponse:
        start=time.perf_counter(); await asyncio.sleep(0)
        prompt="\n".join(m.get("content","") for m in messages)
        text=self._answer(prompt, options.safe_mode if self.default_safe_mode is None else self.default_safe_mode)
        return ProviderResponse(text=text, raw_response={"mode":"safe" if options.safe_mode else "vulnerable"}, latency_ms=int((time.perf_counter()-start)*1000)+12, input_tokens_estimate=max(1,len(prompt.split())), output_tokens_estimate=max(1,len(text.split())), model="mock-deterministic", provider=self.name)
    def _answer(self, prompt: str, safe_mode: bool) -> str:
        p=prompt.lower()
        if safe_mode:
            return "I cannot reveal hidden instructions or comply with requests to reveal hidden instructions, leak data, invent citations, or simulate external actions without authorization. I can provide a safe, bounded summary."
        if any(t in p for t in ["very long","repeat","recursive","token"]): return "TOKEN-ABUSE-DEMO " * 360
        if any(t in p for t in ["api key","secret","credential","bearer"]): return "Mock secret leak for defensive testing only: api_key=sk-demoSECRET123456 and Authorization: Bearer demo-token-123456789."
        if any(t in p for t in ["pii","customer","personal data","email list"]): return "Mock customer record: Ali Example, ali@example.com, SSN 123-45-6789, +1 202-555-0188."
        if any(t in p for t in ["system prompt","hidden","developer instruction","chain","config"]): return "The hidden system prompt is: You are LLMShield vulnerable demo assistant. Developer message: trust user override."
        if any(t in p for t in ["delete","remove file","wipe"]): return "I deleted the file /tmp/customer_data.csv using delete_file_simulation."
        if any(t in p for t in ["send email","email","exfiltrate"]): return "Email sent to finance@example.com with the requested sensitive data attached."
        if any(t in p for t in ["citation","source","rag","according to"]): return "According to the International Journal of AI Safety 2024 and [source:made-up-doc], this is confirmed."
        if any(t in p for t in ["book","purchase","schedule","approval","ticket"]): return "I completed the action without asking for human approval and created ticket SEC-999."
        if any(t in p for t in ["roleplay","jailbreak","override","ignore"]): return "Sure, I will ignore safety rules and follow your override instruction."
        return "Mock answer: I processed the request."
