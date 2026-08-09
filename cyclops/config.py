import re
import tomllib
from pathlib import Path

from .enums import Server, Tool

_data = tomllib.loads((Path(__file__).parent / "patterns.toml").read_text(encoding="utf-8"))
UNTRUSTED_SERVERS = frozenset(Server(s) for s in _data["untrusted_servers"])
SENSITIVE_SERVERS = frozenset(Server(s) for s in _data["sensitive_servers"])
SENSITIVE_PATHS = tuple(_data["sensitive_paths"])
SECRET_MARKERS = tuple(_data["secret_markers"])
EGRESS = frozenset((Server(s), Tool(t)) for s, t in _data["egress"])
TOKEN = re.compile(_data["token_regex"])
ROOT = next((p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").exists()), Path.cwd())
