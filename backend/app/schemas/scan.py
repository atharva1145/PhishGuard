"""
PhishGuard Pydantic Schemas for URL and Email Scanning
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, HttpUrl, field_validator


class RiskIndicatorSchema(BaseModel):
    id: str
    name: str
    severity: str  # HIGH, MEDIUM, LOW, INFO
    description: str
    evidence: str
    rationale: str


class FeatureContributionSchema(BaseModel):
    feature: str
    display_name: str
    description: str
    raw_value: Any
    contribution: float
    direction: str  # phishing, legitimate
    abs_contribution: float


class InfluentialTermSchema(BaseModel):
    term: str
    tfidf_value: float
    coefficient: float
    contribution: float
    direction: str
    abs_contribution: float


class UrlScanRequest(BaseModel):
    url: str = Field(..., min_length=3, max_length=2048, description="URL string to analyze")

    @field_validator("url")
    def validate_url(cls, v: str) -> str:
        clean = v.strip()
        if len(clean) < 3:
            raise ValueError("URL must be at least 3 characters long.")
        if len(clean) > 2048:
            raise ValueError("URL length exceeds maximum permissible limit of 2048 characters.")
        return clean


class SyntaxTokenSchema(BaseModel):
    text: str
    type: str  # scheme, userinfo, ip_host, punycode, subdomain, domain, tld, port, path, query
    is_suspicious: bool
    severity: str  # HIGH, MEDIUM, LOW, INFO, SAFE
    tooltip: str


class EmlAttachmentSchema(BaseModel):
    filename: str
    content_type: str
    size_bytes: int
    is_executable: bool


class EmlMetadataSchema(BaseModel):
    from_header: str
    to_header: str
    date_header: str
    spf_header: Optional[str] = None
    dkim_present: bool = False
    auth_results: Optional[str] = None
    embedded_urls: List[str] = []
    attachments: List[EmlAttachmentSchema] = []


class BrandImpersonationSchema(BaseModel):
    is_impersonating: bool
    target_brand: str
    canonical_domain: str
    spoof_technique: str
    severity: str
    similarity_score: float
    details: str


class EnsembleModelResultSchema(BaseModel):
    model_name: str
    prediction: str
    phishing_probability: float
    is_phishing: bool


class EnsembleConsensusSchema(BaseModel):
    models_evaluated: int
    consensus_verdict: str
    agreement_ratio: float
    models: List[EnsembleModelResultSchema]


class UrlScanResponse(BaseModel):
    scan_id: str
    scan_type: str = "url"
    target: str
    prediction: str
    is_phishing: bool
    confidence_score: float
    phishing_probability: float
    risk_level: str
    risk_indicators: List[RiskIndicatorSchema]
    brand_impersonation: Optional[BrandImpersonationSchema] = None
    ensemble_consensus: Optional[EnsembleConsensusSchema] = None
    feature_contributions: List[FeatureContributionSchema]
    syntax_tokens: Optional[List[SyntaxTokenSchema]] = []
    explanation: str
    model_version: str
    timestamp: str
    disclaimer: str


class EmailScanRequest(BaseModel):
    subject: str = Field("", max_length=500, description="Email subject line")
    body: str = Field(..., min_length=5, max_length=50000, description="Email body text content")

    @field_validator("body")
    def validate_body(cls, v: str) -> str:
        clean = v.strip()
        if len(clean) < 5:
            raise ValueError("Email body must be at least 5 characters.")
        if len(clean) > 50000:
            raise ValueError("Email body exceeds maximum size of 50,000 characters.")
        return clean


class EmailScanResponse(BaseModel):
    scan_id: str
    scan_type: str = "email"
    target_preview: str
    prediction: str
    is_phishing: bool
    confidence_score: float
    phishing_probability: float
    risk_level: str
    risk_indicators: List[RiskIndicatorSchema]
    influential_terms: List[InfluentialTermSchema]
    explanation: str
    model_version: str
    timestamp: str
    warning: str
    extracted_subject: Optional[str] = None
    extracted_body: Optional[str] = None
    eml_metadata: Optional[EmlMetadataSchema] = None
