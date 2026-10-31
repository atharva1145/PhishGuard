"""
PhishGuard URL & Indicator Defanging Engine
Safely transforms live malicious indicators (URLs, domains, IPs, emails) into
defanged text strings to prevent accidental clicking in incident reports, Slack, or tickets.
"""

from __future__ import annotations
import re
from typing import Dict, Any


def defang_url(url: str) -> str:
    """
    Transforms an active URL into a defanged safe string.
    Examples:
        http://example.com/path -> hxxp://example[.]com/path
        https://192.168.1.1:8080/login -> hxxps://192[.]168[.]1[.]1:8080/login
    """
    if not url:
        return ""

    s = url.strip()

    # 1. Defang protocols
    if s.lower().startswith("https://"):
        s = "hxxps://" + s[8:]
    elif s.lower().startswith("http://"):
        s = "hxxp://" + s[7:]
    elif s.lower().startswith("ftp://"):
        s = "fxp://" + s[6:]

    # 2. Defang domain dots (replace dots in host/domain, while preserving path query if possible)
    # Match scheme + host portion
    m = re.match(r'^(hxxps?://|fxp://)?([^/?#]+)(.*)$', s, re.IGNORECASE)
    if m:
        scheme = m.group(1) or ""
        host = m.group(2)
        rest = m.group(3) or ""

        # Replace dots in host with [.]
        defanged_host = host.replace(".", "[.]")
        return f"{scheme}{defanged_host}{rest}"

    # Fallback: defang all dots
    return s.replace(".", "[.]")


def refang_url(defanged_url: str) -> str:
    """
    Reconstructs an active URL from a defanged string.
    Examples:
        hxxp://example[.]com/path -> http://example.com/path
        hxxps://192[.]168[.]1[.]1:8080/login -> https://192.168.1.1:8080/login
    """
    if not defanged_url:
        return ""

    s = defanged_url.strip()

    # 1. Refang protocol
    if s.lower().startswith("hxxps://") or s.lower().startswith("hxxps[://]"):
        s = "https://" + re.sub(r'^hxxps(\[://\]|://)', '', s, flags=re.I)
    elif s.lower().startswith("hxxp://") or s.lower().startswith("hxxp[://]"):
        s = "http://" + re.sub(r'^hxxp(\[://\]|://)', '', s, flags=re.I)
    elif s.lower().startswith("fxp://"):
        s = "ftp://" + s[6:]

    # 2. Refang bracketed dots
    s = s.replace("[.]", ".").replace("(.)", ".").replace("{.}", ".")

    # 3. Refang bracketed colons/slashes
    s = s.replace("[:]", ":").replace("[/]", "/")

    return s


def analyze_and_defang(url: str) -> Dict[str, Any]:
    """
    Returns both raw and defanged variants with SOC-formatted notation.
    """
    defanged = defang_url(url)
    return {
        "raw_url": url,
        "defanged_url": defanged,
        "is_defanged": "hxxp" in defanged or "[.]" in defanged,
        "soc_shareable_snippet": f"[DEFANGED IOC] {defanged}"
    }
