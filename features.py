"""URL feature extraction for PhishGuard (fully offline)."""
import re
from urllib.parse import urlparse

SUSPICIOUS_WORDS = [
    "login", "verify", "update", "secure", "account", "bank", "paypal",
    "signin", "confirm", "password", "wallet", "free", "bonus", "urgent",
]
SHORTENERS = ("bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd", "ow.ly")
RISKY_TLDS = (".xyz", ".top", ".tk", ".ml", ".ga", ".cf", ".click", ".work")

FEATURE_NAMES = [
    "url_length", "num_dots", "num_hyphens", "num_digits", "has_at",
    "has_ip", "uses_https", "num_subdomains", "suspicious_words",
    "is_shortener", "risky_tld", "has_punycode", "path_length", "num_params",
]


def _normalize(url: str) -> str:
    url = url.strip()
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url):
        url = "http://" + url
    return url


def extract_features(url: str) -> dict:
    url = _normalize(url)
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    lowered = url.lower()
    parts = host.split(".") if host else []

    return {
        "url_length": len(url),
        "num_dots": url.count("."),
        "num_hyphens": host.count("-"),
        "num_digits": sum(c.isdigit() for c in host),
        "has_at": int("@" in url),
        "has_ip": int(bool(re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", host))),
        "uses_https": int(parsed.scheme == "https"),
        "num_subdomains": max(len(parts) - 2, 0),
        "suspicious_words": sum(w in lowered for w in SUSPICIOUS_WORDS),
        "is_shortener": int(host in SHORTENERS),
        "risky_tld": int(host.endswith(RISKY_TLDS)),
        "has_punycode": int("xn--" in host),
        "path_length": len(parsed.path),
        "num_params": len(parsed.query.split("&")) if parsed.query else 0,
    }


def explain(feats: dict) -> list:
    """Human-readable reasons a URL looks risky."""
    reasons = []
    if feats["has_ip"]:
        reasons.append("Uses a raw IP address instead of a domain name")
    if feats["has_at"]:
        reasons.append("Contains '@' which can hide the real destination")
    if not feats["uses_https"]:
        reasons.append("Does not use HTTPS")
    if feats["url_length"] > 75:
        reasons.append("Unusually long URL")
    if feats["num_subdomains"] >= 3:
        reasons.append("Too many subdomains")
    if feats["num_hyphens"] >= 2:
        reasons.append("Many hyphens in the domain")
    if feats["suspicious_words"] >= 2:
        reasons.append("Contains several phishing-style keywords")
    if feats["is_shortener"]:
        reasons.append("Uses a URL shortener that hides the destination")
    if feats["risky_tld"]:
        reasons.append("Uses a top-level domain often abused by scammers")
    if feats["has_punycode"]:
        reasons.append("Contains punycode (possible lookalike characters)")
    return reasons
