from __future__ import annotations
import json
from pathlib import Path
from threading import Lock
try:
    from .models import AuditEvent
except ImportError:
    from models import AuditEvent
AUDIT_PATH = Path(__file__).resolve().parents[1] / 'output' / 'audit_trail.json'
_LOCK = Lock()
def append_event(event: AuditEvent) -> None:
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _LOCK:
        try: existing = json.loads(AUDIT_PATH.read_text()) if AUDIT_PATH.exists() else []
        except (json.JSONDecodeError, OSError): existing = []
        if not isinstance(existing, list): existing = [existing]
        existing.append(event.model_dump(mode='json')); AUDIT_PATH.write_text(json.dumps(existing, indent=2)+'\n')
