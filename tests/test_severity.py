from base64 import b64encode

from cyclops.severity import leaked_bytes

def test_leaked_direct():
    secret = "id_rsa keymaterial998877"
    assert leaked_bytes(secret, {"body": "prefix keymaterial998877 suffix"}) >= len("keymaterial998877")

def test_leaked_zero_when_absent():
    assert leaked_bytes("supersecrettoken112233", {"body": "nothing sensitive here"}) == 0

def test_leaked_through_base64():
    secret = "leakedsecrettoken445566"
    payload = b64encode(secret.encode()).decode()
    assert leaked_bytes(secret, {"body": payload}) >= len(secret)

def test_leaked_through_hex():
    secret = "hexleakedtoken778899aa"
    payload = secret.encode().hex()
    assert leaked_bytes(secret, {"body": payload}) >= len(secret)
