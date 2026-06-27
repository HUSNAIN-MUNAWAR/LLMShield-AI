from fastapi import APIRouter

router = APIRouter(prefix="/ci", tags=["ci"])


@router.post("/run")
def ci_run() -> dict[str, str]:
    return {"status": "available", "command": "python -m app.services.ci_runner --target mock-unsafe"}
