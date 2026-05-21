from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.document import WritingDocument
from app.schemas.analysis import EmbeddingStatsResponse
from app.services.embedding_stats import build_embedding_stats

router = APIRouter(tags=["embeddings"])


@router.get("/embedding_stats", response_model=EmbeddingStatsResponse)
def embedding_stats(delegate_id: str = Query(...), db: Session = Depends(get_db)):
    docs = (
        db.query(WritingDocument)
        .filter(WritingDocument.delegate_id == delegate_id, WritingDocument.status == "ready")
        .order_by(WritingDocument.created_at.asc())
        .all()
    )
    docs = [doc for doc in docs if doc.feature_set]
    if not docs:
        raise HTTPException(status_code=404, detail="No processed history embeddings found for this delegate.")
    stats = build_embedding_stats([doc.feature_set.embedding for doc in docs], [doc.filename for doc in docs])
    return EmbeddingStatsResponse(delegate_id=delegate_id, **stats)

