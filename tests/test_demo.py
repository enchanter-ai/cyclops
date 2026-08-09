from cyclops.cli import demo
from cyclops.enums import Mode

def test_demo_benign_is_green():
    assert "GREEN" in demo("benign", Mode.DETECT)

def test_demo_poisoned_is_red():
    out = demo("poisoned", Mode.DETECT)
    assert "RED" in out
    assert "leaked" in out

def test_demo_encoded_is_caught():
    assert "RED" in demo("poisoned-encoded", Mode.DETECT)

def test_demo_prevent_blocks():
    assert "BLOCKED" in demo("poisoned", Mode.PREVENT)
