from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from datetime import datetime
from sqlalchemy.orm import Session

from db.models import UserRecord, FileRecord
from utils.auth import get_current_user
from db.database import get_db

UPLOAD_DIR = Path("files")

router = APIRouter(prefix="/files", tags=["files"])


async def save_upload_file(
    upload_file: UploadFile, user_id: int, db: Session
) -> FileRecord:

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    content_type = upload_file.content_type or "application/octet-stream"

    # for the sanitization of the path(path traversal vulnerability)
    safe_name = Path(upload_file.filename).name
    extension = Path(safe_name).suffix
    generated_name = f"{timestamp}_{extension}"

    user_dir = UPLOAD_DIR / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    file_path = user_dir / generated_name

    content = await upload_file.read()
    file_path.write_bytes(content)

    db_file = FileRecord(
        user_id=user_id,
        nume=safe_name,
        generated_name=generated_name,
        content_type=content_type,
        path=str(file_path),
    )

    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    current_user: UserRecord = Depends(get_current_user),
    db=Depends(get_db),
):
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    db_record = await save_upload_file(file, current_user.id, db)
    return db_record


@router.get("", response_model=list[dict])
async def list_my_files(
    current_user: UserRecord = Depends(get_current_user), db: Session = Depends(get_db)
):
    files = db.query(FileRecord).filter(FileRecord.user_id == current_user.id).all()
    return files


@router.get("/{file_id}")
async def get_file_metadata(
    file_id: int,
    current_user: UserRecord = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    file_record = (
        db.query(FileRecord)
        .filter(FileRecord.id == file_id, FileRecord.user_id == current_user.id)
        .first()
    )

    if not file_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

    return file_record


@router.get("/{file_id}/preview", response_class=FileResponse)
async def preview_file(
    file_id: int,
    current_user: UserRecord = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    file_record = (
        db.query(FileRecord)
        .filter(FileRecord.id == file_id, FileRecord.user_id == current_user.id)
        .first()
    )

    if not file_record or not Path(file_record.path).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File content not found on disk",
        )

    return FileResponse(
        path=file_record.path,
        filename=file_record.nume,
        media_type=file_record.content_type,
    )
