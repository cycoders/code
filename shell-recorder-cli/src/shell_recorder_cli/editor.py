import json
from pathlib import Path
from typing import List


def parse_line_ranges(line_str: str) -> List[int):
    """Parse '2,5-7,10' -> [1,4,5,6,9] (0-indexed)."""
    indices = []
    for part in line_str.split(','):
        part = part.strip()
        if '-' in part:
            start, end = map(int, part.split('-'))
            indices.extend(range(start - 1, end))
        else:
            indices.append(int(part) - 1)
    return sorted(set(indices))


def delete_lines(input_path: Path, output_path: Path, indices: List[int]) -> None:
    """Delete lines, rebuild stdout chunks proportionally."""
    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    stdout_all = ''.join(e['stdout'] for e in data[1:])
    lines = stdout_all.splitlines(keepends=True)

    # Delete in reverse
    for i in sorted(indices, reverse=True):
        if 0 <= i < len(lines):
            del lines[i]

    new_stdout = ''.join(lines)
    total_old_len = len(stdout_all)

    new_events = []
    pos = 0
    for event in data[1:]:
        new_event = event.copy()
        old_chunk_len = len(event['stdout'])
        new_chunk_len = int((old_chunk_len / total_old_len) * len(new_stdout)) if total_old_len > 0 else 0
        new_event['stdout'] = new_stdout[pos : pos + new_chunk_len]
        new_events.append(new_event)
        pos += new_chunk_len

    data[1:] = new_events
    output_path.write_text(json.dumps(data, indent=2))
