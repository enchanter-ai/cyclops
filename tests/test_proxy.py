import pytest

from cyclops.enums import Server
from cyclops.proxy import _claim

def test_claim_registers_names():
    owner = {}
    _claim(owner, ["alpha", "beta"], Server.WEB)
    assert owner == {"alpha": Server.WEB, "beta": Server.WEB}

def test_claim_rejects_duplicate_tool_name():
    owner = {}
    _claim(owner, ["dup"], Server.WEB)
    with pytest.raises(ValueError):
        _claim(owner, ["dup"], Server.FILESYSTEM)
