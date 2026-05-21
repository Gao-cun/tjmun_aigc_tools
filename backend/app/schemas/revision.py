from pydantic import BaseModel, Field


class RevisionAnalysisRequest(BaseModel):
    delegate_id: str | None = None
    source_type: str = "typing_session"
    events: list[dict] = Field(default_factory=list)


class RevisionAnalysisResponse(BaseModel):
    revision_session_id: str | None = None
    result: dict

