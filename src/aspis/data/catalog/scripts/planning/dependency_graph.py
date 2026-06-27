#!/usr/bin/env python3
"""Build a dependency graph from TASKS.md — DOT output, ASCII tree, cycle detection.

Purpose: Parse one or more TASKS.md files, extract "Depends on:" and "Blocks:"
declarations, build a directed acyclic graph (DAG), detect circular
dependencies, and output the graph in DOT format or as an ASCII tree.

Does Not: Resolve dependencies — only parses declared relationships.
Does not modify any files.

Used By: planning-lead (dependency analysis), dependency-analyzer subagent (L3).

Stdlib-only. Deterministic. --help shows usage.

Usage:
  python dependency_graph.py <TASKS.md> [<TASKS.md> ...]
  python dependency_graph.py <TASKS.md> --format dot
  python dependency_graph.py <TASKS.md> --format tree
  python dependency_graph.py <TASKS.md> --check-cycles
  python dependency_graph.py --help
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from collections import defaultdict


def parse_dependencies(text: str, source_file: str = "") -> dict[str, dict]:
    """Parse task dependencies and metadata from TASKS.md text.

    Returns dict keyed by task ID, each with: depends_on, blocks, layer, priority, description.
    """
    tasks = {}
    blocks = re.split(r"\n(?=- \[ \] T-)", text)

    for block in blocks:
        task_match = re.search(r"T-(\d+[a-z]?)", block[:100])
        if not task_match:
            continue

        tid = f"T-{task_match.group(1)}"

        # Extract Depends on: (stop at | or newline)
        depends = set()
        dep_match = re.search(r"Depends on:\s*([^|\n]+)", block)
        if dep_match:
            deps_text = dep_match.group(1).strip()
            if deps_text.lower() != "none":
                depends = set(re.findall(r"T-\d+[a-z]?", deps_text))

        # Extract Blocks: (stop at | or newline)
        blocks_set = set()
        block_match = re.search(r"Blocks:\s*([^|\n]+)", block)
        if block_match:
            blocks_text = block_match.group(1).strip()
            if blocks_text.lower() != "none":
                blocks_set = set(re.findall(r"T-\d+[a-z]?", blocks_text))

        # Extract layer
        layer = ""
        layer_match = re.search(r"###\s+(L\d)", block)
        if layer_match:
            layer = layer_match.group(1)

        # Extract priority
        priority = "P2"
        for p in ["P0", "P1", "P2"]:
            if re.search(rf"\[{p}\]", block[:200]):
                priority = p
                break

        # Extract description
        desc_match = re.search(r"—\s*(.+?)(?:\n|$)", block[:200])
        desc = desc_match.group(1).strip() if desc_match else tid

        tasks[tid] = {
            "depends_on": depends,
            "blocks": blocks_set,
            "layer": layer,
            "priority": priority,
            "description": desc,
            "source": source_file,
        }

    return tasks


def detect_cycles(tasks: dict[str, dict]) -> list[list[str]]:
    """Detect circular dependencies using DFS. Returns list of cycles."""
    cycles = []
    visited = set()
    path = []

    def dfs(node):
        if node in path:
            cycle_start = path.index(node)
            cycles.append(path[cycle_start:] + [node])
            return
        if node in visited:
            return
        visited.add(node)
        path.append(node)
        for neighbor in tasks.get(node, {}).get("depends_on", set()):
            if neighbor in tasks:
                dfs(neighbor)
        path.pop()

    for node in tasks:
        dfs(node)

    # Deduplicate cycles (same cycle, different starting point)
    unique = []
    seen = set()
    for cycle in cycles:
        # Normalize: find canonical rotation
        n = len(cycle) - 1
        canonical = min(
            tuple(cycle[i:] + cycle[1:i+1]) for i in range(n)
        )
        if canonical not in seen:
            seen.add(canonical)
            unique.append(cycle)

    return unique


def compute_layers(tasks: dict[str, dict]) -> dict[str, int]:
    """Compute topological layers for each task using Kahn's algorithm."""
    in_degree = defaultdict(int)
    adj = defaultdict(set)

    for tid, info in tasks.items():
        for dep in info.get("depends_on", set()):
            if dep in tasks:
                adj[dep].add(tid)
                in_degree[tid] += 1
        if tid not in in_degree:
            in_degree[tid] = 0

    # Kahn's algorithm
    layers = {}
    queue = [tid for tid in tasks if in_degree[tid] == 0]
    current_layer = 0

    while queue:
        next_queue = []
        for tid in queue:
            layers[tid] = current_layer
            for neighbor in adj[tid]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    next_queue.append(neighbor)
        queue = next_queue
        current_layer += 1

    # Any remaining -> part of a cycle
    for tid in tasks:
        if tid not in layers:
            layers[tid] = -1

    return layers


def format_dot(tasks: dict[str, dict], layers: dict[str, int]) -> str:
    """Format graph as DOT for Graphviz."""
    lines = ["digraph G {", "  rankdir=TB;", "  node [shape=box, style=rounded];"]
    lines.append("")

    # Group by layer
    layer_groups = defaultdict(list)
    for tid, layer in layers.items():
        layer_groups[layer].append(tid)

    for layer_num in sorted(layer_groups):
        tids = layer_groups[layer_num]
        label = f"Layer {layer_num}" if layer_num >= 0 else "Cycle"
        lines.append(f"  subgraph cluster_{layer_num} {{")
        lines.append(f'    label="{label}";')
        for tid in sorted(tids):
            desc = tasks[tid]["description"][:40]
            lines.append(f'    "{tid}" [label="{tid}\\n{desc}"];')
        lines.append("  }")

    # Edges
    lines.append("")
    for tid, info in tasks.items():
        for dep in info.get("depends_on", set()):
            if dep in tasks:
                lines.append(f'  "{tid}" -> "{dep}";')

    lines.append("}")
    return "\n".join(lines)


def format_tree(tasks: dict[str, dict], layers: dict[str, int]) -> str:
    """Format graph as an ASCII tree."""
    lines = []
    lines.append("Dependency Tree")
    lines.append("=" * 60)

    # Find roots (layer 0)
    roots = sorted(tid for tid, layer in layers.items() if layer == 0)

    def render_tree(tid, prefix="", is_last=True, ancestors=None):
        if ancestors is None:
            ancestors = set()
        if tid in ancestors:
            return  # prevent infinite loops from cycles

        info = tasks.get(tid, {})
        connector = "`-- " if is_last else "|-- "
        desc = info.get("description", tid)[:50]
        prio = info.get("priority", "")
        lines.append(f"{prefix}{connector}{tid} [{prio}] {desc}")

        children = sorted(
            [c for c in tasks if tid in tasks[c].get("depends_on", set())],
            key=lambda c: layers.get(c, 99)
        )
        new_prefix = prefix + ("    " if is_last else "|   ")
        for i, child in enumerate(children):
            render_tree(child, new_prefix, i == len(children) - 1, ancestors | {tid})

    if roots:
        lines.append("Roots:")
        for i, root in enumerate(roots):
            render_tree(root, "", i == len(roots) - 1)
    else:
        lines.append("No root tasks found (possible cycles).")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a dependency graph from TASKS.md files."
    )
    parser.add_argument(
        "tasks_paths", nargs="*", default=None, help="one or more TASKS.md paths"
    )
    parser.add_argument(
        "--format", choices=["dot", "tree", "json"], default="tree",
        help="output format (default: tree)"
    )
    parser.add_argument(
        "--check-cycles", action="store_true", help="only check for cycles, exit 1 if found"
    )
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    if not args.tasks_paths:
        print("error: at least one TASKS.md path required", file=sys.stderr)
        parser.print_help()
        return 1

    all_tasks = {}
    for p in args.tasks_paths:
        path = Path(p)
        if not path.exists():
            print(f"error: file not found: {p}", file=sys.stderr)
            return 1
        text = path.read_text(encoding="utf-8")
        tasks = parse_dependencies(text, str(path))
        all_tasks.update(tasks)

    if not all_tasks:
        print("No tasks found in input files.")
        return 1

    cycles = detect_cycles(all_tasks)
    layers = compute_layers(all_tasks)

    if args.check_cycles:
        if cycles:
            print(f"CIRCULAR DEPENDENCIES FOUND ({len(cycles)}):")
            for c in cycles:
                print(f"  {' -> '.join(c)}")
            return 1
        else:
            print("No circular dependencies detected.")
            return 0

    if args.format == "json":
        import json
        output = {
            "tasks": {
                tid: {
                    "depends_on": sorted(info["depends_on"]),
                    "blocks": sorted(info["blocks"]),
                    "layer": info["layer"],
                    "priority": info["priority"],
                    "layer_depth": layers.get(tid, -1),
                }
                for tid, info in all_tasks.items()
            },
            "cycles": [c for c in cycles],
            "total_tasks": len(all_tasks),
            "total_edges": sum(len(info["depends_on"]) for info in all_tasks.values()),
        }
        print(json.dumps(output, indent=2))
    elif args.format == "dot":
        print(format_dot(all_tasks, layers))
    else:
        print(format_tree(all_tasks, layers))
        if cycles:
            print()
            print("[WARN] CIRCULAR DEPENDENCIES:")
            for c in cycles:
                print(f"  {' -> '.join(c)}")

    return 1 if cycles else 0


if __name__ == "__main__":
    raise SystemExit(main())
