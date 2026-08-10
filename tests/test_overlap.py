from base64 import b64encode

from cyclops.overlap import forms, shares, tokens

def test_shares_direct():
    assert shares("the path is id_rsa here", tokens("please read id_rsa now"))

def test_shares_through_base64():
    secret = "SUPERSECRETtokenmaterial123456"
    assert shares(b64encode(secret.encode()).decode(), tokens(secret))

def test_shares_through_hex():
    secret = "HEXSECRETmaterial7788990011"
    assert shares(secret.encode().hex(), tokens(secret))

def test_shares_through_nested_base64():
    secret = "NESTEDsecrettoken44556677"
    once = b64encode(secret.encode()).decode()
    twice = b64encode(once.encode()).decode()
    assert shares(twice, tokens(secret))

def test_invalid_hex_does_not_raise():
    assert isinstance(forms("abcdef1234567890a and other text"), list)

def test_no_share():
    assert not shares("totally unrelated wording", tokens("different content entirely"))
