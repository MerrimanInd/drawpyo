from __future__ import annotations

import ast
import fnmatch
import heapq
import html
import math
import os
import sys
import tokenize
from dataclasses import dataclass, replace
from enum import Enum
from pathlib import Path, PurePosixPath
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple, Union

from ..diagram.edges import Edge
from ..diagram.objects import Object
from ..diagram.text_format import TextFormat
from ..file import File
from ..page import Page
from .legend import Legend


PathInput = Union[str, os.PathLike[str]]


class NodeKind(str, Enum):
    INTERNAL_MODULE = "internal_module"
    INTERNAL_PACKAGE = "internal_package"
    STANDARD_LIBRARY = "standard_library"
    EXTERNAL = "external"


class DependencyKind(str, Enum):
    INTERNAL = "internal"
    STANDARD_LIBRARY = "standard_library"
    EXTERNAL = "external"


class DiagnosticSeverity(str, Enum):
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True)
class CouplingMetrics:
    fan_in: int = 0
    fan_out: int = 0
    ca: int = 0
    ce: int = 0
    instability: float = 0.0


@dataclass(frozen=True)
class ImportEvidence:
    source_path: Path
    line: int
    imported_name: str
    type_checking: bool = False


@dataclass(frozen=True)
class AnalysisDiagnostic:
    severity: DiagnosticSeverity
    code: str
    message: str
    path: Optional[Path] = None
    line: Optional[int] = None


@dataclass(frozen=True)
class DependencyNode:
    id: str
    label: str
    kind: NodeKind
    source_paths: Tuple[Path, ...] = ()
    metrics: CouplingMetrics = CouplingMetrics()
    scc_id: Optional[int] = None
    cycle_id: Optional[int] = None
    cycle_size: int = 0


@dataclass(frozen=True)
class DependencyEdge:
    source: str
    target: str
    kind: DependencyKind
    weight: int
    type_checking_only: bool
    evidence: Tuple[ImportEvidence, ...]
    in_cycle: bool = False


@dataclass(frozen=True)
class DependencyAnalysis:
    nodes: Mapping[str, DependencyNode]
    edges: Tuple[DependencyEdge, ...]
    sccs: Tuple[Tuple[str, ...], ...]
    cycles: Tuple[Tuple[str, ...], ...]
    diagnostics: Tuple[AnalysisDiagnostic, ...]
    source_path: Path
    root_name: Optional[str]
    granularity: str


class DependencyAnalysisError(Exception):
    """Raised when strict static analysis encounters incomplete source data."""

    def __init__(self, diagnostics: Sequence[AnalysisDiagnostic]) -> None:
        self.diagnostics = tuple(diagnostics)
        details = "; ".join(_format_diagnostic(item) for item in self.diagnostics)
        super().__init__(f"Dependency analysis failed: {details}")


@dataclass(frozen=True)
class _SourceUnit:
    id: str
    path: Path
    display_path: Path
    kind: NodeKind
    parse_source: bool


@dataclass(frozen=True)
class _RawDependency:
    source: str
    target: str
    evidence: ImportEvidence


_IGNORED_DIRECTORIES = {
    ".git",
    ".hg",
    ".svn",
    ".tox",
    ".nox",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "build",
    "dist",
    "site-packages",
    "node_modules",
}

_NODE_STYLES = {
    NodeKind.INTERNAL_MODULE: ("#DAE8FC", "#6C8EBF"),
    NodeKind.INTERNAL_PACKAGE: ("#D5E8D4", "#82B366"),
    NodeKind.STANDARD_LIBRARY: ("#F5F5F5", "#666666"),
    NodeKind.EXTERNAL: ("#E1D5E7", "#9673A6"),
}
_CYCLE_STYLE = ("#F8CECC", "#B85450")
_CYCLE_EDGE_COLOR = "#B85450"
_ROUTING_CLEARANCE = 10
_ROUTING_GAP = _ROUTING_CLEARANCE * 2 + 8
_ROUTING_FRAME_MARGIN = _ROUTING_CLEARANCE * 3
_BEND_PENALTY = 24
_CROSSING_PENALTY = 300
_OVERLAP_PENALTY = 250


_Point = Tuple[float, float]


@dataclass(frozen=True)
class _Rectangle:
    left: float
    top: float
    right: float
    bottom: float

    def expanded(self, amount: float) -> "_Rectangle":
        return _Rectangle(
            self.left - amount,
            self.top - amount,
            self.right + amount,
            self.bottom + amount,
        )


class _RouteOccupancy:
    """Spatial index for already-routed horizontal and vertical segments."""

    def __init__(self) -> None:
        self.horizontal: Dict[float, List[Tuple[float, float]]] = {}
        self.vertical: Dict[float, List[Tuple[float, float]]] = {}

    def add(self, path: Sequence[_Point]) -> None:
        for first, second in zip(path, path[1:]):
            if first[1] == second[1]:
                bounds = tuple(sorted((first[0], second[0])))
                self.horizontal.setdefault(first[1], []).append(bounds)
            else:
                bounds = tuple(sorted((first[1], second[1])))
                self.vertical.setdefault(first[0], []).append(bounds)

    def penalty(self, first: _Point, second: _Point) -> float:
        penalty = 0.0
        if first[1] == second[1]:
            left, right = sorted((first[0], second[0]))
            for other_left, other_right in self.horizontal.get(first[1], ()):
                overlap = max(0.0, min(right, other_right) - max(left, other_left))
                if overlap:
                    penalty += _OVERLAP_PENALTY + overlap * 4
            for x, ranges in self.vertical.items():
                if left < x < right and any(
                    top < first[1] < bottom for top, bottom in ranges
                ):
                    penalty += _CROSSING_PENALTY
        else:
            top, bottom = sorted((first[1], second[1]))
            for other_top, other_bottom in self.vertical.get(first[0], ()):
                overlap = max(
                    0.0, min(bottom, other_bottom) - max(top, other_top)
                )
                if overlap:
                    penalty += _OVERLAP_PENALTY + overlap * 4
            for y, ranges in self.horizontal.items():
                if top < y < bottom and any(
                    left < first[0] < right for left, right in ranges
                ):
                    penalty += _CROSSING_PENALTY
        return penalty


class _ImportVisitor(ast.NodeVisitor):
    def __init__(
        self,
        unit: _SourceUnit,
        internal_names: Set[str],
        diagnostics: List[AnalysisDiagnostic],
        typing_aliases: Set[str],
        type_checking_names: Set[str],
    ) -> None:
        self.unit = unit
        self.internal_names = internal_names
        self.diagnostics = diagnostics
        self.typing_aliases = typing_aliases
        self.type_checking_names = type_checking_names
        self.type_checking_depth = 0
        self.dependencies: List[_RawDependency] = []

    def visit_If(self, node: ast.If) -> None:
        self.visit(node.test)
        guarded = self._is_type_checking_guard(node.test)
        if guarded:
            self.type_checking_depth += 1
        for statement in node.body:
            self.visit(statement)
        if guarded:
            self.type_checking_depth -= 1
        for statement in node.orelse:
            self.visit(statement)

    def visit_Import(self, node: ast.Import) -> None:
        targets = {alias.name for alias in node.names}
        for target in sorted(targets):
            self._add_dependency(node, target, f"import {target}")

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        base = self._resolve_from_base(node)
        if base is None:
            return

        targets: Dict[str, str] = {}
        for alias in node.names:
            candidate = f"{base}.{alias.name}" if base and alias.name != "*" else base
            if candidate in self.internal_names:
                target = candidate
            elif base in self.internal_names or node.level == 0:
                target = base
            else:
                self.diagnostics.append(
                    AnalysisDiagnostic(
                        DiagnosticSeverity.ERROR,
                        "unresolved_relative_import",
                        f"Could not resolve relative import '{self._from_spelling(node)}' "
                        f"from module '{self.unit.id}'",
                        self.unit.path,
                        node.lineno,
                    )
                )
                continue
            if target:
                targets[target] = self._from_spelling(node)

        for target, spelling in sorted(targets.items()):
            self._add_dependency(node, target, spelling)

    def _resolve_from_base(self, node: ast.ImportFrom) -> Optional[str]:
        if node.level == 0:
            return node.module or ""

        package = (
            self.unit.id
            if self.unit.kind == NodeKind.INTERNAL_PACKAGE
            else self.unit.id.rpartition(".")[0]
        )
        package_parts = package.split(".") if package else []
        ascents = node.level - 1
        if not package_parts or ascents >= len(package_parts):
            self.diagnostics.append(
                AnalysisDiagnostic(
                    DiagnosticSeverity.ERROR,
                    "unresolved_relative_import",
                    f"Relative import '{self._from_spelling(node)}' ascends beyond "
                    f"the known package for module '{self.unit.id}'",
                    self.unit.path,
                    node.lineno,
                )
            )
            return None

        parts = package_parts[: len(package_parts) - ascents]
        if node.module:
            parts.extend(node.module.split("."))
        return ".".join(parts)

    def _add_dependency(self, node: ast.AST, target: str, spelling: str) -> None:
        self.dependencies.append(
            _RawDependency(
                self.unit.id,
                target,
                ImportEvidence(
                    self.unit.display_path,
                    getattr(node, "lineno", 0),
                    spelling,
                    self.type_checking_depth > 0,
                ),
            )
        )

    def _is_type_checking_guard(self, node: ast.AST) -> bool:
        if isinstance(node, ast.Name):
            return node.id in self.type_checking_names
        return (
            isinstance(node, ast.Attribute)
            and node.attr == "TYPE_CHECKING"
            and isinstance(node.value, ast.Name)
            and node.value.id in self.typing_aliases
        )

    @staticmethod
    def _from_spelling(node: ast.ImportFrom) -> str:
        module = "." * node.level + (node.module or "")
        names = ", ".join(alias.name for alias in node.names)
        return f"from {module} import {names}"


def _format_diagnostic(diagnostic: AnalysisDiagnostic) -> str:
    location = ""
    if diagnostic.path is not None:
        location = str(diagnostic.path)
        if diagnostic.line is not None:
            location += f":{diagnostic.line}"
        location += ": "
    return f"{location}{diagnostic.message}"


def _matches_pattern(relative_path: str, patterns: Sequence[str]) -> bool:
    path = PurePosixPath(relative_path)
    return any(
        fnmatch.fnmatch(relative_path, pattern) or path.match(pattern)
        for pattern in patterns
    )


def _is_test_path(relative_path: PurePosixPath) -> bool:
    parts = {part.lower() for part in relative_path.parts[:-1]}
    name = relative_path.name.lower()
    return (
        bool(parts & {"test", "tests"})
        or name.startswith("test_")
        or name.endswith("_test.py")
    )


def _module_name(path: Path, source_root: Path) -> Tuple[str, NodeKind]:
    relative = path.relative_to(source_root)
    if path.name == "__init__.py":
        parts = relative.parent.parts
        return ".".join(parts), NodeKind.INTERNAL_PACKAGE
    return ".".join(relative.with_suffix("").parts), NodeKind.INTERNAL_MODULE


def _discover_units(
    source_path: Path,
    *,
    patterns: Sequence[str],
    exclude_tests: bool,
    namespace: Optional[str],
) -> Tuple[Dict[str, _SourceUnit], Optional[str]]:
    if not source_path.exists():
        raise FileNotFoundError(
            f"Python dependency source does not exist: {source_path}"
        )

    source_path = source_path.resolve()
    files: List[Path] = []

    if source_path.is_file():
        if source_path.suffix != ".py":
            raise ValueError(f"Dependency source file must end in .py: {source_path}")
        source_root = source_path.parent
        regular_root = None
        while (source_root / "__init__.py").is_file():
            regular_root = source_root
            source_root = source_root.parent
        files = [source_path]
    elif source_path.is_dir():
        regular_root = source_path if (source_path / "__init__.py").is_file() else None
        source_root = source_path.parent if regular_root else source_path
        walk_errors: List[OSError] = []

        def onerror(error: OSError) -> None:
            walk_errors.append(error)

        for directory, directory_names, file_names in os.walk(
            source_path, topdown=True, followlinks=False, onerror=onerror
        ):
            current = Path(directory)
            relative_directory = current.relative_to(source_path)
            kept_directories = []
            for name in sorted(directory_names):
                relative = (relative_directory / name).as_posix()
                if name in _IGNORED_DIRECTORIES or name.startswith("."):
                    continue
                if _matches_pattern(relative, patterns):
                    continue
                if exclude_tests and name.lower() in {"test", "tests"}:
                    continue
                kept_directories.append(name)
            directory_names[:] = kept_directories

            for name in sorted(file_names):
                if not name.endswith(".py"):
                    continue
                file_path = current / name
                relative = file_path.relative_to(source_path)
                relative_string = relative.as_posix()
                if _matches_pattern(relative_string, patterns):
                    continue
                if exclude_tests and _is_test_path(PurePosixPath(relative_string)):
                    continue
                files.append(file_path)

        if walk_errors and not files:
            raise walk_errors[0]
    else:
        raise ValueError(
            f"Dependency source must be a directory or Python file: {source_path}"
        )

    if not files:
        raise ValueError(f"No Python source files found under: {source_path}")

    display_root = source_root
    units: Dict[str, _SourceUnit] = {}
    for file_path in sorted(files):
        module_id, kind = _module_name(file_path, source_root)
        if not module_id:
            raise ValueError(f"Could not derive a module name for: {file_path}")
        if module_id in units:
            raise ValueError(
                f"Duplicate module name '{module_id}' for '{units[module_id].path}' "
                f"and '{file_path}'"
            )
        units[module_id] = _SourceUnit(
            module_id,
            file_path,
            file_path.relative_to(display_root),
            kind,
            True,
        )

    # Add synthetic namespace packages for directories that contain discovered files.
    for unit in tuple(units.values()):
        relative_parent = unit.path.parent.relative_to(source_root)
        for index in range(1, len(relative_parent.parts) + 1):
            package_id = ".".join(relative_parent.parts[:index])
            package_path = source_root.joinpath(*relative_parent.parts[:index])
            existing = units.get(package_id)
            if existing is not None and existing.kind == NodeKind.INTERNAL_MODULE:
                raise ValueError(
                    f"Duplicate module name '{package_id}' for '{existing.path}' "
                    f"and namespace package '{package_path}'"
                )
            if existing is None:
                units[package_id] = _SourceUnit(
                    package_id,
                    package_path,
                    package_path.relative_to(display_root),
                    NodeKind.INTERNAL_PACKAGE,
                    False,
                )

    if namespace is not None:
        if not namespace.strip() or any(
            not part.isidentifier() for part in namespace.split(".")
        ):
            raise ValueError("namespace must be a non-empty dotted module name")
        selected = {
            name: unit
            for name, unit in units.items()
            if name == namespace or name.startswith(namespace + ".")
        }
        if not selected:
            raise ValueError(
                f"Namespace '{namespace}' was not found under dependency source '{source_path}'"
            )
        units = selected
        root_name = namespace
    elif regular_root is not None:
        root_name = regular_root.name
    else:
        root_name = None

    return dict(sorted(units.items())), root_name


def _typing_aliases(tree: ast.Module) -> Tuple[Set[str], Set[str]]:
    module_aliases = {"typing"}
    checking_names = {"TYPE_CHECKING"}
    for statement in tree.body:
        if isinstance(statement, ast.Import):
            for alias in statement.names:
                if alias.name == "typing":
                    module_aliases.add(alias.asname or alias.name)
        elif isinstance(statement, ast.ImportFrom) and statement.module == "typing":
            for alias in statement.names:
                if alias.name == "TYPE_CHECKING":
                    checking_names.add(alias.asname or alias.name)
    return module_aliases, checking_names


def _collect_dependencies(
    units: Mapping[str, _SourceUnit], diagnostics: List[AnalysisDiagnostic]
) -> List[_RawDependency]:
    dependencies: List[_RawDependency] = []
    internal_names = set(units)
    for unit in units.values():
        if not unit.parse_source:
            continue
        try:
            with tokenize.open(unit.path) as source_file:
                source = source_file.read()
        except (OSError, UnicodeError, SyntaxError) as exc:
            diagnostics.append(
                AnalysisDiagnostic(
                    DiagnosticSeverity.ERROR,
                    "unreadable_source",
                    f"Could not read module '{unit.id}': {exc}",
                    unit.path,
                )
            )
            continue
        try:
            tree = ast.parse(source, filename=str(unit.path))
        except SyntaxError as exc:
            diagnostics.append(
                AnalysisDiagnostic(
                    DiagnosticSeverity.ERROR,
                    "invalid_syntax",
                    f"Could not parse module '{unit.id}': {exc.msg}",
                    unit.path,
                    exc.lineno,
                )
            )
            continue

        typing_aliases, checking_names = _typing_aliases(tree)
        visitor = _ImportVisitor(
            unit, internal_names, diagnostics, typing_aliases, checking_names
        )
        visitor.visit(tree)
        dependencies.extend(visitor.dependencies)
    return dependencies


def _target_kind(target: str, internal_names: Set[str]) -> NodeKind:
    if target in internal_names:
        raise ValueError("Internal targets are classified from their source units")
    top_level = target.partition(".")[0]
    stdlib_names = set(getattr(sys, "stdlib_module_names", ())) | set(
        sys.builtin_module_names
    )
    if top_level in stdlib_names:
        return NodeKind.STANDARD_LIBRARY
    return NodeKind.EXTERNAL


def _aggregate_mapping(
    units: Mapping[str, _SourceUnit], granularity: str
) -> Dict[str, str]:
    if granularity == "module":
        return {name: name for name in units}

    packages = {
        name for name, unit in units.items() if unit.kind == NodeKind.INTERNAL_PACKAGE
    }
    mapping: Dict[str, str] = {}
    for name, unit in units.items():
        if unit.kind == NodeKind.INTERNAL_PACKAGE:
            mapping[name] = name
            continue
        parts = name.split(".")[:-1]
        candidates = [".".join(parts[:index]) for index in range(1, len(parts) + 1)]
        owning_packages = [
            candidate for candidate in candidates if candidate in packages
        ]
        mapping[name] = owning_packages[-1] if owning_packages else name
    return mapping


def _tarjan(
    node_ids: Iterable[str], edges: Iterable[Tuple[str, str]]
) -> Tuple[Tuple[str, ...], ...]:
    adjacency: Dict[str, Set[str]] = {node_id: set() for node_id in node_ids}
    for source, target in edges:
        if source in adjacency and target in adjacency:
            adjacency[source].add(target)

    index = 0
    indices: Dict[str, int] = {}
    lowlinks: Dict[str, int] = {}
    stack: List[str] = []
    on_stack: Set[str] = set()
    components: List[Tuple[str, ...]] = []

    def visit(node_id: str) -> None:
        nonlocal index
        indices[node_id] = index
        lowlinks[node_id] = index
        index += 1
        stack.append(node_id)
        on_stack.add(node_id)

        for target in sorted(adjacency[node_id]):
            if target not in indices:
                visit(target)
                lowlinks[node_id] = min(lowlinks[node_id], lowlinks[target])
            elif target in on_stack:
                lowlinks[node_id] = min(lowlinks[node_id], indices[target])

        if lowlinks[node_id] == indices[node_id]:
            members = []
            while True:
                member = stack.pop()
                on_stack.remove(member)
                members.append(member)
                if member == node_id:
                    break
            components.append(tuple(sorted(members)))

    for node_id in sorted(adjacency):
        if node_id not in indices:
            visit(node_id)

    return tuple(sorted(components, key=lambda component: component[0]))


def _analyze_path(
    path: PathInput,
    *,
    granularity: str,
    include_external: bool,
    include_standard_library: bool,
    include_type_checking: bool,
    exclude_patterns: Iterable[str],
    exclude_tests: bool,
    namespace: Optional[str],
) -> DependencyAnalysis:
    if granularity not in {"module", "package"}:
        raise ValueError("granularity must be 'module' or 'package'")
    source_path = Path(path).expanduser()
    if isinstance(exclude_patterns, str):
        patterns = (exclude_patterns,)
    else:
        patterns = tuple(str(pattern) for pattern in exclude_patterns)
    diagnostics: List[AnalysisDiagnostic] = []
    units, root_name = _discover_units(
        source_path,
        patterns=patterns,
        exclude_tests=exclude_tests,
        namespace=namespace,
    )
    raw_dependencies = _collect_dependencies(units, diagnostics)
    aggregation = _aggregate_mapping(units, granularity)

    node_sources: Dict[str, Set[Path]] = {}
    node_kinds: Dict[str, NodeKind] = {}
    for unit in units.values():
        aggregate_id = aggregation[unit.id]
        node_sources.setdefault(aggregate_id, set()).add(unit.display_path)
        if aggregate_id == unit.id and unit.kind == NodeKind.INTERNAL_PACKAGE:
            node_kinds[aggregate_id] = NodeKind.INTERNAL_PACKAGE
        else:
            node_kinds.setdefault(aggregate_id, NodeKind.INTERNAL_MODULE)

    internal_names = set(units)
    edge_evidence: Dict[Tuple[str, str], List[ImportEvidence]] = {}
    for dependency in raw_dependencies:
        if dependency.evidence.type_checking and not include_type_checking:
            continue
        source = aggregation[dependency.source]
        if dependency.target in internal_names:
            target = aggregation[dependency.target]
            if granularity == "package" and source == target:
                continue
        else:
            target = dependency.target
            kind = _target_kind(target, internal_names)
            if kind == NodeKind.STANDARD_LIBRARY and not include_standard_library:
                continue
            if kind == NodeKind.EXTERNAL and not include_external:
                continue
            node_kinds.setdefault(target, kind)
            node_sources.setdefault(target, set())
        edge_evidence.setdefault((source, target), []).append(dependency.evidence)

    nodes: Dict[str, DependencyNode] = {}
    for node_id in sorted(node_kinds):
        nodes[node_id] = DependencyNode(
            node_id,
            node_id,
            node_kinds[node_id],
            tuple(sorted(node_sources.get(node_id, set()), key=str)),
        )

    edges: List[DependencyEdge] = []
    for (source, target), evidence_items in sorted(edge_evidence.items()):
        evidence = tuple(
            sorted(
                evidence_items,
                key=lambda item: (
                    str(item.source_path),
                    item.line,
                    item.imported_name,
                    item.type_checking,
                ),
            )
        )
        target_node_kind = nodes[target].kind
        if target_node_kind in {NodeKind.INTERNAL_MODULE, NodeKind.INTERNAL_PACKAGE}:
            kind = DependencyKind.INTERNAL
        elif target_node_kind == NodeKind.STANDARD_LIBRARY:
            kind = DependencyKind.STANDARD_LIBRARY
        else:
            kind = DependencyKind.EXTERNAL
        edges.append(
            DependencyEdge(
                source,
                target,
                kind,
                len(evidence),
                all(item.type_checking for item in evidence),
                evidence,
            )
        )

    internal_ids = {
        node_id
        for node_id, node in nodes.items()
        if node.kind in {NodeKind.INTERNAL_MODULE, NodeKind.INTERNAL_PACKAGE}
    }
    internal_pairs = {
        (edge.source, edge.target)
        for edge in edges
        if edge.source in internal_ids and edge.target in internal_ids
    }
    sccs = _tarjan(internal_ids, internal_pairs)
    self_edges = {source for source, target in internal_pairs if source == target}
    cycles = tuple(
        component
        for component in sccs
        if len(component) > 1 or component[0] in self_edges
    )
    scc_lookup = {
        node_id: scc_id
        for scc_id, component in enumerate(sccs, start=1)
        for node_id in component
    }
    cycle_lookup = {
        node_id: (cycle_id, len(component))
        for cycle_id, component in enumerate(cycles, start=1)
        for node_id in component
    }

    incoming: Dict[str, Set[str]] = {node_id: set() for node_id in internal_ids}
    outgoing: Dict[str, Set[str]] = {node_id: set() for node_id in internal_ids}
    for source, target in internal_pairs:
        if source == target:
            continue
        outgoing[source].add(target)
        incoming[target].add(source)

    for node_id in internal_ids:
        ca = len(incoming[node_id])
        ce = len(outgoing[node_id])
        instability = ce / (ca + ce) if ca + ce else 0.0
        cycle_id, cycle_size = cycle_lookup.get(node_id, (None, 0))
        nodes[node_id] = replace(
            nodes[node_id],
            metrics=CouplingMetrics(ca, ce, ca, ce, instability),
            scc_id=scc_lookup[node_id],
            cycle_id=cycle_id,
            cycle_size=cycle_size,
        )

    cyclic_pairs = {
        (source, target)
        for source, target in internal_pairs
        if source in cycle_lookup
        and target in cycle_lookup
        and cycle_lookup[source][0] == cycle_lookup[target][0]
    }
    edges = [
        replace(edge, in_cycle=(edge.source, edge.target) in cyclic_pairs)
        for edge in edges
    ]

    if len(nodes) > 100:
        diagnostics.append(
            AnalysisDiagnostic(
                DiagnosticSeverity.WARNING,
                "large_graph",
                f"The dependency diagram contains {len(nodes)} nodes and may be difficult to read",
                source_path.resolve(),
            )
        )

    diagnostics.sort(
        key=lambda item: (
            item.severity.value,
            item.code,
            str(item.path or ""),
            item.line or 0,
            item.message,
        )
    )
    return DependencyAnalysis(
        dict(sorted(nodes.items())),
        tuple(edges),
        sccs,
        cycles,
        tuple(diagnostics),
        source_path.resolve(),
        root_name,
        granularity,
    )


class DependencyDiagram:
    """A directed dependency diagram produced by static Python source analysis."""

    def __init__(
        self,
        *,
        show_metrics: bool = False,
        show_edge_weights: bool = False,
        show_legend: bool = True,
        direction: str = "right",
        link_style: str = "orthogonal",
        layer_spacing: int = 180,
        node_spacing: int = 40,
        component_spacing: int = 100,
        padding: int = 40,
        file_path: PathInput = ".",
        file_name: str = "Python Dependencies.drawio",
    ) -> None:
        if direction not in {"right", "down"}:
            raise ValueError("direction must be 'right' or 'down'")
        if link_style not in {"orthogonal", "straight", "curved"}:
            raise ValueError("link_style must be 'orthogonal', 'straight', or 'curved'")
        for name, value in {
            "layer_spacing": layer_spacing,
            "node_spacing": node_spacing,
            "component_spacing": component_spacing,
            "padding": padding,
        }.items():
            if not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")

        self.show_metrics = show_metrics
        self.show_edge_weights = show_edge_weights
        self.show_legend = show_legend
        self.direction = direction
        self.link_style = link_style
        self.layer_spacing = layer_spacing
        self.node_spacing = node_spacing
        self.component_spacing = component_spacing
        self.padding = padding
        self.file = File(file_name=file_name, file_path=str(file_path))
        self.page = Page(file=self.file, name="Dependencies")
        self.objects: List[Object] = []
        self.links: List[Edge] = []
        self.analysis: Optional[DependencyAnalysis] = None
        self._node_objects: Dict[str, Object] = {}
        self._routed_paths: Tuple[Tuple[_Point, ...], ...] = ()

    @classmethod
    def create_from_path(
        cls,
        path: PathInput,
        *,
        granularity: str = "module",
        include_external: bool = True,
        include_standard_library: bool = False,
        include_type_checking: bool = True,
        exclude_patterns: Iterable[str] = (),
        exclude_tests: bool = True,
        namespace: Optional[str] = None,
        strict: bool = False,
        show_metrics: bool = False,
        show_edge_weights: bool = False,
        show_legend: bool = True,
        direction: str = "right",
        link_style: str = "orthogonal",
        layer_spacing: int = 180,
        node_spacing: int = 40,
        component_spacing: int = 100,
        padding: int = 40,
        file_path: PathInput = ".",
        file_name: str = "Python Dependencies.drawio",
    ) -> "DependencyDiagram":
        """Analyze Python source without importing it and build a dependency diagram."""
        analysis = _analyze_path(
            path,
            granularity=granularity,
            include_external=include_external,
            include_standard_library=include_standard_library,
            include_type_checking=include_type_checking,
            exclude_patterns=exclude_patterns,
            exclude_tests=exclude_tests,
            namespace=namespace,
        )
        incomplete = [
            diagnostic
            for diagnostic in analysis.diagnostics
            if diagnostic.severity == DiagnosticSeverity.ERROR
        ]
        if strict and incomplete:
            raise DependencyAnalysisError(incomplete)

        diagram = cls(
            show_metrics=show_metrics,
            show_edge_weights=show_edge_weights,
            show_legend=show_legend,
            direction=direction,
            link_style=link_style,
            layer_spacing=layer_spacing,
            node_spacing=node_spacing,
            component_spacing=component_spacing,
            padding=padding,
            file_path=file_path,
            file_name=file_name,
        )
        diagram.analysis = analysis
        diagram._render()
        return diagram

    @property
    def diagnostics(self) -> Tuple[AnalysisDiagnostic, ...]:
        return self.analysis.diagnostics if self.analysis is not None else ()

    @property
    def file_name(self) -> str:
        return self.file.file_name

    @file_name.setter
    def file_name(self, value: str) -> None:
        self.file.file_name = value

    @property
    def file_path(self) -> str:
        return self.file.file_path

    @file_path.setter
    def file_path(self, value: PathInput) -> None:
        self.file.file_path = str(value)

    def write(self, **kwargs: object) -> str:
        return self.file.write(**kwargs)

    def _render(self) -> None:
        if self.analysis is None:
            return
        legend_height = self._add_legend() if self.show_legend else 0
        graph_origin = (
            self.padding + _ROUTING_FRAME_MARGIN,
            self.padding + legend_height + _ROUTING_FRAME_MARGIN,
        )

        sizes: Dict[str, Tuple[int, int]] = {}
        for node in self.analysis.nodes.values():
            width = max(140, min(320, 42 + len(node.label) * 7))
            if node.kind in {NodeKind.STANDARD_LIBRARY, NodeKind.EXTERNAL}:
                width = max(120, min(260, 32 + len(node.label) * 7))
            height = (
                76
                if self.show_metrics
                and node.kind
                in {
                    NodeKind.INTERNAL_MODULE,
                    NodeKind.INTERNAL_PACKAGE,
                }
                else 52
            )
            sizes[node.id] = (width, height)

        positions = self._layout(sizes)
        for node_id, node in self.analysis.nodes.items():
            fill, stroke = (
                _CYCLE_STYLE if node.cycle_id is not None else _NODE_STYLES[node.kind]
            )
            value = f"<b>{html.escape(node.label)}</b>"
            if self.show_metrics and node.kind in {
                NodeKind.INTERNAL_MODULE,
                NodeKind.INTERNAL_PACKAGE,
            }:
                value += (
                    f'<br><font size="2">Ca {node.metrics.ca} · Ce {node.metrics.ce} '
                    f"· I {node.metrics.instability:.2f}</font>"
                )
            x, y = positions[node_id]
            width, height = sizes[node_id]
            obj = Object(
                page=self.page,
                value=value,
                position=(x + graph_origin[0], y + graph_origin[1]),
                width=width,
                height=height,
                rounded=1,
                fillColor=fill,
                strokeColor=stroke,
                tooltip=self._node_tooltip(node),
                text_format=TextFormat(
                    formattedText=True, align="center", verticalAlign="middle"
                ),
            )
            self.objects.append(obj)
            self._node_objects[node_id] = obj

        rendered_edges: List[Tuple[DependencyEdge, Edge]] = []
        for dependency in self.analysis.edges:
            edge = Edge(
                page=self.page,
                source=self._node_objects[dependency.source],
                target=self._node_objects[dependency.target],
                label=(
                    f"×{dependency.weight}"
                    if self.show_edge_weights and dependency.weight > 1
                    else None
                ),
                waypoints=self.link_style,
                pattern="dashed_medium" if dependency.type_checking_only else "solid",
                line_end_target="classic",
                endFill_target=True,
                stroke_color=_CYCLE_EDGE_COLOR if dependency.in_cycle else None,
                strokeWidth=(
                    3
                    if dependency.in_cycle
                    else (
                        min(4, 1 + int(math.log2(dependency.weight)))
                        if self.show_edge_weights
                        else 1
                    )
                ),
                tooltip=self._edge_tooltip(dependency),
            )
            self.links.append(edge)
            rendered_edges.append((dependency, edge))

        self._route_edges(rendered_edges)

        self._fit_page()

    def _add_legend(self) -> int:
        legend = Legend(
            {
                "Internal module": _NODE_STYLES[NodeKind.INTERNAL_MODULE][0],
                "Internal package": _NODE_STYLES[NodeKind.INTERNAL_PACKAGE][0],
                "Standard library": _NODE_STYLES[NodeKind.STANDARD_LIBRARY][0],
                "External": _NODE_STYLES[NodeKind.EXTERNAL][0],
                "Cycle member": _CYCLE_STYLE[0],
            },
            position=(self.padding, self.padding),
            title="Dependency types",
        )
        legend.add_to_page(self.page)
        base_y = int(self.padding + legend.group.height + 10)
        for index, (label, pattern, color) in enumerate(
            (
                ("Type-checking only", "dashed_medium", None),
                ("Cycle dependency", "solid", _CYCLE_EDGE_COLOR),
            )
        ):
            y = base_y + index * 24
            source = Object(
                page=self.page,
                value="",
                position=(self.padding, y + 7),
                width=1,
                height=1,
                fillColor="none",
                strokeColor="none",
            )
            target = Object(
                page=self.page,
                value="",
                position=(self.padding + 35, y + 7),
                width=1,
                height=1,
                fillColor="none",
                strokeColor="none",
            )
            edge = Edge(
                page=self.page,
                source=source,
                target=target,
                waypoints="straight",
                pattern=pattern,
                line_end_target="classic",
                endFill_target=True,
                stroke_color=color,
                strokeWidth=3 if color else 1,
            )
            text = Object(
                page=self.page,
                value=label,
                position=(self.padding + 48, y),
                width=150,
                height=18,
                fillColor="none",
                strokeColor="none",
                text_format=TextFormat(align="left", verticalAlign="middle"),
            )
        return int(legend.group.height + 70)

    def _layout(
        self, sizes: Mapping[str, Tuple[int, int]]
    ) -> Dict[str, Tuple[int, int]]:
        assert self.analysis is not None
        internal_ids = {
            node_id
            for node_id, node in self.analysis.nodes.items()
            if node.kind in {NodeKind.INTERNAL_MODULE, NodeKind.INTERNAL_PACKAGE}
        }
        super_members: Dict[str, Tuple[str, ...]] = {}
        node_super: Dict[str, str] = {}
        for index, component in enumerate(self.analysis.sccs):
            key = f"scc:{index}:{component[0]}"
            super_members[key] = component
            for node_id in component:
                node_super[node_id] = key
        for node_id in self.analysis.nodes:
            if node_id not in internal_ids:
                key = f"external:{node_id}"
                super_members[key] = (node_id,)
                node_super[node_id] = key

        adjacency: Dict[str, Set[str]] = {key: set() for key in super_members}
        reverse: Dict[str, Set[str]] = {key: set() for key in super_members}
        for edge in self.analysis.edges:
            source = node_super[edge.source]
            target = node_super[edge.target]
            if source != target:
                adjacency[source].add(target)
                reverse[target].add(source)

        components: List[Tuple[str, ...]] = []
        unseen = set(super_members)
        while unseen:
            start = min(unseen, key=lambda key: super_members[key][0])
            stack = [start]
            members = set()
            while stack:
                current = stack.pop()
                if current in members:
                    continue
                members.add(current)
                stack.extend(
                    sorted(adjacency[current] | reverse[current], reverse=True)
                )
            unseen.difference_update(members)
            components.append(
                tuple(sorted(members, key=lambda key: super_members[key][0]))
            )
        components.sort(key=lambda component: super_members[component[0]][0])

        block_sizes: Dict[str, Tuple[int, int]] = {}
        member_offsets: Dict[str, Dict[str, Tuple[int, int]]] = {}
        grid_gap = max(_ROUTING_GAP, self.node_spacing // 2)
        for key, members in super_members.items():
            columns = max(1, math.ceil(math.sqrt(len(members))))
            rows = math.ceil(len(members) / columns)
            cell_width = max(sizes[member][0] for member in members)
            cell_height = max(sizes[member][1] for member in members)
            block_sizes[key] = (
                columns * cell_width + (columns - 1) * grid_gap,
                rows * cell_height + (rows - 1) * grid_gap,
            )
            offsets = {}
            for index, member in enumerate(members):
                column = index % columns
                row = index // columns
                offsets[member] = (
                    column * (cell_width + grid_gap),
                    row * (cell_height + grid_gap),
                )
            member_offsets[key] = offsets

        positions: Dict[str, Tuple[int, int]] = {}
        component_cross_offset = 0
        for component in components:
            component_set = set(component)
            indegree = {key: len(reverse[key] & component_set) for key in component}
            queue = [
                (super_members[key][0], key)
                for key, degree in indegree.items()
                if degree == 0
            ]
            heapq.heapify(queue)
            layer = {key: 0 for key in component}
            order: List[str] = []
            while queue:
                _, key = heapq.heappop(queue)
                order.append(key)
                for target in sorted(
                    adjacency[key] & component_set,
                    key=lambda item: super_members[item][0],
                ):
                    layer[target] = max(layer[target], layer[key] + 1)
                    indegree[target] -= 1
                    if indegree[target] == 0:
                        heapq.heappush(queue, (super_members[target][0], target))

            layers: Dict[int, List[str]] = {}
            for key in order:
                layers.setdefault(layer[key], []).append(key)
            self._order_layers(layers, adjacency, reverse, super_members)
            primary_offsets: Dict[int, int] = {}
            primary = 0
            for layer_index in sorted(layers):
                primary_offsets[layer_index] = primary
                maximum = max(
                    block_sizes[key][0 if self.direction == "right" else 1]
                    for key in layers[layer_index]
                )
                primary += maximum + max(self.layer_spacing, _ROUTING_GAP)

            component_cross_size = 0
            for layer_index in sorted(layers):
                cross = component_cross_offset
                for key in layers[layer_index]:
                    block_width, block_height = block_sizes[key]
                    if self.direction == "right":
                        block_x, block_y = primary_offsets[layer_index], cross
                        cross += block_height + max(self.node_spacing, _ROUTING_GAP)
                        component_cross_size = max(
                            component_cross_size, cross - component_cross_offset
                        )
                    else:
                        block_x, block_y = cross, primary_offsets[layer_index]
                        cross += block_width + max(self.node_spacing, _ROUTING_GAP)
                        component_cross_size = max(
                            component_cross_size, cross - component_cross_offset
                        )
                    for member, (offset_x, offset_y) in member_offsets[key].items():
                        positions[member] = (block_x + offset_x, block_y + offset_y)
            component_cross_offset += component_cross_size + max(
                self.component_spacing, _ROUTING_GAP
            )
        return positions

    @staticmethod
    def _order_layers(
        layers: Dict[int, List[str]],
        adjacency: Mapping[str, Set[str]],
        reverse: Mapping[str, Set[str]],
        super_members: Mapping[str, Tuple[str, ...]],
    ) -> None:
        """Reduce crossings with deterministic forward/backward barycentric sweeps."""
        layer_for = {
            key: layer_index
            for layer_index, keys in layers.items()
            for key in keys
        }

        def positions() -> Dict[str, int]:
            return {
                key: index
                for keys in layers.values()
                for index, key in enumerate(keys)
            }

        def reorder(
            layer_index: int,
            neighbors: Mapping[str, Set[str]],
            toward_lower_layers: bool,
        ) -> None:
            ranks = positions()

            def sort_key(key: str) -> Tuple[float, str]:
                relevant = [
                    neighbor
                    for neighbor in neighbors[key]
                    if (
                        layer_for[neighbor] < layer_index
                        if toward_lower_layers
                        else layer_for[neighbor] > layer_index
                    )
                ]
                barycenter = (
                    sum(ranks[item] for item in relevant) / len(relevant)
                    if relevant
                    else float(ranks[key])
                )
                return barycenter, super_members[key][0]

            layers[layer_index].sort(key=sort_key)

        layer_indexes = sorted(layers)
        for _ in range(4):
            for layer_index in layer_indexes[1:]:
                reorder(layer_index, reverse, True)
            for layer_index in reversed(layer_indexes[:-1]):
                reorder(layer_index, adjacency, False)

    def _route_edges(
        self, rendered_edges: Sequence[Tuple[DependencyEdge, Edge]]
    ) -> None:
        if not rendered_edges:
            return

        rectangles = {
            node_id: _Rectangle(
                float(obj.position[0]),
                float(obj.position[1]),
                float(obj.position[0] + obj.width),
                float(obj.position[1] + obj.height),
            )
            for node_id, obj in self._node_objects.items()
        }
        faces: Dict[Tuple[int, str], str] = {}
        endpoint_groups: Dict[Tuple[str, str], List[Tuple[int, str]]] = {}
        for index, (dependency, _) in enumerate(rendered_edges):
            source_face, target_face = self._preferred_faces(
                rectangles[dependency.source], rectangles[dependency.target]
            )
            for role, node_id, face in (
                ("source", dependency.source, source_face),
                ("target", dependency.target, target_face),
            ):
                endpoint = (index, role)
                faces[endpoint] = face
                endpoint_groups.setdefault((node_id, face), []).append(endpoint)

        ports: Dict[Tuple[int, str], Tuple[_Point, _Point, float]] = {}
        for (node_id, face), endpoints in sorted(endpoint_groups.items()):
            rectangle = rectangles[node_id]

            def endpoint_key(endpoint: Tuple[int, str]) -> Tuple[float, str, str]:
                index, role = endpoint
                dependency = rendered_edges[index][0]
                other_id = (
                    dependency.target if role == "source" else dependency.source
                )
                other = rectangles[other_id]
                other_center = (
                    (other.top + other.bottom) / 2
                    if face in {"left", "right"}
                    else (other.left + other.right) / 2
                )
                return other_center, other_id, role

            endpoints.sort(key=endpoint_key)
            for rank, endpoint in enumerate(endpoints, start=1):
                fraction = rank / (len(endpoints) + 1)
                port, stub = self._port_points(rectangle, face, fraction)
                ports[endpoint] = (port, stub, fraction)

        order = sorted(
            range(len(rendered_edges)),
            key=lambda index: self._routing_order_key(
                rendered_edges[index][0], rectangles
            ),
        )
        obstacles = [
            rectangle.expanded(_ROUTING_CLEARANCE)
            for rectangle in rectangles.values()
        ]
        occupied_paths: List[List[_Point]] = []
        occupancy = _RouteOccupancy()
        routed_paths: Dict[int, List[_Point]] = {}
        for index in order:
            dependency, edge = rendered_edges[index]
            source_port, source_stub, source_fraction = ports[(index, "source")]
            target_port, target_stub, target_fraction = ports[(index, "target")]
            self._set_edge_port(
                edge, faces[(index, "source")], source_fraction, source=True
            )
            self._set_edge_port(
                edge, faces[(index, "target")], target_fraction, source=False
            )

            middle = self._find_orthogonal_route(
                source_stub, target_stub, obstacles, occupancy
            )
            path = self._simplify_path(
                [source_port, source_stub, *middle[1:-1], target_stub, target_port]
            )
            for point in path[1:-1]:
                edge.add_point_pos(point)  # type: ignore[arg-type]
            if any(
                self._paths_cross(path, prior_path)
                for prior_path in occupied_paths
            ):
                edge.jumpStyle = "arc"
                edge.jumpSize = 6
            occupied_paths.append(path)
            occupancy.add(path)
            routed_paths[index] = path

        # Retain deterministic link order while routing the hardest edges first.
        self._routed_paths = tuple(
            tuple(routed_paths[index]) for index in range(len(rendered_edges))
        )

    def _preferred_faces(
        self, source: _Rectangle, target: _Rectangle
    ) -> Tuple[str, str]:
        if source == target:
            return ("right", "bottom") if self.direction == "right" else (
                "bottom",
                "right",
            )
        source_center = (
            (source.left + source.right) / 2,
            (source.top + source.bottom) / 2,
        )
        target_center = (
            (target.left + target.right) / 2,
            (target.top + target.bottom) / 2,
        )
        delta_x = target_center[0] - source_center[0]
        delta_y = target_center[1] - source_center[1]
        if abs(delta_x) >= abs(delta_y):
            return ("right", "left") if delta_x >= 0 else ("left", "right")
        return ("bottom", "top") if delta_y >= 0 else ("top", "bottom")

    @staticmethod
    def _port_points(
        rectangle: _Rectangle, face: str, fraction: float
    ) -> Tuple[_Point, _Point]:
        if face == "left":
            y = rectangle.top + (rectangle.bottom - rectangle.top) * fraction
            return (rectangle.left, y), (
                rectangle.left - _ROUTING_CLEARANCE,
                y,
            )
        if face == "right":
            y = rectangle.top + (rectangle.bottom - rectangle.top) * fraction
            return (rectangle.right, y), (
                rectangle.right + _ROUTING_CLEARANCE,
                y,
            )
        if face == "top":
            x = rectangle.left + (rectangle.right - rectangle.left) * fraction
            return (x, rectangle.top), (
                x,
                rectangle.top - _ROUTING_CLEARANCE,
            )
        x = rectangle.left + (rectangle.right - rectangle.left) * fraction
        return (x, rectangle.bottom), (
            x,
            rectangle.bottom + _ROUTING_CLEARANCE,
        )

    @staticmethod
    def _set_edge_port(
        edge: Edge, face: str, fraction: float, *, source: bool
    ) -> None:
        coordinates = {
            "left": (0.0, fraction),
            "right": (1.0, fraction),
            "top": (fraction, 0.0),
            "bottom": (fraction, 1.0),
        }[face]
        if source:
            edge.exitX, edge.exitY = coordinates
        else:
            edge.entryX, edge.entryY = coordinates

    @staticmethod
    def _routing_order_key(
        dependency: DependencyEdge, rectangles: Mapping[str, _Rectangle]
    ) -> Tuple[float, str, str]:
        source = rectangles[dependency.source]
        target = rectangles[dependency.target]
        distance = abs(
            (source.left + source.right) / 2 - (target.left + target.right) / 2
        ) + abs(
            (source.top + source.bottom) / 2
            - (target.top + target.bottom) / 2
        )
        return -distance, dependency.source, dependency.target

    @classmethod
    def _find_orthogonal_route(
        cls,
        start: _Point,
        end: _Point,
        obstacles: Sequence[_Rectangle],
        occupancy: _RouteOccupancy,
    ) -> List[_Point]:
        frame_margin = _ROUTING_CLEARANCE * 2
        xs = {start[0], end[0]}
        ys = {start[1], end[1]}
        for obstacle in obstacles:
            xs.update((obstacle.left, obstacle.right))
            ys.update((obstacle.top, obstacle.bottom))
        xs.update((min(xs) - frame_margin, max(xs) + frame_margin))
        ys.update((min(ys) - frame_margin, max(ys) + frame_margin))

        valid_points = {
            (x, y)
            for x in xs
            for y in ys
            if not cls._point_inside_obstacle((x, y), obstacles)
        }
        if start not in valid_points or end not in valid_points:
            raise RuntimeError("Unable to place a dependency edge outside node bounds")

        neighbors: Dict[_Point, List[_Point]] = {
            point: [] for point in valid_points
        }
        by_y: Dict[float, List[float]] = {}
        by_x: Dict[float, List[float]] = {}
        for x, y in valid_points:
            by_y.setdefault(y, []).append(x)
            by_x.setdefault(x, []).append(y)
        for y, row in by_y.items():
            row.sort()
            for left, right in zip(row, row[1:]):
                first, second = (left, y), (right, y)
                if cls._segment_clear(first, second, obstacles):
                    neighbors[first].append(second)
                    neighbors[second].append(first)
        for x, column in by_x.items():
            column.sort()
            for top, bottom in zip(column, column[1:]):
                first, second = (x, top), (x, bottom)
                if cls._segment_clear(first, second, obstacles):
                    neighbors[first].append(second)
                    neighbors[second].append(first)

        start_state = (start, "")
        costs = {start_state: 0.0}
        previous: Dict[Tuple[_Point, str], Tuple[_Point, str]] = {}
        pending: List[Tuple[float, float, _Point, str]] = [
            (cls._manhattan(start, end), 0.0, start, "")
        ]
        final_state: Optional[Tuple[_Point, str]] = None
        while pending:
            _, cost, point, incoming = heapq.heappop(pending)
            state = (point, incoming)
            if cost != costs.get(state):
                continue
            if point == end:
                final_state = state
                break
            for neighbor in sorted(neighbors[point]):
                direction = "h" if neighbor[1] == point[1] else "v"
                bend = _BEND_PENALTY if incoming and incoming != direction else 0
                route_penalty = occupancy.penalty(point, neighbor)
                next_cost = (
                    cost
                    + cls._manhattan(point, neighbor)
                    + bend
                    + route_penalty
                )
                next_state = (neighbor, direction)
                if next_cost < costs.get(next_state, math.inf):
                    costs[next_state] = next_cost
                    previous[next_state] = state
                    estimate = next_cost + cls._manhattan(neighbor, end)
                    heapq.heappush(
                        pending, (estimate, next_cost, neighbor, direction)
                    )

        if final_state is None:
            raise RuntimeError("Unable to route a dependency edge around node bounds")
        route = []
        state = final_state
        while True:
            route.append(state[0])
            if state == start_state:
                break
            state = previous[state]
        route.reverse()
        return cls._simplify_path(route)

    @staticmethod
    def _point_inside_obstacle(
        point: _Point, obstacles: Sequence[_Rectangle]
    ) -> bool:
        x, y = point
        return any(
            obstacle.left < x < obstacle.right
            and obstacle.top < y < obstacle.bottom
            for obstacle in obstacles
        )

    @staticmethod
    def _segment_clear(
        first: _Point, second: _Point, obstacles: Sequence[_Rectangle]
    ) -> bool:
        if first[1] == second[1]:
            left, right = sorted((first[0], second[0]))
            y = first[1]
            return not any(
                obstacle.top < y < obstacle.bottom
                and max(left, obstacle.left) < min(right, obstacle.right)
                for obstacle in obstacles
            )
        top, bottom = sorted((first[1], second[1]))
        x = first[0]
        return not any(
            obstacle.left < x < obstacle.right
            and max(top, obstacle.top) < min(bottom, obstacle.bottom)
            for obstacle in obstacles
        )

    @staticmethod
    def _segments_cross(
        first: _Point,
        second: _Point,
        other_first: _Point,
        other_second: _Point,
    ) -> bool:
        first_horizontal = first[1] == second[1]
        other_horizontal = other_first[1] == other_second[1]
        if first_horizontal == other_horizontal:
            return False
        horizontal_first, horizontal_second = (
            (first, second) if first_horizontal else (other_first, other_second)
        )
        vertical_first, vertical_second = (
            (other_first, other_second) if first_horizontal else (first, second)
        )
        horizontal_min, horizontal_max = sorted(
            (horizontal_first[0], horizontal_second[0])
        )
        vertical_min, vertical_max = sorted(
            (vertical_first[1], vertical_second[1])
        )
        return (
            horizontal_min < vertical_first[0] < horizontal_max
            and vertical_min < horizontal_first[1] < vertical_max
        )

    @classmethod
    def _paths_cross(
        cls, first_path: Sequence[_Point], second_path: Sequence[_Point]
    ) -> bool:
        return any(
            cls._segments_cross(first, second, other_first, other_second)
            for first, second in zip(first_path, first_path[1:])
            for other_first, other_second in zip(second_path, second_path[1:])
        )

    @staticmethod
    def _manhattan(first: _Point, second: _Point) -> float:
        return abs(first[0] - second[0]) + abs(first[1] - second[1])

    @staticmethod
    def _simplify_path(path: Sequence[_Point]) -> List[_Point]:
        simplified: List[_Point] = []
        for point in path:
            if simplified and point == simplified[-1]:
                continue
            if len(simplified) >= 2:
                first, second = simplified[-2:]
                if (first[0] == second[0] == point[0]) or (
                    first[1] == second[1] == point[1]
                ):
                    simplified[-1] = point
                    continue
            simplified.append(point)
        return simplified

    @staticmethod
    def _node_tooltip(node: DependencyNode) -> str:
        lines = [f"Kind: {node.kind.value.replace('_', ' ')}"]
        if node.source_paths:
            lines.append("Sources:")
            lines.extend(f"  {path}" for path in node.source_paths)
        if node.kind in {NodeKind.INTERNAL_MODULE, NodeKind.INTERNAL_PACKAGE}:
            lines.extend(
                (
                    f"Fan-in / Ca: {node.metrics.ca}",
                    f"Fan-out / Ce: {node.metrics.ce}",
                    f"Instability: {node.metrics.instability:.3f}",
                    f"SCC: {node.scc_id}",
                )
            )
            if node.cycle_id is not None:
                lines.append(f"Cycle: {node.cycle_id} ({node.cycle_size} nodes)")
            lines.append("Metrics measure static import coupling only.")
        return "\n".join(lines)

    @staticmethod
    def _edge_tooltip(edge: DependencyEdge) -> str:
        lines = [
            f"Dependency: {edge.source} -> {edge.target}",
            f"Import sites: {edge.weight}",
            f"Type-checking only: {'yes' if edge.type_checking_only else 'no'}",
        ]
        if edge.in_cycle:
            lines.append("Part of a dependency cycle")
        lines.append("Evidence:")
        lines.extend(
            f"  {item.source_path}:{item.line} — {item.imported_name}"
            + (" [TYPE_CHECKING]" if item.type_checking else "")
            for item in edge.evidence
        )
        return "\n".join(lines)

    def _fit_page(self) -> None:
        if not self.objects:
            return
        maximum_x = max(obj.position[0] + obj.width for obj in self.objects)
        maximum_y = max(obj.position[1] + obj.height for obj in self.objects)
        route_points = [
            point
            for edge in self.links
            for point in edge.geometry.points
        ]
        if route_points:
            maximum_x = max(maximum_x, max(point.x for point in route_points))
            maximum_y = max(maximum_y, max(point.y for point in route_points))
        self.page.width = max(850, maximum_x + self.padding)
        self.page.height = max(1100, maximum_y + self.padding)


__all__ = [
    "AnalysisDiagnostic",
    "CouplingMetrics",
    "DependencyAnalysis",
    "DependencyAnalysisError",
    "DependencyDiagram",
    "DependencyEdge",
    "DependencyKind",
    "DependencyNode",
    "DiagnosticSeverity",
    "ImportEvidence",
    "NodeKind",
]
