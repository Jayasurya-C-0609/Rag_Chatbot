from fastapi import APIRouter, Depends
from backend.api.dependencies import get_system_service
from backend.services.system_service import SystemService

router = APIRouter(prefix="/health", tags=["health"])

@router.get("")
def health_check():
    return {"status": "ok"}

@router.get("/ready")
def readiness_check(system: SystemService = Depends(get_system_service)):
    ready = system.retriever is not None
    if ready:
        return {"status": "ready"}
    return {"status": "initializing"}
