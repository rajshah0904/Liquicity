from __future__ import annotations

from sqlalchemy import Column, DateTime, Integer, String, JSON, func, Boolean

from ..database import Base

class VelafiApiLog(Base):
    __tablename__ = "velafi_api_log"

    id = Column(Integer, primary_key=True)
    method = Column(String(8), nullable=False)  # GET / POST etc
    endpoint = Column(String(128), nullable=False)
    request_payload = Column(JSON, nullable=True)
    response_payload = Column(JSON, nullable=True)
    status_code = Column(Integer, nullable=False)
    success = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 