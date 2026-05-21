from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.revision import RevisionSession
from app.schemas.revision import RevisionAnalysisRequest, RevisionAnalysisResponse
from app.services.revision_analyzer import analyze_revision_events

router = APIRouter(tags=["revisions"])


@router.post("/revision_analysis", response_model=RevisionAnalysisResponse)
def revision_analysis(payload: RevisionAnalysisRequest, db: Session = Depends(get_db)):
    result = analyze_revision_events(payload.events)
    session = RevisionSession(delegate_id=payload.delegate_id, source_type=payload.source_type, events=payload.events, result=result)
    db.add(session)
    db.commit()
    db.refresh(session)
    return RevisionAnalysisResponse(revision_session_id=session.id, result=result)

