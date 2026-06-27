from __future__ import annotations
import json, logging, sys
from datetime import datetime, timezone
from app.core.redaction import redact_text, redact_mapping
class JSONFormatter(logging.Formatter):
    def format(self, record):
        payload={"ts":datetime.now(timezone.utc).isoformat(),"level":record.levelname,"logger":record.name,"message":redact_text(record.getMessage())}
        return json.dumps(redact_mapping(payload))
def configure_logging():
    handler=logging.StreamHandler(sys.stdout); handler.setFormatter(JSONFormatter())
    logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)
