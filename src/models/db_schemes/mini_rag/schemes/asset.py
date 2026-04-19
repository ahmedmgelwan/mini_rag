from .minirag_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, DateTime, func, String, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from uuid import uuid4

class Asset(SQLAlchemyBase):
    __tablename__ = 'assets'
    asset_id = Column(Integer, primary_key=True, autoincrement=True)
    asset_uuid = Column(UUID(as_uuid=True),default=uuid4, nullable=False, unique=True)
    asset_name = Column(String, nullable=False)
    asset_type = Column(String, nullable=False)
    asset_size = Column(Integer, nullable=False)
    asset_config = Column(JSONB, nullable=True)
    asset_project_id = Column(Integer, ForeignKey('projects.project_id'), nullable=False)

    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    project = relationship("Project", back_populates="assets")
    chunks = relationship('DataChunk', back_populates='assets')

    __table_args__ = (
        Index('asset_projec_id_idx', asset_project_id),
        Index('asset_type_idx', asset_type)
    )