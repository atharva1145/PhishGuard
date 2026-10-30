"""
PhishGuard Brand Impersonation & Typosquatting Detection Engine
Detects visual confusables, homoglyphs, Damerau-Levenshtein lookalikes,
subdomain stacking, and combo-squatting against high-value targeted brands.
"""

from __future__ import annotations
import re
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse

# Database of high-value brands commonly targeted in phishing campaigns
PROTECTED_BRANDS = {
    "paypal": {"name": "PayPal", "canonical": ["paypal.com"]},
    "microsoft": {"name": "Microsoft", "canonical": ["microsoft.com", "office.com", "live.com", "microsoftonline.com"]},
    "apple": {"name": "Apple", "canonical": ["apple.com", "icloud.com"]},
    "google": {"name": "Google", "canonical": ["google.com", "gmail.com", "google.co.uk"]},
    "amazon": {"name": "Amazon", "canonical": ["amazon.com", "aws.amazon.com"]},
    "netflix": {"name": "Netflix", "canonical": ["netflix.com"]},
    "chase": {"name": "Chase Bank", "canonical": ["chase.com"]},
    "bankofamerica": {"name": "Bank of America", "canonical": ["bankofamerica.com"]},
    "wellsfargo": {"name": "Wells Fargo", "canonical": ["wellsfargo.com"]},
    "binance": {"name": "Binance", "canonical": ["binance.com"]},
    "coinbase": {"name": "Coinbase", "canonical": ["coinbase.com"]},
    "docusign": {"name": "DocuSign", "canonical": ["docusign.com", "docusign.net"]},
    "facebook": {"name": "Facebook", "canonical": ["facebook.com", "fb.com"]},
    "instagram": {"name": "Instagram", "canonical": ["instagram.com"]},
    "linkedin": {"name": "LinkedIn", "canonical": ["linkedin.com"]},
    "dhl": {"name": "DHL Express", "canonical": ["dhl.com"]},
    "fedex": {"name": "FedEx", "canonical": ["fedex.com"]},
    "usps": {"name": "USPS", "canonical": ["usps.com"]},
    "steam": {"name": "Steam", "canonical": ["steampowered.com", "steamcommunity.com"]},
    "metamask": {"name": "MetaMask", "canonical": ["metamask.io"]},
    "dropbox": {"name": "Dropbox", "canonical": ["dropbox.com"]},
    "adobe": {"name": "Adobe", "canonical": ["adobe.com"]},
    "spotify": {"name": "Spotify", "canonical": ["spotify.com"]},
}

# Visual confusable characters and homoglyph mapping
CONFUSABLE_MAP = {
    "0": "o",
    "1": "l",
    "|": "l",
    "!": "i",
    "@": "a",
    "$": "s",
    "5": "s",
    "3": "e",
    "8": "b",
    "vv": "w",
    "rn": "m",
    "cl": "d",
}


def damerau_levenshtein_distance(s1: str, s2: str) -> int:
    """
    Computes Damerau-Levenshtein distance between two strings,
    supporting insertions, deletions, substitutions, and adjacent transpositions.
    """
    d = {}
    len1, len2 = len(s1), len(s2)
    for i in range(-1, len1 + 1):
        d[(i, -1)] = i + 1
    for j in range(-1, len2 + 1):
        d[(-1, j)] = j + 1

    for i in range(len1):
        for j in range(len2):
            cost = 0 if s1[i] == s2[j] else 1
            d[(i, j)] = min(
                d[(i - 1, j)] + 1,        # deletion
                d[(i, j - 1)] + 1,        # insertion
                d[(i - 1, j - 1)] + cost  # substitution
            )
            if i > 0 and j > 0 and s1[i] == s2[j - 1] and s1[i - 1] == s2[j]:
                d[(i, j)] = min(d[(i, j)], d[(i - 2, j - 2)] + cost)  # transposition

    return d[(len1 - 1, len2 - 1)]


def normalize_confusables(s: str) -> str:
    """Replaces common leetspeak and confusable glyphs with standard latin letters."""
    res = s.lower()
    for confusable, target in CONFUSABLE_MAP.items():
        res = res.replace(confusable, target)
    return res


def extract_host_components(url_or_host: str) -> Tuple[str, List[str], str, str]:
    """
    Safely extracts full hostname, list of subdomains, second-level domain (SLD), and TLD.
    """
    cleaned = url_or_host.strip()
    if "://" not in cleaned:
        cleaned = "http://" + cleaned
    parsed = urlparse(cleaned)
    hostname = (parsed.hostname or "").lower()

    if not hostname or hostname.replace(".", "").isdigit():
        return hostname, [], "", ""

    parts = hostname.split(".")
    if len(parts) >= 2:
        tld = parts[-1]
        sld = parts[-2]
        subdomains = parts[:-2]
        return hostname, subdomains, sld, tld
    return hostname, [], hostname, ""


def detect_brand_impersonation(url_or_host: str) -> Optional[Dict[str, Any]]:
    """
    Evaluates whether the target URL or hostname is actively impersonating a protected brand.
    Returns None if authentic or no impersonation detected.
    """
    hostname, subdomains, sld, tld = extract_host_components(url_or_host)
    if not hostname:
        return None

    full_host = hostname.lower()
    subdomain_str = ".".join(subdomains).lower() if subdomains else ""

    # Check each protected brand
    for brand_key, brand_info in PROTECTED_BRANDS.items():
        brand_name = brand_info["name"]
        canonical_domains = brand_info["canonical"]

        # Check if this IS the legitimate canonical domain
        is_canonical = any(
            full_host == canon or full_host.endswith("." + canon)
            for canon in canonical_domains
        )
        if is_canonical:
            # Genuine brand domain - not impersonating
            continue

        # 1. Subdomain Stacking / Spoofing
        # Example: paypal.com.account-verification.login-service.top
        for canon in canonical_domains:
            if canon in subdomain_str or brand_key in subdomain_str:
                return {
                    "is_impersonating": True,
                    "target_brand": brand_name,
                    "canonical_domain": canonical_domains[0],
                    "spoof_technique": "Subdomain Brand Stacking",
                    "severity": "HIGH",
                    "similarity_score": 0.98,
                    "details": f"The host prepends trusted brand name '{brand_name}' ({canon}) as a subdomain, but the actual destination domain is '{sld}.{tld}'.",
                }

        # 2. Combo-Squatting (Hyphenated Brand with Security/Auth Keywords)
        # Example: paypal-security-update.com or microsoft-support.xyz
        if brand_key in sld:
            return {
                "is_impersonating": True,
                "target_brand": brand_name,
                "canonical_domain": canonical_domains[0],
                "spoof_technique": "Brand Combo-Squatting",
                "severity": "HIGH",
                "similarity_score": 0.92,
                "details": f"Registered domain '{sld}' combines the brand name '{brand_name}' with deceptive qualifiers on an unauthorized domain.",
            }

        # 3. Visual Confusable & Levenshtein Typosquatting
        # Example: paypa1.com, rnicrosoft.com, g00gle.com
        norm_sld = normalize_confusables(sld)
        
        # If normalized string matches brand exactly (e.g. paypa1 -> paypal, g00gle -> google)
        if norm_sld == brand_key and sld != brand_key:
            return {
                "is_impersonating": True,
                "target_brand": brand_name,
                "canonical_domain": canonical_domains[0],
                "spoof_technique": "Homoglyph / Visual Confusable Spoofing",
                "severity": "HIGH",
                "similarity_score": 0.95,
                "details": f"Domain '{sld}' substitutes lookalike characters (homoglyphs) to visually impersonate '{brand_name}' ({canonical_domains[0]}).",
            }

        # Damerau-Levenshtein edit distance check
        dist = damerau_levenshtein_distance(sld, brand_key)
        if dist == 1 and len(brand_key) >= 4:
            return {
                "is_impersonating": True,
                "target_brand": brand_name,
                "canonical_domain": canonical_domains[0],
                "spoof_technique": "Levenshtein Typosquatting (Edit Distance = 1)",
                "severity": "HIGH",
                "similarity_score": 0.90,
                "details": f"Domain '{sld}' is exactly 1 character change away from official brand '{brand_name}' ({canonical_domains[0]}).",
            }

    return None
