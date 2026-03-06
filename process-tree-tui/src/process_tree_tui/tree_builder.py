from collections import defaultdict
from typing import Dict

import psutil
from textual.widgets import Tree

from .utils import format_node


def populate_tree(tree: Tree, search_term: str = "") -> None:
    """Build and populate process tree, filtered by search. Clears existing."""
    tree.clear()

    # Gather live processes
    procs: Dict[int, psutil.Process] = {}
    attrs = [
        "pid",
        "ppid",
        "name",
        "cpu_percent",
        "memory_percent",
        "cmdline",
        "create_time",
        "status",
    ]
    for p in psutil.process_iter(attrs=attrs):
        try:
            info = p.info
            if search_term:
                term_lower = search_term.lower()
                if (
                    term_lower not in info["name"].lower()
                    and term_lower not in " ".join(info["cmdline"]).lower()
                ):
                    continue
            procs[info["pid"]] = p
        except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
            continue

    if not procs:
        tree.root.add_leaf("[bold]No processes found[/bold]")
        return

    # Build children map
    children_map: Dict[int, list[int]] = defaultdict(list)
    for pid, p in procs.items():
        ppid = p.ppid()
        if ppid and ppid in procs:
            children_map[ppid].append(pid)

    # Roots (top-level)
    roots = [pid for pid in procs if procs[pid].ppid() not in procs]
    roots.sort(key=lambda pid: procs[pid].create_time())

    for root_pid in roots:
        try:
            p = procs[root_pid]
            label = format_node(p)
            node = tree.root.add_leaf(label, str(root_pid))  # Will expand if children
            _populate_children(tree, node, procs, children_map)
        except Exception:
            continue


def _populate_children(
    tree: Tree,
    parent_node: Tree.Node,
    procs: Dict[int, psutil.Process],
    children_map: Dict[int, list[int]],
) -> None:
    """Recursively add children."""
    pid = int(parent_node.id)
    if pid not in procs:
        return

    child_pids = children_map.get(pid, [])
    child_pids.sort(key=lambda cp: procs[cp].create_time())

    for child_pid in child_pids:
        try:
            p = procs[child_pid]
            label = format_node(p)
            child_node = parent_node.add_leaf(label, str(child_pid))
            _populate_children(tree, child_node, procs, children_map)
        except (KeyError, psutil.NoSuchProcess, psutil.AccessDenied):
            pass