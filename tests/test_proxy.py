import pytest

from cyclops.proxy import _claim, _verify_sinks

def test_claim_registers_names():
    owner: dict[str, str] = {}
    _claim(owner, ["alpha", "beta"], "web")
    assert owner == {"alpha": "web", "beta": "web"}

def test_claim_rejects_duplicate_tool_name():
    owner: dict[str, str] = {}
    _claim(owner, ["dup"], "web")
    with pytest.raises(ValueError):
        _claim(owner, ["dup"], "filesystem")

def test_verify_sinks_passes_when_advertised():
    _verify_sinks({("notify", "post"), ("admin", "grant_access")})

def test_verify_sinks_rejects_unadvertised_sink():
    with pytest.raises(ValueError):
        _verify_sinks({("web", "fetch_url")})
