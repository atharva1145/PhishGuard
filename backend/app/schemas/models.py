"""
PhishGuard Health & Model Metadata Schemas
"""

from __future__ import annotations
from typing import Dict, Any, Optional
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    database_status: str
    models_ready: bool
    models: Dict[str, Any]


class ModelMetadataResponse(BaseModel):
    pipeline_version: str
    last_trained_at: Optional[str]
    models: Dict[str, Any]
