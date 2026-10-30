"""
PhishGuard FastAPI Route Handlers
Defines REST API endpoints for scanning, health checks, model metadata, metrics, and scan history.
"""

from __future__ import annotations
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status, UploadFile, File

from backend.app.schemas.scan import (
    UrlScanRequest, UrlScanResponse,
    EmailScanRequest, EmailScanResponse
)
from backend.app.schemas.models import HealthResponse, ModelMetadataResponse
from backend.app.schemas.metrics import AllMetricsResponse
from backend.app.schemas.history import HistoryListResponse, HistoryDeleteResponse
from backend.app.services.url_scanner import execute_url_scan
from backend.app.services.email_scanner import execute_email_scan, parse_and_scan_eml_file
from backend.app.services.model_service import (
    check_models_health, get_model_metadata, load_evaluation_report
)
from backend.app.database.db import (
    get_scan_history, delete_scan_record, clear_all_history, get_scan_summary_stats
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["System Health"])
async def get_health():
    """
    Returns application status and model readiness.
    Distinguishes application operational status from model artifact readiness.
    """
    models_status = check_models_health()
    db_status = "operational"

    return {
        "status": "healthy" if models_status["all_ready"] else "degraded",
        "timestamp": datetime.now().isoformat(),
        "database_status": db_status,
        "models_ready": models_status["all_ready"],
        "models": models_status
    }


@router.get("/models", response_model=ModelMetadataResponse, tags=["Model Registry"])
async def get_models():
    """Returns metadata for all trained classifiers, versions, and training run dates."""
    metadata = get_model_metadata()
    return metadata


@router.post("/scan/url", response_model=UrlScanResponse, tags=["Scanners"])
async def scan_url(payload: UrlScanRequest):
    """
    Scans a submitted URL string using the trained classifier and XAI engine.
    SECURITY ASSURANCE: Strictly analyzes URL string locally; never issues external HTTP or DNS requests.
    """
    models_status = check_models_health()
    if not models_status["url_classifier"]["ready"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="URL phishing classification model is not available. Please train models via `python scripts/train_models.py`."
        )

    try:
        result = execute_url_scan(payload.url)
        return result
    except Exception as e:
        logger.error(f"Error during URL scan: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while analyzing the URL: {str(e)}"
        )


@router.post("/scan/email", response_model=EmailScanResponse, tags=["Scanners"])
async def scan_email(payload: EmailScanRequest):
    """
    Scans email subject and body text using the trained TF-IDF NLP pipeline.
    Analyzes vocabulary and linguistic risk indicators.
    PRIVACY ASSURANCE: Raw email body is never persisted in database logs.
    """
    models_status = check_models_health()
    if not models_status["email_classifier"]["ready"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Email phishing classification model is not available. Please train models via `python scripts/train_models.py`."
        )

    try:
        result = execute_email_scan(payload.subject, payload.body)
        return result
    except Exception as e:
        logger.error(f"Error during email scan: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while analyzing the email: {str(e)}"
        )


@router.post("/scan/email/file", response_model=EmailScanResponse, tags=["Scanners"])
async def scan_email_file(file: UploadFile = File(...)):
    """
    Parses and scans an uploaded .eml (RFC 822 MIME) message file.
    Extracts headers, checks SPF/DKIM flags, identifies embedded URLs and attachments,
    and runs the text through the NLP classifier without executing external code.
    """
    models_status = check_models_health()
    if not models_status["email_classifier"]["ready"]:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Email phishing classification model is not available. Please train models via `python scripts/train_models.py`."
        )

    filename = file.filename or "upload.eml"
    if not any(filename.lower().endswith(ext) for ext in [".eml", ".msg", ".txt"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload an RFC 822 .eml or text file."
        )

    try:
        file_bytes = await file.read()
        result = parse_and_scan_eml_file(file_bytes, filename)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Error parsing .eml file: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while parsing the email file: {str(e)}"
        )


@router.get("/metrics", response_model=AllMetricsResponse, tags=["Model Evaluation"])
async def get_evaluation_metrics():
    """
    Returns authentic evaluation reports generated from the held-out test splits,
    including confusion matrices, FPR, FNR, per-class metrics, and model comparisons.
    """
    url_eval = load_evaluation_report("url_evaluation.json")
    email_eval = load_evaluation_report("email_evaluation.json")
    comparison = load_evaluation_report("model_comparison.json")
    stats = get_scan_summary_stats()

    return {
        "url_evaluation": url_eval,
        "email_evaluation": email_eval,
        "model_comparison": comparison,
        "scan_statistics": stats
    }


@router.get("/history", response_model=HistoryListResponse, tags=["Scan History"])
async def list_history(
    scan_type: Optional[str] = Query(None, description="Filter by 'url' or 'email'"),
    prediction: Optional[str] = Query(None, description="Filter by 'phishing' or 'legitimate'"),
    search: Optional[str] = Query(None, description="Search term for target preview"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    """Retrieves paginated scan history with optional filtering and search."""
    history_data = get_scan_history(
        scan_type=scan_type,
        prediction=prediction,
        search=search,
        limit=limit,
        offset=offset
    )
    return history_data


@router.delete("/history/{scan_id}", response_model=HistoryDeleteResponse, tags=["Scan History"])
async def delete_history_item(scan_id: str):
    """Deletes an individual scan record from history."""
    success = delete_scan_record(scan_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan record with ID '{scan_id}' not found."
        )
    return {"success": True, "message": f"Scan record '{scan_id}' deleted successfully."}


@router.delete("/history", response_model=HistoryDeleteResponse, tags=["Scan History"])
async def clear_history():
    """Clears all scan history records from local SQLite storage."""
    deleted_count = clear_all_history()
    return {"success": True, "message": f"Cleared {deleted_count} scan records from history."}
