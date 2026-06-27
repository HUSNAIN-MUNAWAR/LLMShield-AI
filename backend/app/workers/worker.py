from __future__ import annotations
from app.core.config import settings

def main():
    try:
        from redis import Redis  # type: ignore
        from rq import Worker, Queue  # type: ignore
    except Exception as exc:
        raise SystemExit(f"Redis/RQ dependencies are required for async worker mode: {exc}")
    redis=Redis.from_url(settings.redis_url)
    worker=Worker([Queue("llmshield-scans", connection=redis)], connection=redis)
    worker.work()

if __name__ == "__main__":
    main()
