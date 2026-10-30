"""
PhishGuard Evaluation Metrics Schemas
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class MetricReportSchema(BaseModel):
    model_type: str
    model_version: str
    algorithm: str
    evaluated_at: str
    dataset_summary: Dict[str, Any]
    evaluation_protocol: str
    metrics: Dict[str, Any]
    model_comparison: List[Dict[str, Any]]
    misclassified_samples: List[Dict[str, Any]]


class AllMetricsResponse(BaseModel):
    url_evaluation: Optional[Dict[str, Any]]
    email_evaluation: Optional[Dict[str, Any]]
    model_comparison: Optional[Dict[str, Any]]
    scan_statistics: Dict[str, Any]
