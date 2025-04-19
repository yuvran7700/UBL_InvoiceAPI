# src/routes/health_routes.py

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse


router = APIRouter(prefix="/health", tags=["Health Checks"])

@router.get("/live")
async def liveness_check():
    """
    Always returns 'alive' if the FastAPI process is running.
    Prevents orchestrator from restarting container during startup.
    """
    return {"status": "alive"}

@router.get("/ready")
async def readiness_check(request: Request):
    """
    Returns 'ready' only when all required resources are initialized.
    """

    health_service = request.app.state.health_service
    status = health_service.get_status()


    # If any subsystem is not ready, return 503 with detailed message
    if status["status"] != "ready":
        return JSONResponse(status_code=503, content=status)

    return status
