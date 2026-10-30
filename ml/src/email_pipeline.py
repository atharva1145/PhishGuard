"""
PhishGuard Email NLP Pipeline
Preprocesses subject and body text, extracts features via TF-IDF, and detects NLP-based risk heuristics.

DISCLAIMER:
PhishGuard analyzes email text patterns locally. It does NOT claim to verify email sender authenticity,
SPF, DKIM, or DMARC records, as those require full email transport headers.
"""

from __future__ import annotations
import re
from typing import Dict, Any, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


# Regex patterns for normalization
URL_REGEX = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
EMAIL_REGEX = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+", re.IGNORECASE)
CURRENCY_REGEX = re.compile(r"[\$€£¥]\s*\d+(?:[,\.]\d+)*|\d+(?:[,\.]\d+)*\s*(?:dollars|usd|eur|gbp|btc|eth)", re.IGNORECASE)
PHONE_REGEX = re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")
HTML_TAG_REGEX = re.compile(r"<[^>]+>")
WHITESPACE_REGEX = re.compile(r"\s+")

# Risk indicator dictionary with regex patterns and explanations
EMAIL_INDICATOR_RULES = [
    {
        "id": "URGENCY_PRESSURE",
        "name": "Artificial Urgency & Deadline Pressure",
        "severity": "HIGH",
        "pattern": re.compile(r"\b(?:urgent|immediately|within \d+ hours?|account suspended|immediate action|terminate|expire within|final notice|critical warning|last chance)\b", re.IGNORECASE),
        "description": "Message emphasizes impending deadlines or sudden account cancellation.",
        "rationale": "Phishers rely on psychological urgency to induce panic and bypass the victim's critical analytical reasoning.",
    },
    {
        "id": "CREDENTIAL_HARVESTING",
        "name": "Direct Credential / Verification Request",
        "severity": "HIGH",
        "pattern": re.compile(r"\b(?:(?:verify|confirm|reset|update|re-enter|validate)\s+(?:your|my|the)?\s*(?:account|password|credentials?|security\s*info|identity|access))\b", re.IGNORECASE),
        "description": "Text prompts the recipient to verify or submit authentication credentials.",
        "rationale": "Legitimate enterprise services rarely instruct users via email body to click a link and re-enter passwords without prior user-initiated actions.",
    },
    {
        "id": "FINANCIAL_FRAUD_THEME",
        "name": "Financial Transfer or Payment Dispute",
        "severity": "HIGH",
        "pattern": re.compile(r"\b(?:wire transfer|unauthorized payment|overdue invoice|bitcoin wallet|cryptocurrency payment|gift cards?|claim your prize|won the lottery|refund issued)\b", re.IGNORECASE),
        "description": "Mentions irregular financial disbursements, bitcoin, gift cards, or overdue payment disputes.",
        "rationale": "High-impact social engineering attacks (such as CEO fraud or BEC) impersonate billing departments to divert financial transfers.",
    },
    {
        "id": "CALL_TO_ACTION_LINKS",
        "name": "Coerced Link Redirection",
        "severity": "MEDIUM",
        "pattern": re.compile(r"\b(?:click here to (?:login|verify|view)|follow the link below|access your portal here|download attachment to review|scan the qr code)\b", re.IGNORECASE),
        "description": "Strong instructional prompt directing user to follow an embedded link or scan a QR code.",
        "rationale": "Direct calls-to-action are intended to divert users off email clients onto malicious clone portals.",
    },
    {
        "id": "GENERIC_SALUTATION",
        "name": "Generic or Impersonal Salutation",
        "severity": "LOW",
        "pattern": re.compile(r"\b(?:dear customer|dear user|valued member|dear client|attention: account holder)\b", re.IGNORECASE),
        "description": "Impersonal greeting lacking recipient's actual name.",
        "rationale": "Automated mass-phishing campaigns frequently lack accurate recipient identity data, relying on generic placeholders.",
    },
]


def clean_and_normalize_text(text: str) -> str:
    """
    Safely sanitize, clean, and normalize raw email text without executing HTML or scripts.
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Remove HTML tags safely
    text = HTML_TAG_REGEX.sub(" ", text)
    
    # Normalize entities
    text = URL_REGEX.sub(" __URL__ ", text)
    text = EMAIL_REGEX.sub(" __EMAIL__ ", text)
    text = CURRENCY_REGEX.sub(" __MONEY__ ", text)
    text = PHONE_REGEX.sub(" __PHONE__ ", text)
    
    # Clean whitespace and lowercase
    text = WHITESPACE_REGEX.sub(" ", text).strip().lower()
    return text


def combine_subject_and_body(subject: str, body: str) -> str:
    """
    Produce normalized combined text representation for TF-IDF vectorization.
    """
    clean_subj = clean_and_normalize_text(subject or "")
    clean_bdy = clean_and_normalize_text(body or "")
    return f"subject: {clean_subj} body: {clean_bdy}".strip()


def extract_email_risk_indicators(subject: str, body: str) -> List[Dict[str, str]]:
    """
    Extract transparent rule-based risk indicators with rationale.
    """
    combined = f"{subject}\n{body}"
    detected = []

    for rule in EMAIL_INDICATOR_RULES:
        matches = rule["pattern"].findall(combined)
        if matches:
            unique_matches = list(dict.fromkeys(matches))[:3]
            detected.append({
                "id": rule["id"],
                "name": rule["name"],
                "severity": rule["severity"],
                "description": rule["description"],
                "evidence": f"Found cues: {', '.join(unique_matches)}",
                "rationale": rule["rationale"],
            })

    return detected


def build_email_pipeline() -> Pipeline:
    """
    Construct the baseline scikit-learn pipeline for email phishing classification.
    """
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            min_df=2,
            sublinear_tf=True,
            stop_words="english",
        )),
        ("classifier", LogisticRegression(
            class_weight="balanced",
            C=1.0,
            max_iter=1000,
            random_state=42,
            solver="liblinear",
        )),
    ])
    return pipeline
