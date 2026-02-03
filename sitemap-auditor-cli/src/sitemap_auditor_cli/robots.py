from typing import List


def parse_robots(text: str) -> List[str]:
    """Parse robots.txt for Disallow paths under User-agent: *."""
    disallows: List[str] = []
    in_star_section = False
    for line in text.splitlines():
        line = line.strip()
        if line.lower().startswith("user-agent: "):
            ua = line[11:].strip().lower()
            in_star_section = ua == "*"
        elif in_star_section and line.lower().startswith("disallow: "):
            disallow_path = line[9:].strip()
            if disallow_path:
                disallows.append(disallow_path)
    return disallows


import aiohttp

async def get_disallow_paths(session: aiohttp.ClientSession, base_url: str) -> List[str]:
    """Fetch and parse robots.txt disallow paths."""
    robots_url = f"{base_url.rstrip('/')}/robots.txt"
    try:
        async with session.get(robots_url, timeout=aiohttp.ClientTimeout(total=5.0)) as resp:
            if resp.status == 200:
                text = await resp.text()
                return parse_robots(text)
    except Exception:
        pass  # Ignore errors, treat as no restrictions
    return []