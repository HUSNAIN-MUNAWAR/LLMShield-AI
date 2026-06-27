# Security Boundaries

LLMShield AI is for defensive, authorized GenAI security evaluation only.

Allowed targets:

- MockLLM provider
- local vulnerable demo apps included in this repository
- local Ollama server controlled by the user
- OpenAI account explicitly configured by the user for testing their own prompts/apps
- custom HTTP endpoints that the user owns or has written permission to test and that pass the allowlist/SSRF checks

Not allowed by project design:

- public-target scanning
- credential theft
- phishing
- malware or exploit deployment
- attempts to bypass real production security controls
- destructive actions against real systems

The platform intentionally uses simulated prompts, fake agent tools, local demos, and redaction controls. It does not guarantee LLM security and does not replace professional penetration testing.
