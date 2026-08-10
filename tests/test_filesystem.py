from cyclops.servers.filesystem import _contained

def test_inside_sandbox_is_allowed():
    assert _contained("notes.txt") is not None

def test_parent_traversal_is_rejected():
    assert _contained("../../etc/passwd") is None

def test_sibling_prefix_is_rejected():
    assert _contained("../home_evil/secret") is None
