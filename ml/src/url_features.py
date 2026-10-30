"""
PhishGuard URL Feature Extractor
Extracts engineered lexical, structural, and semantic features from URLs locally.

SECURITY REQUIREMENT:
Never visit, fetch, execute, or send network packets to any submitted URL.
All parsing is performed strictly using local string manipulation and standard library URL parsing.
"""

from __future__ import annotations
import re
import ipaddress
from typing import Dict, Any, List, Tuple
from urllib.parse import urlparse, unquote


# Known public URL shortener domains (local list)
KNOWN_SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", 
    "buff.ly", "adf.ly", "bit.do", "cutt.ly", "rb.gy", "shorturl.at"
}

# TLDs historically associated with high abuse rates in phishing feeds
SUSPICIOUS_TLDS = {
    "xyz", "top", "buzz", "work", "tk", "ml", "ga", "cf", "gq", 
    "fit", "click", "cam", "bar", "rest", "party", "gdn", "date", "loan"
}

# Sensitive authentication/account keywords frequently used in phishing targets
SENSITIVE_KEYWORDS = [
    "login", "signin", "verify", "verification", "update", "secure", 
    "security", "account", "banking", "wallet", "confirm", "authenticate", 
    "support", "recovery", "password", "credential", "suspend", "unlock",
    "portal", "oauth", "validate", "billing", "invoice", "payment"
]

# Standard web ports
STANDARD_PORTS = {80, 443}

# Canonical feature schema list (order matters for consistent vectorization)
FEATURE_NAMES: List[str] = [
    "url_length",
    "hostname_length",
    "path_length",
    "query_length",
    "num_dots",
    "num_dots_hostname",
    "num_subdomains",
    "num_hyphens",
    "num_hyphens_hostname",
    "num_digits",
    "num_digits_hostname",
    "digit_ratio",
    "num_special_chars",
    "has_ip_address",
    "has_punycode",
    "is_https",
    "has_at_symbol",
    "has_suspicious_port",
    "num_percent_encoded",
    "has_shortener",
    "has_suspicious_tld",
    "num_sensitive_keywords",
    "has_prefix_suffix_in_host",
    "is_valid_url",
]


def is_ip_address(host: str) -> bool:
    """Check if host is an IPv4 or IPv6 address without making DNS calls."""
    if not host:
        return False
    # Strip port if present
    clean_host = host.split(":")[0].strip("[]")
    try:
        ipaddress.ip_address(clean_host)
        return True
    except ValueError:
        return False


def safe_parse_url(raw_url: str) -> Tuple[str, Any]:
    """
    Safely normalize and parse URL string.
    Prepends http:// if scheme is missing to allow urlparse to extract netloc reliably.
    """
    if not isinstance(raw_url, str):
        raw_url = str(raw_url)
    cleaned = raw_url.strip()
    
    # If no scheme given, add temporary http:// for parser
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+\-.]*://", cleaned):
        parsed = urlparse("http://" + cleaned)
        has_original_scheme = False
    else:
        parsed = urlparse(cleaned)
        has_original_scheme = True

    return cleaned, parsed, has_original_scheme


def extract_url_features(url_str: str) -> Dict[str, Any]:
    """
    Extract a dictionary of numerical/boolean features from a URL string.
    Guaranteed to return all keys in FEATURE_NAMES and never crash on malformed inputs.
    """
    cleaned_url, parsed, has_scheme = safe_parse_url(url_str)
    
    hostname = (parsed.hostname or "").lower()
    path = parsed.path or ""
    query = parsed.query or ""
    scheme = (parsed.scheme or "").lower()
    
    url_len = len(cleaned_url)
    host_len = len(hostname)
    path_len = len(path)
    query_len = len(query)

    dots_total = cleaned_url.count(".")
    dots_host = hostname.count(".")
    
    # Estimate subdomains (e.g., sub.domain.com -> 3 parts -> 1 subdomain)
    parts = hostname.split(".")
    num_subdomains = max(0, len(parts) - 2) if len(parts) >= 2 else 0

    hyphens_total = cleaned_url.count("-")
    hyphens_host = hostname.count("-")

    digits_total = sum(c.isdigit() for c in cleaned_url)
    digits_host = sum(c.isdigit() for c in hostname)
    digit_ratio = (digits_total / url_len) if url_len > 0 else 0.0

    special_chars = sum(cleaned_url.count(c) for c in ["@", "?", "=", "&", "_", "%", "+", "~", "#", "$", "!"])

    has_ip = 1 if is_ip_address(hostname) else 0
    has_punycode = 1 if "xn--" in hostname else 0
    is_https = 1 if scheme == "https" else 0
    has_at = 1 if "@" in cleaned_url else 0

    # Port checking
    has_suspicious_port = 0
    if parsed.port is not None and parsed.port not in STANDARD_PORTS:
        has_suspicious_port = 1

    percent_encoded = cleaned_url.count("%")
    has_shortener = 1 if hostname in KNOWN_SHORTENERS else 0

    # Extract TLD
    tld = parts[-1] if len(parts) > 1 else ""
    has_suspicious_tld = 1 if tld in SUSPICIOUS_TLDS else 0

    # Search for sensitive keywords in host and path
    url_lower = cleaned_url.lower()
    num_keywords = sum(1 for kw in SENSITIVE_KEYWORDS if kw in url_lower)

    # Prefix/suffix: check if hyphen is in domain (common in spoofed domains like `paypal-update`)
    has_prefix_suffix = 1 if "-" in hostname else 0

    is_valid = 1 if (host_len > 0 and "." in hostname) or has_ip == 1 else 0

    return {
        "url_length": float(url_len),
        "hostname_length": float(host_len),
        "path_length": float(path_len),
        "query_length": float(query_len),
        "num_dots": float(dots_total),
        "num_dots_hostname": float(dots_host),
        "num_subdomains": float(num_subdomains),
        "num_hyphens": float(hyphens_total),
        "num_hyphens_hostname": float(hyphens_host),
        "num_digits": float(digits_total),
        "num_digits_hostname": float(digits_host),
        "digit_ratio": float(digit_ratio),
        "num_special_chars": float(special_chars),
        "has_ip_address": float(has_ip),
        "has_punycode": float(has_punycode),
        "is_https": float(is_https),
        "has_at_symbol": float(has_at),
        "has_suspicious_port": float(has_suspicious_port),
        "num_percent_encoded": float(percent_encoded),
        "has_shortener": float(has_shortener),
        "has_suspicious_tld": float(has_suspicious_tld),
        "num_sensitive_keywords": float(num_keywords),
        "has_prefix_suffix_in_host": float(has_prefix_suffix),
        "is_valid_url": float(is_valid),
    }


def extract_url_risk_indicators(url_str: str) -> List[Dict[str, str]]:
    """
    Transparent heuristic risk indicators for explainability.
    Provides human-readable descriptions of why each indicator matters.
    """
    features = extract_url_features(url_str)
    cleaned_url, parsed, _ = safe_parse_url(url_str)
    hostname = (parsed.hostname or "").lower()
    
    indicators = []

    if features["has_ip_address"] == 1.0:
        indicators.append({
            "id": "IP_HOST",
            "name": "Direct IP Address Host",
            "severity": "HIGH",
            "description": "The URL uses a raw IP address instead of a registered domain name.",
            "evidence": f"Host is {hostname}",
            "rationale": "Legitimate organizations register descriptive domain names; attackers frequently use raw IP addresses to bypass domain reputation blocklists.",
        })

    if features["has_at_symbol"] == 1.0:
        indicators.append({
            "id": "AT_SYMBOL",
            "name": "Embedded '@' Symbol in URL",
            "severity": "HIGH",
            "description": "The URL contains an '@' symbol prior to the path.",
            "evidence": "Contains '@' token",
            "rationale": "In standard URL syntax, everything preceding an '@' symbol is treated as userinfo (credentials), causing the browser to connect to whatever follows it. Attackers exploit this to disguise destination domains.",
        })

    if features["has_punycode"] == 1.0:
        indicators.append({
            "id": "PUNYCODE",
            "name": "Punycode (Homograph Attack Indicator)",
            "severity": "HIGH",
            "description": "Domain contains 'xn--' internationalized character encoding.",
            "evidence": f"Punycode prefix found in {hostname}",
            "rationale": "Homograph attacks replace Latin letters with identical-looking Cyrillic or Greek glyphs to visually impersonate trusted brands.",
        })

    if features["num_subdomains"] >= 3.0:
        indicators.append({
            "id": "MULTIPLE_SUBDOMAINS",
            "name": "Excessive Subdomain Levels",
            "severity": "MEDIUM",
            "description": f"URL contains {int(features['num_subdomains'])} subdomain levels.",
            "evidence": f"Host structure: {hostname}",
            "rationale": "Phishing sites often stack recognized brand names as subdomains (e.g. paypal.com.verify-login.attacker.com) to deceive users reading left-to-right.",
        })

    if features["has_suspicious_tld"] == 1.0:
        indicators.append({
            "id": "SUSPICIOUS_TLD",
            "name": "High-Abuse Top-Level Domain",
            "severity": "MEDIUM",
            "description": "Domain is registered under a TLD commonly linked to automated phishing campaigns.",
            "evidence": f"TLD in {hostname}",
            "rationale": "Certain cheap or free top-level domains are heavily leveraged for disposable phishing campaigns due to minimal registrar identity verification.",
        })

    if features["has_prefix_suffix_in_host"] == 1.0 and features["num_sensitive_keywords"] > 0:
        indicators.append({
            "id": "BRAND_HYPHENATION",
            "name": "Hyphenated Domain with Sensitive Keywords",
            "severity": "MEDIUM",
            "description": "Hostname combines hyphens with security or authentication terms.",
            "evidence": f"Pattern in {hostname}",
            "rationale": "Attackers combine brand names with words like 'secure', 'support', or 'account' separated by hyphens (e.g. microsoft-support-update) to mimic official services.",
        })

    if features["has_suspicious_port"] == 1.0:
        indicators.append({
            "id": "NON_STANDARD_PORT",
            "name": "Non-Standard Web Port",
            "severity": "MEDIUM",
            "description": f"URL explicitly targets non-standard port {parsed.port}.",
            "evidence": f"Port: {parsed.port}",
            "rationale": "Legitimate customer-facing web services use default ports 80 (HTTP) or 443 (HTTPS). Alternative ports may indicate compromised or temporary staging servers.",
        })

    if features["has_shortener"] == 1.0:
        indicators.append({
            "id": "URL_SHORTENER",
            "name": "URL Shortener Domain",
            "severity": "LOW",
            "description": "URL routes through a link shortening service.",
            "evidence": f"Shortener service {hostname}",
            "rationale": "Shorteners mask the final destination URL, preventing users and basic filters from inspecting the true domain before following the link.",
        })

    if features["is_https"] == 0.0:
        indicators.append({
            "id": "NO_HTTPS",
            "name": "Insecure HTTP Protocol",
            "severity": "LOW",
            "description": "URL transmits data in plaintext without TLS encryption.",
            "evidence": "Scheme is http://",
            "rationale": "While lack of HTTPS does not prove malicious intent, modern sensitive login portals universally require HTTPS. Note: Many modern phishing sites now also obtain free TLS certificates, so HTTPS alone does not prove legitimacy.",
        })

    if features["num_percent_encoded"] >= 3.0:
        indicators.append({
            "id": "HEAVY_ENCODING",
            "name": "Excessive Percent-Encoding",
            "severity": "LOW",
            "description": "URL contains multiple percent-encoded (%xx) characters.",
            "evidence": f"{int(features['num_percent_encoded'])} encoded sequences",
            "rationale": "Percent-encoding is used to obscure malicious URLs, hidden redirection parameters, or script injections from pattern-matching filters.",
        })

    if features["url_length"] > 90.0:
        indicators.append({
            "id": "LONG_URL",
            "name": "Unusually Long URL",
            "severity": "LOW",
            "description": f"URL length is {int(features['url_length'])} characters.",
            "evidence": f"Length: {int(features['url_length'])}",
            "rationale": "Long URLs are often used to pack redirect URLs, stolen session tokens, or extensive tracking IDs that hide the true destination.",
        })

    return indicators


def tokenize_url_structure(url_str: str) -> List[Dict[str, Any]]:
    """
    Deconstructs a URL string into color-coded semantic tokens highlighting
    safe components vs suspicious anomalies (IP host, homographs, deceptive subdomains,
    high-abuse TLDs, non-standard ports, credential traps).
    """
    cleaned_url, parsed, has_scheme = safe_parse_url(url_str)
    tokens: List[Dict[str, Any]] = []

    # 1. Scheme
    scheme_str = (parsed.scheme or "").lower()
    if scheme_str:
        scheme_prefix = f"{scheme_str}://"
        if scheme_str == "https":
            tokens.append({
                "text": scheme_prefix,
                "type": "scheme",
                "is_suspicious": False,
                "severity": "SAFE",
                "tooltip": "Encrypted HTTPS scheme with TLS encryption."
            })
        elif scheme_str == "http":
            tokens.append({
                "text": scheme_prefix,
                "type": "scheme",
                "is_suspicious": True,
                "severity": "LOW",
                "tooltip": "Insecure HTTP protocol (unencrypted plaintext transmission)."
            })
        else:
            tokens.append({
                "text": scheme_prefix,
                "type": "scheme",
                "is_suspicious": True,
                "severity": "MEDIUM",
                "tooltip": f"Unusual protocol scheme: '{scheme_str}'."
            })

    # 2. Check for '@' symbol in netloc/authority (Userinfo credential trap)
    netloc = parsed.netloc or ""
    if "@" in netloc:
        userinfo_part, _, host_port_part = netloc.rpartition("@")
        tokens.append({
            "text": f"{userinfo_part}@",
            "type": "userinfo",
            "is_suspicious": True,
            "severity": "HIGH",
            "tooltip": "Credential '@' trap: Browser ignores preceding text and connects to the host that follows it."
        })
    else:
        host_port_part = netloc

    # Extract hostname and port
    hostname = (parsed.hostname or "").lower()
    port = parsed.port

    # 3. Hostname parsing
    if is_ip_address(hostname):
        tokens.append({
            "text": hostname,
            "type": "ip_host",
            "is_suspicious": True,
            "severity": "HIGH",
            "tooltip": "Raw IP address host. Phishers use IP addresses to bypass domain registration reputation systems."
        })
    elif "xn--" in hostname:
        tokens.append({
            "text": hostname,
            "type": "punycode",
            "is_suspicious": True,
            "severity": "HIGH",
            "tooltip": "Punycode (xn--) internationalized domain name: High risk of visual homograph brand spoofing."
        })
    elif hostname:
        parts = hostname.split(".")
        if len(parts) >= 2:
            tld = parts[-1]
            sld = parts[-2]
            subdomains = parts[:-2]

            # Subdomain tokens
            if subdomains:
                sub_str = ".".join(subdomains) + "."
                has_sub_kw = any(kw in sub_str.lower() for kw in SENSITIVE_KEYWORDS)
                is_sub_suspicious = has_sub_kw or len(subdomains) >= 2
                tokens.append({
                    "text": sub_str,
                    "type": "subdomain",
                    "is_suspicious": is_sub_suspicious,
                    "severity": "HIGH" if has_sub_kw else ("MEDIUM" if is_sub_suspicious else "SAFE"),
                    "tooltip": (
                        f"Deceptive subdomain stack: Contains sensitive keywords ({sub_str.rstrip('.')})."
                        if has_sub_kw else
                        (f"{len(subdomains)} subdomain level(s) prepended to root domain." if is_sub_suspicious else "Standard subdomain prefix.")
                    )
                })

            # SLD (root domain name)
            has_brand_hyphen = "-" in sld and any(kw in sld for kw in SENSITIVE_KEYWORDS)
            tokens.append({
                "text": sld,
                "type": "domain",
                "is_suspicious": has_brand_hyphen,
                "severity": "MEDIUM" if has_brand_hyphen else "SAFE",
                "tooltip": (
                    f"Hyphenated domain with sensitive security terms ('{sld}')."
                    if has_brand_hyphen else
                    f"Registered root domain name ('{sld}')."
                )
            })

            # TLD
            is_susp_tld = tld in SUSPICIOUS_TLDS
            tokens.append({
                "text": f".{tld}",
                "type": "tld",
                "is_suspicious": is_susp_tld,
                "severity": "MEDIUM" if is_susp_tld else "SAFE",
                "tooltip": (
                    f"High-abuse top-level domain (.{tld}) statistically common in disposable phishing campaigns."
                    if is_susp_tld else
                    f"Standard top-level domain (.{tld})."
                )
            })
        else:
            tokens.append({
                "text": hostname,
                "type": "domain",
                "is_suspicious": False,
                "severity": "INFO",
                "tooltip": "Single-token host."
            })

    # 4. Port
    if port is not None and port not in STANDARD_PORTS:
        tokens.append({
            "text": f":{port}",
            "type": "port",
            "is_suspicious": True,
            "severity": "MEDIUM",
            "tooltip": f"Non-standard web port ({port}). Typically standard web traffic uses port 80 or 443."
        })
    elif port is not None:
        tokens.append({
            "text": f":{port}",
            "type": "port",
            "is_suspicious": False,
            "severity": "SAFE",
            "tooltip": f"Standard web port ({port})."
        })

    # 5. Path
    path_str = parsed.path or ""
    if path_str and path_str != "/":
        has_kw_in_path = any(kw in path_str.lower() for kw in SENSITIVE_KEYWORDS)
        tokens.append({
            "text": path_str,
            "type": "path",
            "is_suspicious": has_kw_in_path,
            "severity": "LOW" if has_kw_in_path else "SAFE",
            "tooltip": (
                "Path contains authentication target keywords (e.g. login, verify, auth)."
                if has_kw_in_path else
                "Resource path."
            )
        })
    elif path_str == "/":
        tokens.append({
            "text": "/",
            "type": "path",
            "is_suspicious": False,
            "severity": "SAFE",
            "tooltip": "Root directory path."
        })

    # 6. Query String
    query_str = parsed.query or ""
    if query_str:
        has_heavy_pct = query_str.count("%") >= 3
        tokens.append({
            "text": f"?{query_str}",
            "type": "query",
            "is_suspicious": has_heavy_pct,
            "severity": "LOW" if has_heavy_pct else "SAFE",
            "tooltip": (
                "Query string contains heavy percent-encoding (%xx) that may conceal redirection targets."
                if has_heavy_pct else
                "Query string parameters."
            )
        })

    return tokens
