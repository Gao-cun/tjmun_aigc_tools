from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.delegate import DelegateProfile
from app.models.document import DocumentFeatureSet, WritingDocument
from app.services.embedding_providers import HashEmbeddingProvider
from app.services.stylometry import extract_stylometry


DEMO_ROOT = Path(__file__).resolve().parents[2] / "data" / "demo"


def seed_demo_data(db: Session) -> dict:
    """写入一组稳定 demo 数据，避免首次打开 dashboard 空白。"""
    delegates_path = DEMO_ROOT / "delegates.json"
    if not delegates_path.exists():
        return {"createdDelegates": 0, "createdDocuments": 0}

    # demo 数据用于启动体验，使用确定性轻量向量，避免首次运行下载 HuggingFace 模型导致卡住。
    provider = HashEmbeddingProvider()
    created_delegates = 0
    created_documents = 0
    for item in json.loads(delegates_path.read_text(encoding="utf-8")):
        existing = db.query(DelegateProfile).filter(DelegateProfile.name == item["name"]).first()
        delegate = existing or DelegateProfile(name=item["name"], country=item.get("country"), committee=item.get("committee"), notes=item.get("notes"))
        if not existing:
            db.add(delegate)
            db.commit()
            db.refresh(delegate)
            created_delegates += 1

        for doc_meta in item.get("documents", []):
            if db.query(WritingDocument).filter(WritingDocument.delegate_id == delegate.id, WritingDocument.filename == doc_meta["filename"]).first():
                continue
            text = (DEMO_ROOT / "history_texts" / doc_meta["filename"]).read_text(encoding="utf-8")
            features = extract_stylometry(text)
            embedding = provider.embed_texts([text])[0].tolist()
            document = WritingDocument(
                delegate_id=delegate.id,
                filename=doc_meta["filename"],
                document_type=doc_meta.get("documentType", "Position Paper"),
                meeting=doc_meta.get("meeting"),
                raw_text=text,
                status="ready",
            )
            document.feature_set = DocumentFeatureSet(features=features, embedding=embedding)
            db.add(document)
            created_documents += 1
    db.commit()
    return {"createdDelegates": created_delegates, "createdDocuments": created_documents}
