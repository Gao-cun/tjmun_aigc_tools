from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.analysis import AnalysisRun
from app.models.delegate import DelegateProfile
from app.models.document import WritingDocument
from app.schemas.analysis import AnalyzeResponse
from app.services.embedding_providers import get_embedding_provider
from app.services.file_parser import parse_uploaded_file
from app.services.risk_engine import analyze_consistency
from app.services.stylometry import extract_stylometry

router = APIRouter(tags=["analysis"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_new_document(
    delegate_id: str = Form(...),
    embedding_provider: str | None = Form(None),
    local_embedding_model: str | None = Form(None),
    openai_embedding_model: str | None = Form(None),
    openai_api_key: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    delegate = db.get(DelegateProfile, delegate_id)
    if not delegate:
        raise HTTPException(status_code=404, detail="Delegate profile not found.")

    history_docs = (
        db.query(WritingDocument)
        .filter(WritingDocument.delegate_id == delegate_id, WritingDocument.status == "ready")
        .order_by(WritingDocument.created_at.asc())
        .all()
    )
    history_docs = [doc for doc in history_docs if doc.feature_set]
    if len(history_docs) < 2:
        raise HTTPException(status_code=400, detail="At least two processed history documents are required before analysis.")

    contents = await file.read()
    try:
        text = parse_uploaded_file(file.filename or "analysis.txt", contents)
        features = extract_stylometry(text)
        embedding = get_embedding_provider(
            overrides={
                "embedding_provider": embedding_provider,
                "local_embedding_model": local_embedding_model,
                "openai_embedding_model": openai_embedding_model,
                "openai_api_key": openai_api_key,
            }
        ).embed_texts([text])[0].tolist()
        history_embeddings = [doc.feature_set.embedding for doc in history_docs]
        if any(len(item) != len(embedding) for item in history_embeddings):
            raise ValueError("The selected embedding settings produce a different vector dimension than the history baseline. Please analyze with the same provider/model used for history uploads.")
        result = analyze_consistency(
            [doc.feature_set.features for doc in history_docs],
            history_embeddings,
            features,
            embedding,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    run = AnalysisRun(
        delegate_id=delegate_id,
        filename=file.filename or "analysis.txt",
        raw_text=text,
        features=features,
        embedding=embedding,
        result=result,
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    return AnalyzeResponse(analysis_id=run.id, delegate_id=delegate_id, filename=run.filename, risk_level=result["riskLevel"], result=result)
