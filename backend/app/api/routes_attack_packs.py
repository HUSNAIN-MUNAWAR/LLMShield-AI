from fastapi import APIRouter

from app.services.attack_pack_loader import AttackPackLoader

router = APIRouter(prefix="/attack-packs", tags=["attack-packs"])


@router.get("")
def list_attack_packs() -> list[dict]:
    return AttackPackLoader().summaries()
