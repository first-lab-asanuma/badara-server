import base64
import json
from typing import Any, Dict


def encode_cursor(payload: Dict[str, Any]) -> str:
    data = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return base64.urlsafe_b64encode(data).decode("ascii")


def decode_cursor(token: str) -> Dict[str, Any]:
    try:
        # Adjust padding for base64url
        padding = '=' * (-len(token) % 4)
        raw = base64.urlsafe_b64decode((token + padding).encode("ascii"))
        obj = json.loads(raw.decode("utf-8"))
        if not isinstance(obj, dict):
            raise ValueError("cursor payload must be an object")
        return obj
    except Exception as e:
        raise ValueError("invalid cursor") from e

