import requests
import time
from typing import List, Dict, Any
from rich.progress import Progress

class CTClient:
    BASE_URL = "https://crt.sh"

    def __init__(self, timeout: int = 10, retries: int = 3):
        self.session = requests.Session()
        self.timeout = timeout
        self.retries = retries

    def search(self, query: str, output_format: str = "json") -> List[Dict[str, Any]]:
        url = f"{self.BASE_URL}/?q={requests.utils.quote(query)}&output={output_format}"
        for attempt in range(self.retries):
            try:
                with Progress() as progress:
                    task = progress.add_task("[cyan]Fetching CT logs...", total=None)
                    resp = self.session.get(url, timeout=self.timeout)
                    progress.remove_task(task)
                resp.raise_for_status()
                data = resp.json()
                if isinstance(data, list):
                    return data
                else:
                    raise ValueError(f"Unexpected data format: {type(data)}")
            except Exception as e:
                if attempt < self.retries - 1:
                    wait = 2 ** attempt + (attempt * 0.5)
                    time.sleep(wait)
                    continue
                raise RuntimeError(f"Failed after {self.retries} retries: {e}")

    def fetch_pem(self, cert_id: int) -> str:
        url = f"{self.BASE_URL}/{cert_id}.pem"
        resp = self.session.get(url, timeout=self.timeout)
        resp.raise_for_status()
        return resp.text