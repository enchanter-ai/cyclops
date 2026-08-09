from typing import Any

from .overlap import forms, tokens

def leaked_bytes(secret: str, sink_args: dict[str, Any]) -> int:
    produced = tokens(secret)
    if not produced:
        return 0
    payload = " ".join(str(v) for v in sink_args.values())
    return max((sum(len(t) for t in produced & tokens(form)) for form in forms(payload)), default=0)
