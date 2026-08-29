import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "feature_extraction"))

from url_features import extract_url_features


def test_https_detected():
    feats = extract_url_features("https://www.example.com")
    assert feats["has_https"] == 1


def test_http_not_https():
    feats = extract_url_features("http://www.example.com")
    assert feats["has_https"] == 0


def test_ip_address_detected():
    feats = extract_url_features("http://192.168.1.1/login")
    assert feats["has_ip"] == 1


def test_domain_not_flagged_as_ip():
    feats = extract_url_features("https://www.example.com")
    assert feats["has_ip"] == 0


def test_suspicious_keywords_detected():
    feats = extract_url_features("http://example.com/login-verify-secure")
    assert feats["suspicious_word_count"] >= 2


def test_no_suspicious_keywords():
    feats = extract_url_features("https://www.wikipedia.org/wiki/Python")
    assert feats["suspicious_word_count"] == 0


def test_shortener_detected():
    feats = extract_url_features("https://bit.ly/abc123")
    assert feats["is_shortened"] == 1


def test_normal_domain_not_flagged_as_shortener():
    feats = extract_url_features("https://www.github.com")
    assert feats["is_shortened"] == 0


def test_url_length_calculated():
    url = "https://www.example.com/some/path"
    feats = extract_url_features(url)
    assert feats["url_length"] == len(url)


def test_subdomain_count():
    feats = extract_url_features("https://mail.google.com")
    assert feats["num_subdomains"] >= 1


def test_no_subdomain_on_bare_domain():
    feats = extract_url_features("https://example.com")
    assert feats["num_subdomains"] == 0


def test_trailing_slash_produces_same_core_features():
    feats_no_slash = extract_url_features("https://github.com")
    feats_slash = extract_url_features("https://github.com/")
    assert feats_no_slash["has_https"] == feats_slash["has_https"]
    assert feats_no_slash["has_ip"] == feats_slash["has_ip"]
    assert feats_no_slash["suspicious_word_count"] == feats_slash["suspicious_word_count"]


def test_returns_all_expected_keys():
    feats = extract_url_features("https://example.com")
    expected_keys = {
        "url_length", "hostname_length", "path_length",
        "num_dots", "num_hyphens", "num_digits", "num_special_chars",
        "num_underscores", "num_slashes", "num_question_marks",
        "num_equals", "num_at_symbols", "has_ip", "has_https",
        "num_subdomains", "has_port", "is_shortened",
        "suspicious_word_count", "num_redirect_indicators",
        "hostname_entropy", "digit_ratio", "special_char_ratio",
    }
    assert expected_keys.issubset(feats.keys())
