from fastapi import APIRouter

router = APIRouter(tags=["core"])

@router.get("/")
def root():
    return {"message": "Chatbox API is running ok!", "version": "1.0.0"}

@router.get("/healthz")
def healthz():
    return {"status": "ok"}