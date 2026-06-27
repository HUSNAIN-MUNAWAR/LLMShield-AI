# Production Hardening Checklist

Before using LLMShield AI beyond a local evaluation environment:

- Deploy only behind HTTPS.
- Disable demo login and rotate all demo credentials.
- Set a strong `JWT_SECRET` and rotate it periodically.
- Use managed Postgres and Redis with backups enabled.
- Set strict `CORS_ORIGINS`.
- Configure `ENDPOINT_ALLOWLIST` for user-owned endpoints only.
- Keep SSRF protections enabled.
- Keep request timeout, prompt size, and response size limits enabled.
- Enable redaction in logs, JSONL scan artifacts, reports, and frontend views.
- Decide whether raw prompts/responses may be stored under your data policy.
- Configure audit log retention and export policy.
- Run `python scripts/secret_scan.py` before every push.
- Run `python scripts/run_all_checks.py` before releases.
- Run Docker smoke tests before deployment.
- Run provider smoke tests only with approved keys/local providers.
- Add SSO/OIDC before enterprise use.
- Add dependency/security scanning in your real CI/CD platform.
- Review attack packs for your internal policies before use.
