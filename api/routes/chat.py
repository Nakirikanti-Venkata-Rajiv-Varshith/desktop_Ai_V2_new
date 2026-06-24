from fastapi import APIRouter

router = APIRouter()

@router.post("/chat")
def chat(
    query: str
):
    return {
        "message": query
    }