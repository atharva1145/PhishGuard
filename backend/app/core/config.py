"""
PhishGuard Backend Configuration
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import List

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = BASE_DIR.parent

ML_DIR = PROJECT_ROOT / "ml"
MODELS_DIR = ML_DIR / "models"
REPORTS_DIR = ML_DIR / "reports"

# Development CORS origins
ALLOWED_ORIGINS: List[str] = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

PROJECT_NAME = "PhishGuard Explainable AI Platform"
API_V1_STR = "/api"
VERSION = "1.0.0"
