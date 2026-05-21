import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RevisionSession(Base):
    __tablename__ = "revision_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    delegate_id: Mapped[str | None] = mapped_column(ForeignKey("delegate_profiles.id"), nullable=True, index=True)
    source_type: Mapped[str] = mapped_column(String(80), default="typing_session")
    events: Mapped[list[dict]] = mapped_column(JSON, nullable=False)
    result: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

