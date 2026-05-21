from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DelegateCreate(BaseModel):
    name: str
    country: str | None = None
    committee: str | None = None
    notes: str | None = None


class DelegateRead(BaseModel):
    id: str
    name: str
    country: str | None = None
    committee: str | None = None
    notes: str | None = None
    created_at: datetime
    document_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class DelegateProfileResponse(BaseModel):
    delegate: DelegateRead
    documents: list[dict]
    embedding_stats: dict | None = None
    style_baseline: dict | None = None

