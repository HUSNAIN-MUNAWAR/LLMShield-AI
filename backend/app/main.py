from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes_api_keys, routes_attack_packs, routes_audit, routes_auth, routes_ci, routes_findings, routes_health, routes_metrics, routes_providers, routes_reports, routes_scans, routes_targets
from app.core.config import settings
from app.core.database import init_db
from app.core.logging import configure_logging
from app.core.rate_limit import BasicRateLimitMiddleware
def create_app() -> FastAPI:
    configure_logging()
    app=FastAPI(title="LLMShield AI API", version="0.2.0", description="Defensive GenAI red-teaming and LLM security evaluation API.")
    app.add_middleware(BasicRateLimitMiddleware, limit=300, window_seconds=60)
    app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins or ["http://localhost:3000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
    init_db()
    @app.on_event("startup")
    def _startup(): init_db()
    app.include_router(routes_health.router)
    app.include_router(routes_metrics.router)
    for router in [routes_auth.router,routes_api_keys.router,routes_attack_packs.router,routes_audit.router,routes_ci.router,routes_providers.router,routes_targets.router,routes_scans.router,routes_findings.router,routes_reports.router]:
        app.include_router(router, prefix=settings.api_prefix)
    return app
app=create_app()
