from fastapi import APIRouter, Query

router = APIRouter(tags=["search"])

@router.get("/search")
def search(q: str = Query(...)):
    return {"ok": True, "q": q}

