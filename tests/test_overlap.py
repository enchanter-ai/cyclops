from base64 import b64encode

from cyclops.overlap import shares, tokens

def test_shares_direct():
    assert shares("the path is id_rsa here", tokens("please read id_rsa now"))

def test_shares_through_base64():
    secret = "SUPERSECRETtokenmaterial123456"
    assert shares(b64encode(secret.encode()).decode(), tokens(secret))

def test_no_share():
    assert not shares("totally unrelated wording", tokens("different content entirely"))
