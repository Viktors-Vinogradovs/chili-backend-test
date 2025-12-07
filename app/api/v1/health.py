from fastapi import APIRouter
from app.core.jsend import jsend_success
from app.schemas.responses import MessageResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "/",
    summary="Health check",
    description="Returns OK if the service is running. Use for liveness probes.",
    response_model=MessageResponse,
)
def health_check():
    return jsend_success({"message": "OK"})
