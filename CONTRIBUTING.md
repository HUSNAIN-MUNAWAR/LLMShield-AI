# Contributing

Contributions that improve defensive coverage, provider support, detection quality, reporting, documentation, or test reliability are welcome.

## Development setup

1. Fork and clone the repository.
2. Create a focused branch.
3. Install Python dependencies with `pip install -r requirements-dev.txt`.
4. Install frontend dependencies with `cd frontend && npm ci`.
5. Keep all security tests bounded to local, simulated, user-owned, or explicitly authorized targets.

## Before opening a pull request

Run the relevant checks:

```bash
python scripts/validate_project.py
python scripts/secret_scan.py
cd backend && pytest -q
cd ../frontend && npm run typecheck && npm run build
```

Include a concise description of the change, its security impact, and the validation performed. Never commit API keys, credentials, private endpoint data, or unredacted sensitive evidence.

For vulnerabilities, follow [SECURITY.md](SECURITY.md) instead of opening a public issue.
