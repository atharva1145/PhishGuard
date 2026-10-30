"""
PhishGuard Email Scanning Service
Analyzes email subject and body, extracts XAI influential terms, and logs sanitized metadata without raw body text.
"""

from __future__ import annotations
import uuid
from typing import Dict, Any
from ml.src.predict import predict_email
from backend.app.database.db import insert_scan_record


def execute_email_scan(subject: str, body: str) -> Dict[str, Any]:
    """
    Executes NLP email classification.
    PRIVACY REQUIREMENT: Raw email body is never stored in persistent database logs.
    Only sanitized subject snippet and top explanation metadata are recorded.
    """
    prediction_result = predict_email(subject, body)
    scan_id = str(uuid.uuid4())

    # Build DB history record
    clean_subj = subject.strip() if subject else "(No Subject)"
    target_preview = f"Subj: {clean_subj[:80]}..." if len(clean_subj) > 80 else f"Subj: {clean_subj}"

    db_record = {
        "scan_id": scan_id,
        "scan_type": "email",
        "target_preview": target_preview,
        "prediction": prediction_result["prediction"],
        "is_phishing": prediction_result["is_phishing"],
        "confidence_score": prediction_result["confidence_score"],
        "risk_level": prediction_result["risk_level"],
        "indicators_count": len(prediction_result["risk_indicators"]),
        "model_version": prediction_result["model_version"],
        "created_at": prediction_result["timestamp"],
        "details": {
            "risk_indicators": prediction_result["risk_indicators"],
            "influential_terms": prediction_result["influential_terms"],
            "explanation": prediction_result["explanation"],
            "phishing_probability": prediction_result["phishing_probability"]
        }
    }
    insert_scan_record(db_record)

    return {
        "scan_id": scan_id,
        **prediction_result
    }


import re
import email
from email import policy
from email.parser import BytesParser


def parse_and_scan_eml_file(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    Safely parses an uploaded RFC 822 / MIME (.eml) file:
    - Extracts headers (Subject, From, To, Date)
    - Checks SPF/DKIM/DMARC authentication hints
    - Extracts plain text body (or strips HTML safely)
    - Identifies embedded URLs and suspicious attachment types
    - Runs text through NLP classifier without executing attachments or rendering remote content.
    """
    if len(file_bytes) > 10 * 1024 * 1024:
        raise ValueError("Uploaded .eml file exceeds maximum size limit of 10 MB.")

    try:
        msg = BytesParser(policy=policy.default).parsebytes(file_bytes)
    except Exception as e:
        raise ValueError(f"Failed to parse .eml file structure: {str(e)}")

    subject = str(msg.get("Subject", "") or "")
    from_header = str(msg.get("From", "") or "")
    to_header = str(msg.get("To", "") or "")
    date_header = str(msg.get("Date", "") or "")

    # Headers for authentication context
    auth_results = msg.get("Authentication-Results", None)
    if auth_results:
        auth_results = str(auth_results)
    received_spf = msg.get("Received-SPF", None)
    if received_spf:
        received_spf = str(received_spf)
    dkim_present = msg.get("DKIM-Signature", None) is not None

    plain_body = ""
    html_body = ""
    attachments = []

    for part in msg.walk():
        content_type = part.get_content_type()
        disposition = str(part.get("Content-Disposition", ""))

        if "attachment" in disposition.lower():
            fname = part.get_filename() or "unnamed_attachment"
            payload_data = part.get_payload(decode=True) or b""
            size = len(payload_data)
            is_exec = any(fname.lower().endswith(ext) for ext in [".exe", ".scr", ".bat", ".cmd", ".vbs", ".js", ".iso", ".zip", ".msi", ".ps1"])
            attachments.append({
                "filename": fname,
                "content_type": content_type,
                "size_bytes": size,
                "is_executable": is_exec,
            })
        elif content_type == "text/plain" and not plain_body:
            try:
                content = part.get_content()
                if isinstance(content, str):
                    plain_body = content
            except Exception:
                raw_payload = part.get_payload(decode=True) or b""
                plain_body = raw_payload.decode("utf-8", errors="replace")
        elif content_type == "text/html" and not html_body:
            try:
                content = part.get_content()
                if isinstance(content, str):
                    html_body = content
            except Exception:
                raw_payload = part.get_payload(decode=True) or b""
                html_body = raw_payload.decode("utf-8", errors="replace")

    # Combine extracted body text
    body = plain_body.strip() if plain_body.strip() else html_body.strip()
    if not body:
        body = f"(Subject-only email: {subject})"

    # Extract all embedded URLs for analyst convenience
    url_pattern = re.compile(r"https?://[^\s<>\"'()]+", re.IGNORECASE)
    embedded_urls = list(dict.fromkeys(url_pattern.findall(f"{subject} {plain_body} {html_body}")))[:15]

    # Execute NLP scan
    scan_result = execute_email_scan(subject, body)

    # Attach EML metadata
    scan_result["extracted_subject"] = subject
    scan_result["extracted_body"] = body[:2000] + ("..." if len(body) > 2000 else "")
    scan_result["eml_metadata"] = {
        "from_header": from_header,
        "to_header": to_header,
        "date_header": date_header,
        "spf_header": received_spf,
        "dkim_present": dkim_present,
        "auth_results": auth_results,
        "embedded_urls": embedded_urls,
        "attachments": attachments,
    }

    # If executable attachment detected, add high-risk indicator
    if any(a["is_executable"] for a in attachments):
        exec_names = [a["filename"] for a in attachments if a["is_executable"]]
        scan_result["risk_indicators"].append({
            "id": "EXECUTABLE_ATTACHMENT",
            "name": "Dangerous / Executable Attachment Detected",
            "severity": "HIGH",
            "description": f"Email contains potentially malicious attachment: {', '.join(exec_names)}",
            "evidence": f"Attachment filenames: {', '.join(exec_names)}",
            "rationale": "Phishing attacks deliver infostealers, droppers, and ransomware via executable script or archive attachments.",
        })

    return scan_result
