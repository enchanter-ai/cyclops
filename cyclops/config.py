import os
import re
import tomllib
from collections.abc import Iterable
from pathlib import Path

from .enums import FlowClass

_PATTERNS = Path(os.environ.get("CYCLOPS_PATTERNS", str(Path(__file__).parent / "patterns.toml")))
_data = tomllib.loads(_PATTERNS.read_text(encoding="utf-8"))
UNTRUSTED_SERVERS = frozenset(str(s) for s in _data["untrusted_servers"])
SENSITIVE_SERVERS = frozenset(str(s) for s in _data["sensitive_servers"])
SENSITIVE_PATHS = tuple(_data["sensitive_paths"])
SECRET_MARKERS = tuple(_data["secret_markers"])
EGRESS = frozenset((str(s), str(t)) for s, t in _data["egress"])
PRIVILEGED = frozenset((str(s), str(t)) for s, t in _data["privileged"])
OWASP = {FlowClass(k): str(v) for k, v in _data["owasp"].items()}
TOKEN = re.compile(_data["token_regex"])

def referenced_servers() -> frozenset[str]:
    sinks = {s for s, _ in EGRESS} | {s for s, _ in PRIVILEGED}
    return frozenset(UNTRUSTED_SERVERS | SENSITIVE_SERVERS | sinks)

def assert_closure(declared: Iterable[str]) -> None:
    missing = referenced_servers() - set(declared)
    if missing:
        raise ValueError(f"patterns.toml references servers not declared in downstream.toml: {sorted(missing)}")
