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
    out = demo("poisoned", Mode.PREVENT)
    assert "BLOCKED" in out
    assert "'blocked': 1" in out

def test_demo_detect_does_not_block():
    out = demo("poisoned", Mode.DETECT)
    assert "FLAGGED" in out
    assert "'blocked': 0" in out

def test_demo_benign_prevent_not_blocked():
    out = demo("benign", Mode.PREVENT)
    assert "no toxic flow" in out
    assert "'blocked': 0" in out

def test_demo_excessive_agency_is_red():
    out = demo("excessive-agency", Mode.DETECT)
    assert "RED" in out
    assert "EXCESSIVE_AGENCY" in out
    assert "LLM06:2025" in out
    assert "leaked" not in out

def test_demo_excessive_agency_prevent_blocks():
    out = demo("excessive-agency", Mode.PREVENT)
    assert "BLOCKED" in out
    assert "'blocked': 1" in out
