"""
PhishGuard Scan History Schemas
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class HistoryItemResponse(BaseModel):
    scan_id: str
    scan_type: str
    target_preview: str
    prediction: str
    is_phishing: bool
    confidence_score: float
    risk_level: str
    indicators_count: int
    model_version: str
    created_at: str
    details: Dict[str, Any]


class HistoryListResponse(BaseModel):
    total: int
    items: List[HistoryItemResponse]


class HistoryDeleteResponse(BaseModel):
    success: bool
    message: str
