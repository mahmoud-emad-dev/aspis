#!/usr/bin/env python3
"""Build ``.asps/index/CODE_MAP.md`` — a compact skeleton of the project's Python.

Self-contained (standard library only). For each Python file it extracts the
module docstring, its imports (how files connect), and the public API surface —
function/class signatures with their first docstring line, plus module-level
constants. This is the "understand a file without reading its body" view: an
agent can grasp many files cheaply instead of opening each one.

Two modes:
- whole project (default) → writes ``.asps/index/CODE_MAP.md``
- ``--scope PATH``        → prints just that file's or folder's skeleton to stdout,
                            so an agent can pull the part it needs on demand.

Usage:
    python3 build_code_map.py [project_root]
    python3 build_code_map.py --scope PATH [project_root]
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import build_registry  # reuse SKIP_DIRS so the scan-skip policy stays single-sourced

# ---------------------------------------------------------------------------
# Extraction (stdlib ast — no third-party deps)
# ---------------------------------------------------------------------------


def _signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Render a function signature: ``def name(args) -> return``."""
    args = ast.unparse(node.args)
    returns = f" -> {ast.unparse(node.returns)}" if node.returns else ""
    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    return f"{prefix} {node.name}({args}){returns}"


def _first_doc_line(node: ast.AST) -> str:
    """First non-empty line of *node*'s docstring, trimmed to a single line."""
    doc = ast.get_docstring(node)
    if not doc:
        return ""
    for line in doc.splitlines():
        line = line.strip()
        if line:
            return line if len(line) <= 140 else line[:137] + "..."
    return ""


def _is_public(name: str) -> bool:
    """Keep public names and ``__init__``; skip other private helpers."""
    return name == "__init__" or not name.startswith("_")


def _imports(tree: ast.Module) -> list[str]:
    """Module-level import statements, normalized back to source one-liners."""
    out: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            names = ", ".join(a.name + (f" as {a.asname}" if a.asname else "") for a in node.names)
            out.append(f"import {names}")
        elif isinstance(node, ast.ImportFrom):
            module = "." * node.level + (node.module or "")
            names = ", ".join(a.name + (f" as {a.asname}" if a.asname else "") for a in node.names)
            out.append(f"from {module} import {names}")
    return out


def _constants(tree: ast.Module) -> list[str]:
    """Public module-level UPPER_CASE constant names (the config surface)."""
    names: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        else:
            continue
        for target in targets:
            if (
                isinstance(target, ast.Name)
                and target.id.isupper()
                and not target.id.startswith("_")
            ):
                names.append(target.id)
    return names


def describe(path: Path) -> dict | None:
    """Extract one file's skeleton; return ``None`` if it cannot be parsed."""
    try:
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text)
    except (OSError, UnicodeDecodeError, SyntaxError):
        return None
    info: dict = {
        "lines": text.count("\n") + 1,
        "doc": _first_doc_line(tree),
        "imports": _imports(tree),
        "constants": _constants(tree),
        "functions": [],
        "classes": [],
    }
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and _is_public(node.name):
            info["functions"].append((_signature(node), _first_doc_line(node)))
        elif isinstance(node, ast.ClassDef) and _is_public(node.name):
            methods = [
                (_signature(m), _first_doc_line(m))
                for m in node.body
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and _is_public(m.name)
            ]
            bases = ", ".join(ast.unparse(b) for b in node.bases)
            header = f"class {node.name}" + (f"({bases})" if bases else "")
            info["classes"].append((header, _first_doc_line(node), methods))
    return info


# ---------------------------------------------------------------------------
# Scan + render
# ---------------------------------------------------------------------------


def python_files(root: Path, scope: Path | None) -> list[Path]:
    """Python files under *scope* (or the whole *root*), honoring skip dirs."""
    base = scope if scope is not None else root
    if base.is_file():
        return [base] if base.suffix == ".py" else []
    files: list[Path] = []
    for path in sorted(base.rglob("*.py")):
        rel = path.relative_to(root)
        if any(part in build_registry.SKIP_DIRS for part in rel.parts):
            continue
        files.append(path)
    return files


def render(root: Path, files: list[Path]) -> str:
    """Render *files* as a markdown code map, grouped by their folder."""
    lines = [
        "# Code Map — skeleton + imports per Python file.",
        "# Generated by build_code_map.py — do not edit by hand.",
        "",
    ]
    groups: dict[str, list[Path]] = {}
    for path in files:
        folder = path.parent.relative_to(root).as_posix() or "."
        groups.setdefault(folder, []).append(path)

    for folder in sorted(groups):
        lines.append(f"## {folder}")
        lines.append("")
        for path in groups[folder]:
            rel = path.relative_to(root).as_posix()
            info = describe(path)
            if info is None:
                lines.append(f"### `{rel}`")
                lines.append("- (could not parse)")
                lines.append("")
                continue
            lines.append(f"### `{rel}`  ({info['lines']} lines)")
            if info["doc"]:
                lines.append(f"_{info['doc']}_")
            if info["imports"]:
                lines.append("- imports:")
                lines.extend(f"    - `{imp}`" for imp in info["imports"])
            if info["constants"]:
                joined = ", ".join(f"`{name}`" for name in info["constants"])
                lines.append(f"- constants: {joined}")
            for sig, doc in info["functions"]:
                lines.append(f"- `{sig}`" + (f" — {doc}" if doc else ""))
            for header, doc, methods in info["classes"]:
                lines.append(f"- `{header}`" + (f" — {doc}" if doc else ""))
                for msig, mdoc in methods:
                    lines.append(f"    - `{msig}`" + (f" — {mdoc}" if mdoc else ""))
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    """Write the whole-project code map, or print a scoped skeleton to stdout."""
    args = list(argv if argv is not None else sys.argv[1:])
    scope: Path | None = None
    if "--scope" in args:
        index = args.index("--scope")
        scope = Path(args[index + 1])
        del args[index : index + 2]
    root = Path(args[0]).resolve() if args else Path.cwd()
    resolved_scope = (root / scope).resolve() if scope and not scope.is_absolute() else scope

    output = render(root, python_files(root, resolved_scope))
    if scope is not None:
        sys.stdout.write(output)  # on-demand: hand the scoped skeleton back to the caller
        return 0
    target = root / ".asps" / "index" / "CODE_MAP.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(output, encoding="utf-8")
    print(f"wrote {target.relative_to(root).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
