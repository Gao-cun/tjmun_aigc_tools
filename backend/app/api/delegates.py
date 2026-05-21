from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.delegate import DelegateProfile
from app.models.document import DocumentFeatureSet, WritingDocument
from app.schemas.delegate import DelegateCreate, DelegateProfileResponse, DelegateRead
from app.services.embedding_stats import build_embedding_stats
from app.services.stylometry import flatten_features

router = APIRouter(tags=["delegates"])


def _delegate_read(delegate: DelegateProfile) -> DelegateRead:
    return DelegateRead(
        id=delegate.id,
        name=delegate.name,
        country=delegate.country,
        committee=delegate.committee,
        notes=delegate.notes,
        created_at=delegate.created_at,
        document_count=len(delegate.documents),
    )


@router.post("/delegates", response_model=DelegateRead)
def create_delegate(payload: DelegateCreate, db: Session = Depends(get_db)):
    delegate = DelegateProfile(**payload.model_dump())
    db.add(delegate)
    db.commit()
    db.refresh(delegate)
    return _delegate_read(delegate)


@router.get("/delegates", response_model=list[DelegateRead])
def list_delegates(db: Session = Depends(get_db)):
    delegates = db.query(DelegateProfile).order_by(DelegateProfile.created_at.desc()).all()
    return [_delegate_read(delegate) for delegate in delegates]


@router.get("/delegate/{delegate_id}/profile", response_model=DelegateProfileResponse)
def get_delegate_profile(delegate_id: str, db: Session = Depends(get_db)):
    delegate = db.get(DelegateProfile, delegate_id)
    if not delegate:
        raise HTTPException(status_code=404, detail="Delegate profile not found.")

    docs = db.query(WritingDocument).filter(WritingDocument.delegate_id == delegate_id).order_by(WritingDocument.created_at.asc()).all()
    ready_docs = [doc for doc in docs if doc.status == "ready" and doc.feature_set]
    embedding_stats = None
    style_baseline = None
    if ready_docs:
        embedding_stats = build_embedding_stats([doc.feature_set.embedding for doc in ready_docs], [doc.filename for doc in ready_docs])
        flats = [flatten_features(doc.feature_set.features) for doc in ready_docs]
        keys = sorted({key for item in flats for key in item})
        style_baseline = {
            key: sum(item.get(key, 0.0) for item in flats) / max(len(flats), 1)
            for key in keys
            if key in {"average_sentence_length", "long_sentence_ratio", "passive_voice_ratio", "lexical_diversity"}
        }

    return DelegateProfileResponse(
        delegate=_delegate_read(delegate),
        documents=[
            {
                "id": doc.id,
                "filename": doc.filename,
                "documentType": doc.document_type,
                "meeting": doc.meeting,
                "documentDate": doc.document_date.isoformat() if doc.document_date else None,
                "status": doc.status,
                "errorMessage": doc.error_message,
                "createdAt": doc.created_at.isoformat(),
            }
            for doc in docs
        ],
        embedding_stats=embedding_stats,
        style_baseline=style_baseline,
    )

