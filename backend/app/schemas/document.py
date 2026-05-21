from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class DocumentRead(BaseModel):
    id: str
    delegate_id: str
    filename: str
    document_type: str
    meeting: str | None = None
    document_date: date | None = None
    status: str
    error_message: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UploadHistoryResponse(BaseModel):
    document_id: str
    status: str
    message: str

