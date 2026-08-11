import re
import tomllib
from pathlib import Path

from .enums import FlowClass, Server, Tool

_data = tomllib.loads((Path(__file__).parent / "patterns.toml").read_text(encoding="utf-8"))
UNTRUSTED_SERVERS = frozenset(Server(s) for s in _data["untrusted_servers"])
SENSITIVE_SERVERS = frozenset(Server(s) for s in _data["sensitive_servers"])
SENSITIVE_PATHS = tuple(_data["sensitive_paths"])
SECRET_MARKERS = tuple(_data["secret_markers"])
EGRESS = frozenset((Server(s), Tool(t)) for s, t in _data["egress"])
PRIVILEGED = frozenset((Server(s), Tool(t)) for s, t in _data["privileged"])
OWASP = {FlowClass(k): str(v) for k, v in _data["owasp"].items()}
TOKEN = re.compile(_data["token_regex"])
