from fastapi import APIRouter

router = APIRouter()


@router.get("/api/Health")
async def health():
    return {"Status": "ok"}
