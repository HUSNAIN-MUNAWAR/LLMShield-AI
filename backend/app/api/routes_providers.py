from __future__ import annotations
from fastapi import APIRouter
from app.services.providers.provider_registry import get_provider, provider_names
router=APIRouter(prefix="/providers", tags=["providers"])
@router.get("")
async def list_providers():
    return [await get_provider(n).health() for n in provider_names()]
@router.get("/{provider_name}/health")
async def provider_health(provider_name: str):
    return await get_provider(provider_name).health()
@router.post("/{provider_name}/test")
async def test_provider(provider_name: str):
    return await get_provider(provider_name).health()
