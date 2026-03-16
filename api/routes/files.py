from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from api.services.file_service import FileService, get_file_service
from db.database import get_db
from db.models import UserRecord
from utils.auth import get_current_user

router = APIRouter(prefix="/files", tags=["files"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    current_user: UserRecord = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service),
    db: Session = Depends(get_db),
):
    """Upload a file. Stored under files/{user_id}/ and record metadata in DB."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    record = await file_service.store_and_record(
        file=file,
        user_id=current_user.id,
        db=db,
    )

    return {
        "id": record.id,
        "original_name": record.original_name,
        "random_name": record.random_name,
        "content_type": record.content_type,
        "size": record.size,
        "user_id": record.user_id,
        "created_at": record.created_at,
        "path": record.path,
    }


@router.get("/search")
async def search_files(
    text: str,
    current_user: UserRecord = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service),
    db: Session = Depends(get_db),
):
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query 'text' is required",
        )

    results = file_service.search_files(db=db, query_text=text, user_id=current_user.id)

    return [
        {
            "id": record.id,
            "original_name": record.original_name,
            "content_type": record.content_type,
            "size": record.size,
            "created_at": record.created_at,
        }
        for record in results
    ]
