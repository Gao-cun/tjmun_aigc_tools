from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.api import analysis, delegates, embeddings, revisions, uploads
from app.core.config import get_settings
from app.core.database import Base, engine, get_db
from app.models import AnalysisRun, DelegateProfile, DocumentFeatureSet, RevisionSession, WritingDocument
from app.services.demo_seed import seed_demo_data

settings = get_settings()
settings.upload_path.mkdir(parents=True, exist_ok=True)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Delegate Writing Consistency Analyzer",
    description="Writing consistency analysis against a delegate's historical style baseline.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(delegates.router)
app.include_router(uploads.router)
app.include_router(analysis.router)
app.include_router(embeddings.router)
app.include_router(revisions.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "delegate-writing-consistency-analyzer"}


@app.post("/demo/seed")
def demo_seed(db: Session = Depends(get_db)):
    return seed_demo_data(db)

