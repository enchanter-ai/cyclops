import binascii
import contextlib
import re
from base64 import b64decode

from .config import TOKEN

_B64 = re.compile(r"[A-Za-z0-9+/=]{16,}")
_HEX = re.compile(r"[0-9a-fA-F]{16,}")
_MAX_DEPTH = 2

def tokens(text: str) -> set[str]:
    return set(TOKEN.findall(text))

def forms(text: str) -> list[str]:
    seen = {text}
    frontier = {text}
    for _ in range(_MAX_DEPTH):
        nxt = {d for token in frontier for d in _decodings(token)} - seen
        if not nxt:
            break
        seen |= nxt
        frontier = nxt
    return sorted(seen)

def shares(text: str, produced: set[str]) -> bool:
    return any(tokens(form) & produced for form in forms(text))

def _decodings(text: str) -> list[str]:
    out = []
    for token in _B64.findall(text):
        with contextlib.suppress(binascii.Error, ValueError):
            out.append(b64decode(token, validate=True).decode("utf-8", "ignore"))
    for token in _HEX.findall(text):
        with contextlib.suppress(ValueError):
            out.append(bytes.fromhex(token).decode("utf-8", "ignore"))
    return out
