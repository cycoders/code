from typing import Dict, List, Tuple
from collections import defaultdict, deque

from .models import Stream, BlockingChain


class PriorityGraph:
    """Builds and analyzes HTTP/2 priority graph."""

    def __init__(self, streams: List[Stream]):
        self.streams = {s.id: s for s in streams}
        self.adj: Dict[int, List[int]] = defaultdict(list)  # parent -> children
        self._build_graph()

    def _build_graph(self) -> None:
        for stream in self.streams.values():
            dep = stream.priority.dependency
            if dep != 0 and dep in self.streams:
                self.adj[dep].append(stream.id)

    def compute_levels(self) -> Dict[int, int]:
        """BFS level by dependency depth."""
        levels = {}
        queue = deque([sid for sid in self.streams if self.streams[sid].priority.dependency == 0])
        level = 0
        while queue:
            for _ in range(len(queue)):
                sid = queue.popleft()
                levels[sid] = level
                for child in self.adj[sid]:
                    queue.append(child)
            level += 1
        return levels

    def find_longest_chains(self, max_chains: int = 5) -> List[BlockingChain]:
        """DFS to find top blocking chains (sum durations)."""
        chains = []

        def dfs(sid: int, path: List[int], block_ms: float) -> None:
            path.append(sid)
            block_ms += self.streams[sid].duration or 0
            if len(path) > 1:
                chains.append(BlockingChain(streams=path[:], total_block_ms=block_ms))
            for child in self.adj[sid]:
                dfs(child, path, block_ms)
            path.pop()

        for root in [sid for sid, s in self.streams.items() if s.priority.dependency == 0]:
            dfs(root, [], 0)

        return sorted(chains, key=lambda c: c.total_block_ms, reverse=True)[:max_chains]

    def suggestions(self) -> List[str]:
        levels = self.compute_levels()
        chains = self.find_longest_chains()
        sugg = []
        if chains:
            top_chain = chains[0]
            sugg.append(f"Longest chain ({len(top_chain.streams)} streams) blocks {top_chain.total_block_ms:.0f}ms: {', '.join(str(s) for s in top_chain.streams)}")
        deep = max(levels.values()) if levels else 0
        if deep > 3:
            sugg.append(f"High depth {deep}: Flatten tree by promoting low-weight leaves.")
        low_img = [s.id for s, l in zip(self.streams.values(), levels.values()) if "IMG" in (s.content_type or "") and l > 2]
        if low_img:
            sugg.append(f"Images at low prio (depth>2): Bump IDs {low_img}")
        return sugg
