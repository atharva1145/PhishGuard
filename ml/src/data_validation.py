"""
PhishGuard Data Validation & Leakage Prevention Module
Ensures clean train/test separation, schema adherence, deduplication, and label verification.
"""

from __future__ import annotations
import logging
from typing import Tuple, Dict, Any
import pandas as pd
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)


def validate_and_clean_url_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates URL dataset:
    - Checks required columns: 'url', 'label'
    - Ensures label is integer 0 or 1
    - Cleans whitespace and normalizes
    - Performs strict deduplication to eliminate target leakage
    """
    if "url" not in df.columns or "label" not in df.columns:
        raise ValueError("URL dataset must contain 'url' and 'label' columns.")

    initial_count = len(df)
    cleaned_df = df.dropna(subset=["url", "label"]).copy()
    
    # Cast label to int and filter valid classes
    cleaned_df["label"] = cleaned_df["label"].astype(int)
    cleaned_df = cleaned_df[cleaned_df["label"].isin([0, 1])]
    
    # Normalize URL representation for deduplication
    cleaned_df["url_clean"] = cleaned_df["url"].astype(str).str.strip()
    cleaned_df = cleaned_df[cleaned_df["url_clean"].str.len() > 3]
    
    # Deduplicate based on cleaned URL
    cleaned_df = cleaned_df.drop_duplicates(subset=["url_clean"]).copy()
    cleaned_df["url"] = cleaned_df["url_clean"]
    cleaned_df = cleaned_df.drop(columns=["url_clean"])

    final_count = len(cleaned_df)
    logger.info(f"URL dataset cleaned: {initial_count} initial -> {final_count} valid deduplicated records.")
    return cleaned_df.reset_index(drop=True)


def validate_and_clean_email_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates Email dataset:
    - Checks required columns: 'subject', 'body', 'label'
    - Ensures label is integer 0 or 1
    - Drops empty/null rows
    - Deduplicates on combined text
    """
    required_cols = {"subject", "body", "label"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"Email dataset must contain {required_cols}")

    initial_count = len(df)
    cleaned_df = df.dropna(subset=["body", "label"]).copy()
    cleaned_df["subject"] = cleaned_df["subject"].fillna("").astype(str).str.strip()
    cleaned_df["body"] = cleaned_df["body"].astype(str).str.strip()
    cleaned_df["label"] = cleaned_df["label"].astype(int)
    cleaned_df = cleaned_df[cleaned_df["label"].isin([0, 1])]

    # Combined text for deduplication
    cleaned_df["dedup_key"] = (cleaned_df["subject"] + " || " + cleaned_df["body"]).str.lower()
    cleaned_df = cleaned_df[cleaned_df["body"].str.len() > 10]
    cleaned_df = cleaned_df.drop_duplicates(subset=["dedup_key"]).copy()
    cleaned_df = cleaned_df.drop(columns=["dedup_key"])

    final_count = len(cleaned_df)
    logger.info(f"Email dataset cleaned: {initial_count} initial -> {final_count} valid deduplicated records.")
    return cleaned_df.reset_index(drop=True)


def split_dataset(
    df: pd.DataFrame, 
    test_size: float = 0.2, 
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Performs reproducible stratified train/test split.
    Guarantees no overlap between train and test sets.
    """
    train_df, test_df = train_test_split(
        df,
        test_size=test_size,
        stratify=df["label"],
        random_state=random_state,
        shuffle=True
    )
    return train_df.reset_index(drop=True), test_df.reset_index(drop=True)


def verify_split_leakage(train_series: pd.Series, test_series: pd.Series, name: str = "items") -> None:
    """
    Rigorous leakage check: Asserts that no element in train exists in test.
    """
    train_set = set(train_series.str.strip().str.lower())
    test_set = set(test_series.str.strip().str.lower())
    overlap = train_set.intersection(test_set)
    if overlap:
        raise AssertionError(f"Target leakage detected! {len(overlap)} overlapping {name} found between train and test.")
