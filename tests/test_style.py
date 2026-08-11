import tokenize
from pathlib import Path

_SOURCES = sorted(Path("cyclops").rglob("*.py")) + sorted(Path("tests").rglob("*.py"))

def test_sources_found():
    assert _SOURCES

def test_no_comments_in_source():
    for path in _SOURCES:
        with tokenize.open(path) as handle:
            comments = [t for t in tokenize.generate_tokens(handle.readline) if t.type == tokenize.COMMENT]
        assert not comments, f"{path} contains comments"

def test_no_double_blank_lines():
    for path in _SOURCES:
        assert "\n\n\n" not in path.read_text(encoding="utf-8"), f"{path} has double blank lines"
