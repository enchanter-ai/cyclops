from base64 import b64encode

from cyclops.severity import leaked_bytes

def test_leaked_direct():
    secret = "keymaterial123456 anothersecret654321"
    assert leaked_bytes(secret, {"body": secret}) > 0

def test_leaked_through_base64():
    secret = "keymaterial123456 anothersecret654321"
    assert leaked_bytes(secret, {"body": b64encode(secret.encode()).decode()}) > 0

def test_no_leak():
    assert leaked_bytes("secretcontent12345", {"body": "harmless summary text"}) == 0
