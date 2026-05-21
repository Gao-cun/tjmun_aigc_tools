from datetime import date
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import SessionLocal, get_db
from app.models.delegate import DelegateProfile
from app.models.document import DocumentFeatureSet, WritingDocument
from app.schemas.document import UploadHistoryResponse
from app.services.embedding_providers import get_embedding_provider
from app.services.file_parser import parse_file
from app.services.stylometry import extract_stylometry

router = APIRouter(tags=["uploads"])


def _process_history_document(document_id: str) -> None:
    """后台解析历史文件并写入特征；异常落入文档状态，便于前端显示。"""
    db = SessionLocal()
    try:
        document = db.get(WritingDocument, document_id)
        if not document or not document.file_path:
            return
        text = parse_file(document.file_path)
        if not text:
            raise ValueError("Uploaded document contains no extractable text.")
        features = extract_stylometry(text)
        embedding = get_embedding_provider().embed_texts([text])[0].tolist()
        document.raw_text = text
        document.status = "ready"
        document.error_message = None
        document.feature_set = DocumentFeatureSet(features=features, embedding=embedding)
        db.commit()
    except Exception as exc:
        if document:
            document.status = "failed"
            document.error_message = str(exc)
            db.commit()
    finally:
        db.close()


@router.post("/upload_history", response_model=UploadHistoryResponse)
async def upload_history(
    background_tasks: BackgroundTasks,
    delegate_id: str = Form(...),
    document_type: str = Form("Position Paper"),
    meeting: str | None = Form(None),
    document_date: date | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    delegate = db.get(DelegateProfile, delegate_id)
    if not delegate:
        raise HTTPException(status_code=404, detail="Delegate profile not found.")

    settings = get_settings()
    settings.upload_path.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "upload.txt").suffix
    document = WritingDocument(
        delegate_id=delegate_id,
        filename=file.filename or "upload.txt",
        document_type=document_type,
        meeting=meeting,
        document_date=document_date,
        status="processing",
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    stored_path = settings.upload_path / f"{document.id}{suffix}"
    stored_path.write_bytes(await file.read())
    document.file_path = str(stored_path)
    db.commit()

    background_tasks.add_task(_process_history_document, document.id)
    return UploadHistoryResponse(document_id=document.id, status="processing", message="History document accepted for background processing.")

