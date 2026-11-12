from features import extract_features, explain


def test_at_symbol_flagged():
    f = extract_features("http://192.168.1.1@evil.com/login")
    assert f["has_at"] == 1


def test_ip_host():
    assert extract_features("http://192.168.1.1/login")["has_ip"] == 1


def test_https_safe_site():
    f = extract_features("https://github.com")
    assert f["uses_https"] == 1 and explain(f) == []
