"""
Automated Unit Tests for URL Feature Extraction & Risk Indicators
"""

import pytest
from ml.src.url_features import (
    extract_url_features, 
    extract_url_risk_indicators, 
    FEATURE_NAMES, 
    is_ip_address, 
    safe_parse_url
)


def test_feature_names_schema_completeness():
    """Ensure all required features are extracted."""
    url = "https://www.example.com/path?arg=1"
    features = extract_url_features(url)
    for name in FEATURE_NAMES:
        assert name in features, f"Missing feature {name} in output dictionary"
        assert isinstance(features[name], float), f"Feature {name} is not a float"


def test_malformed_url_safety():
    """Verify that malformed or strange inputs do not cause exceptions."""
    malformed_inputs = [
        "",
        "   ",
        "http://",
        "https://",
        "ftp:////",
        "://invalid",
        "12345",
        "%%%%%",
        "http://[::1]:8080/path",
        "a" * 1000,
        "http://example.com/path#fragment?query=1&arg=2",
        "http://-.-.-",
    ]
    for raw in malformed_inputs:
        feats = extract_url_features(raw)
        assert isinstance(feats, dict)
        assert len(feats) == len(FEATURE_NAMES)
        indicators = extract_url_risk_indicators(raw)
        assert isinstance(indicators, list)


def test_ip_address_detection():
    """Verify IPv4 and IPv6 detection."""
    assert is_ip_address("192.168.1.1") is True
    assert is_ip_address("10.0.0.1:8080") is True
    assert is_ip_address("127.0.0.1") is True
    assert is_ip_address("example.com") is False
    assert is_ip_address("paypal.com.account.com") is False
    assert is_ip_address("") is False

    feats = extract_url_features("http://192.168.1.100/login.php")
    assert feats["has_ip_address"] == 1.0


def test_punycode_detection():
    """Verify detection of internationalized punycode homograph attacks."""
    feats = extract_url_features("http://xn--apple-43a.com/verify")
    assert feats["has_punycode"] == 1.0


def test_subdomains_and_dots():
    """Verify subdomain and dot count logic."""
    feats_simple = extract_url_features("https://example.com")
    assert feats_simple["num_subdomains"] == 0.0

    feats_sub = extract_url_features("https://auth.login.verify.example.com")
    assert feats_sub["num_subdomains"] == 3.0


def test_risk_indicators_extraction():
    """Verify rule-based heuristic generation."""
    phish_url = "http://192.168.1.1:8080/paypal-login/verify.php?user=test"
    indicators = extract_url_risk_indicators(phish_url)
    ind_ids = [ind["id"] for ind in indicators]
    
    assert "IP_HOST" in ind_ids
    assert "NON_STANDARD_PORT" in ind_ids
    assert "NO_HTTPS" in ind_ids


def test_tokenize_url_structure():
    """Verify that URL visual syntax tokenization decomposes tokens with proper classification."""
    from ml.src.url_features import tokenize_url_structure
    
    url = "http://192.168.1.1:8080/secure/login.php?user=admin"
    tokens = tokenize_url_structure(url)
    assert len(tokens) >= 4
    
    types = [t["type"] for t in tokens]
    assert "scheme" in types
    assert "ip_host" in types
    assert "port" in types
    assert "path" in types
    
    # Check that IP host token is flagged suspicious
    ip_tok = next(t for t in tokens if t["type"] == "ip_host")
    assert ip_tok["is_suspicious"] is True
    assert ip_tok["severity"] == "HIGH"


def test_brand_impersonation_detection():
    """Verify homoglyph, combo-squatting, and subdomain stacking detection."""
    from ml.src.typosquatting import detect_brand_impersonation

    # 1. Authentic domain should not trigger
    res_auth = detect_brand_impersonation("https://www.paypal.com/signin")
    assert res_auth is None

    # 2. Homoglyph / Confusable
    res_homo = detect_brand_impersonation("http://paypa1.com/login")
    assert res_homo is not None
    assert res_homo["target_brand"] == "PayPal"
    assert "Homoglyph" in res_homo["spoof_technique"]

    # 3. Subdomain stacking
    res_stack = detect_brand_impersonation("http://paypal.com.verify-user.security-checkpoint.top")
    assert res_stack is not None
    assert res_stack["target_brand"] == "PayPal"
    assert "Subdomain" in res_stack["spoof_technique"]

    # 4. Combo-squatting
    res_combo = detect_brand_impersonation("https://microsoft-support-ticket.xyz")
    assert res_combo is not None
    assert res_combo["target_brand"] == "Microsoft"
    assert "Combo-Squatting" in res_combo["spoof_technique"]


def test_predict_url_with_ensemble_and_typosquatting():
    """Verify that predict_url populates brand_impersonation and ensemble_consensus."""
    from ml.src.predict import predict_url

    res = predict_url("http://paypa1.com/login.php")
    assert "brand_impersonation" in res
    assert res["brand_impersonation"] is not None
    assert res["brand_impersonation"]["target_brand"] == "PayPal"

    assert "ensemble_consensus" in res
    consensus = res["ensemble_consensus"]
    assert consensus["models_evaluated"] >= 1
    assert "models" in consensus
    assert len(consensus["models"]) >= 1
