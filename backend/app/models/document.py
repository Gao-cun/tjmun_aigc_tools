import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class WritingDocument(Base):
    __tablename__ = "writing_documents"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    delegate_id: Mapped[str] = mapped_column(ForeignKey("delegate_profiles.id"), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(240), nullable=False)
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    document_type: Mapped[str] = mapped_column(String(80), default="Position Paper")
    meeting: Mapped[str | None] = mapped_column(String(160), nullable=True)
    document_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="processing")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    delegate = relationship("DelegateProfile", back_populates="documents")
    feature_set = relationship("DocumentFeatureSet", back_populates="document", uselist=False, cascade="all, delete-orphan")


class DocumentFeatureSet(Base):
    __tablename__ = "document_feature_sets"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id: Mapped[str] = mapped_column(ForeignKey("writing_documents.id"), nullable=False, unique=True)
    features: Mapped[dict] = mapped_column(JSON, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    document = relationship("WritingDocument", back_populates="feature_set")

