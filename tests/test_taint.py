from cyclops import Server, Taint, Tool, classify

def test_web_is_untrusted():
    assert classify(Server.WEB, Tool.FETCH_URL, {"url": "http://x"}, "hi") is Taint.UNTRUSTED

def test_ssh_read_is_sensitive():
    result = "-----BEGIN OPENSSH PRIVATE KEY-----"
    assert classify(Server.FILESYSTEM, Tool.READ_FILE, {"path": "~/.ssh/id_rsa"}, result) is Taint.SENSITIVE

def test_plain_read_is_normal():
    assert classify(Server.FILESYSTEM, Tool.READ_FILE, {"path": "~/notes.txt"}, "buy milk") is Taint.NORMAL

def test_egress_has_normal_taint():
    assert classify(Server.NOTIFY, Tool.POST, {"url": "http://x", "body": "hi"}, "202") is Taint.NORMAL
