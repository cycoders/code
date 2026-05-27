import json
import sys
from .manager import ShutdownEvent

def emit(event: ShutdownEvent, **ctx):
    payload = {"event": event.value, "ts": __import__('time').time(), **ctx}
    print(json.dumps(payload), file=sys.stderr)