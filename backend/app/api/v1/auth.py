from fastapi import APIRouter, HTTPException
from app.services.browser_service import capture_auth

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/capture")
async def capture():
    try:
        result = await capture_auth()
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
