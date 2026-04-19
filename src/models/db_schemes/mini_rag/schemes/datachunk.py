from .minirag_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, DateTime, func, String, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from uuid import uuid4
from pydantic import BaseModel


class DataChunk(SQLAlchemyBase):
    __tablename__ = 'chunks'
    chunk_id = Column(Integer, primary_key=True, autoincrement=True)
    chunk_uuid = Column(UUID(as_uuid=True), default=uuid4,unique=True, nullable=False)
    chunk_text = Column(String, nullable=False)
    chunk_metadata = Column(JSONB, nullable=True)
    chunk_project_id = Column(Integer, ForeignKey('projects.project_id'), nullable=False)
    chunk_asset_id = Column(Integer, ForeignKey('assets.asset_id'), nullable=False)

    project = relationship('Project', back_populates='chunks')
    assets = relationship('Asset', back_populates='chunks')

    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    __table_args__ = (
        Index('chunk_project_id_idx', chunk_project_id),
        Index('chunk_asset_id_idx', chunk_asset_id)
    )



class RetrivedDocument(BaseModel):
    text: str
    score: float