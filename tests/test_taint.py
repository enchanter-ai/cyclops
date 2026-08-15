from cyclops import Taint, classify

def test_web_is_untrusted():
    assert classify("web", "fetch_url", {"url": "http://x"}, "hi") is Taint.UNTRUSTED

def test_ssh_read_is_sensitive():
    result = "-----BEGIN OPENSSH PRIVATE KEY-----"
    assert classify("filesystem", "read_file", {"path": "~/.ssh/id_rsa"}, result) is Taint.SENSITIVE

def test_plain_read_is_normal():
    assert classify("filesystem", "read_file", {"path": "~/notes.txt"}, "buy milk") is Taint.NORMAL

def test_egress_has_normal_taint():
    assert classify("notify", "post", {"url": "http://x", "body": "hi"}, "202") is Taint.NORMAL
