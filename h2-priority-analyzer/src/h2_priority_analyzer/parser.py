import json
from pathlib import Path
from typing import Iterator, List, Dict, Optional
from rich.progress import Progress

from .models import NetlogEvent, Stream, PriorityInfo


def parse_netlog(file_path: Path) -> List[Stream]:
    """Parse Chrome netlog JSONL into streams dict."""

    streams: Dict[int, Stream] = {}

    with Progress() as progress:
        task = progress.add_task("Parsing events...", total=None)
        with file_path.open() as f:
            for line_num, line in enumerate(f, 1):
                try:
                    event = NetlogEvent.model_validate_json(line)
                    stream_id = event.source.get("id")
                    if not isinstance(stream_id, int):
                        continue

                    if event.type == "HTTP2_STREAM_RECV_PRIORITY":
                        prio = PriorityInfo(
                            dependency=event.params.get("dependency", 0),
                            weight=event.params.get("weight", 201),
                            exclusive=event.params.get("exclusive", False),
                        )
                        if stream_id not in streams:
                            streams[stream_id] = Stream(id=stream_id)
                        streams[stream_id].priority = prio

                    elif event.type == "URL_REQUEST_STARTED":
                        if stream_id not in streams:
                            streams[stream_id] = Stream(id=stream_id)
                        streams[stream_id].url = event.params.get("url")
                        streams[stream_id].start_time = event.time
                        streams[stream_id].content_type = event.params.get("original_url").split(".")[-1].upper() if event.params.get("original_url") else None

                    elif event.type == "URL_REQUEST_COMPLETED":
                        if stream_id in streams and streams[stream_id].end_time is None:
                            streams[stream_id].end_time = event.time
                            streams[stream_id].duration = (event.time - streams[stream_id].start_time) / 1000 if streams[stream_id].start_time else 0

                except json.JSONDecodeError:
                    print(f"Warning: Invalid JSON at line {line_num}")
                except Exception as e:
                    print(f"Warning: Parse error at line {line_num}: {e}")
                progress.update(task, advance=0.01)

    # Compute durations
    for stream in streams.values():
        if stream.duration is None and stream.start_time:
            stream.duration = 0

    return sorted([s for s in streams.values() if s.duration and s.duration > 0], key=lambda s: s.start_time or 0)
