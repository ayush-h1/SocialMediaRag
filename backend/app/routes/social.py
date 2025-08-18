from fastapi import APIRouter, Query
from ..services.youtube import search_youtube
from ..services.reddit import search_reddit  # keep if you have it
# from ..services.twitter import search_twitter  # optional

router = APIRouter(prefix="", tags=["search"])

@router.get("/search")
def search(q: str = Query(..., min_length=1, max_length=200)):
    """
    Aggregated search. Provider errors never fail the whole request.
    """
    results = {"youtube": [], "reddit": [], "twitter": []}

    try:
        results["youtube"] = search_youtube(q)
    except Exception as e:
        print(f"[search] youtube failed: {e}")

    try:
        results["reddit"] = search_reddit(q)
    except Exception as e:
        print(f"[search] reddit failed: {e}")

    # try:
    #     results["twitter"] = search_twitter(q)
    # except Exception as e:
    #     print(f"[search] twitter failed: {e}")

    return results
