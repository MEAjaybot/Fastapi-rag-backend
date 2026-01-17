import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.sql import Base

class Document(Base):
    __tablename__ = "documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String)
    file_type = Column(String)
    chunk_strategy = Column(String)
    num_chunks = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())