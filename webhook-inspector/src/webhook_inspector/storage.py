import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class Storage:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._today_file = self._get_today_file()

    def _get_today_file(self) -> Path:
        today = datetime.now().strftime("%Y-%m-%d.jsonl")
        return self.base_dir / today

    def save(self, req_id: str, data: Dict[str, Any]) -> None:
        """Append request to JSONL."""
        entry = {
            "id": req_id,
            "timestamp": datetime.utcnow().isoformat(),
            **data,
        }
        self._today_file.write_text(json.dumps(entry) + "\n", mode="a", encoding="utf-8")

    def get(self, req_id: str) -> Optional[Dict[str, Any]]:
        """Fetch by ID (simple scan for demo)."""
        for line in self._today_file.read_text().splitlines():
            entry = json.loads(line)
            if entry["id"] == req_id:
                return entry
        return None

    def list(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Recent requests."""
        lines = self._today_file.read_text().splitlines()
        return [json.loads(line) for line in lines[-limit:]]

    def stats(self) -> Dict[str, int]:
        """Basic stats."""
        count = 0
        verified = 0
        for line in self._today_file.read_text().splitlines():
            data = json.loads(line)
            count += 1
            if data.get("signature_verified"):
                verified += 1
        return {"total": count, "verified": verified}
