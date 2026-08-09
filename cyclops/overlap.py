import binascii
import contextlib
import re
from base64 import b64decode

from .config import TOKEN

_ENCODED = re.compile(r"[A-Za-z0-9+/=]{16,}")

def tokens(text: str) -> set[str]:
    return set(TOKEN.findall(text))

def forms(text: str) -> list[str]:
    return [text, *_decodings(text)]

def shares(text: str, produced: set[str]) -> bool:
    return any(tokens(form) & produced for form in forms(text))

def _decodings(text: str) -> list[str]:
    out = []
    for token in _ENCODED.findall(text):
        with contextlib.suppress(binascii.Error, ValueError):
            out.append(b64decode(token, validate=True).decode("utf-8", "ignore"))
    return out
