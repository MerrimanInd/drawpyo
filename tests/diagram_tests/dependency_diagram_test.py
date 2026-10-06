from pathlib import Path
from xml.etree import ElementTree

import pytest

import drawpyo.diagram_types.dependency_diagram as dependency_module
from drawpyo.diagram_types import (
    DependencyAnalysis,
    DependencyAnalysisError,
    DependencyDiagram,
)
from drawpyo.diagram_types.dependency_diagram import (
    DependencyKind,
    DiagnosticSeverity,
    NodeKind,
)


def _package(tmp_path: Path, name: str = "sample") -> Path:
    package = tmp_path / name
    package.mkdir()
    (package / "__init__.py").write_text("", encoding="utf-8")
    return package


def _edge(diagram: DependencyDiagram, source: str, target: str):
    assert diagram.analysis is not None
    return next(
        edge
        for edge in diagram.analysis.edges
        if edge.source == source and edge.target == target
    )


def test_absolute_relative_aliased_and_local_imports_are_analyzed_without_execution(
    tmp_path,
):
    package = _package(tmp_path)
    subpackage = package / "sub"
    subpackage.mkdir()
    (subpackage / "__init__.py").write_text("", encoding="utf-8")
    (subpackage / "helper.py").write_text("VALUE = 1\n", encoding="utf-8")
    (package / "main.py").write_text(
        "raise RuntimeError('must not execute')\n"
        "import os\n"
        "import requests as http\n"
        "from .sub import helper as helper_alias\n"
        "from requests import Session, adapters\n"
        "def load():\n"
        "    import decimal\n",
        encoding="utf-8",
    )

    diagram = DependencyDiagram.create_from_path(
        package, include_standard_library=True, show_legend=False
    )

    assert set(diagram.analysis.nodes) == {
        "decimal",
        "os",
        "requests",
        "sample",
        "sample.main",
        "sample.sub",
        "sample.sub.helper",
    }
    assert diagram.analysis.nodes["os"].kind == NodeKind.STANDARD_LIBRARY
    assert diagram.analysis.nodes["requests"].kind == NodeKind.EXTERNAL
    internal_edge = _edge(diagram, "sample.main", "sample.sub.helper")
    assert internal_edge.kind == DependencyKind.INTERNAL
    assert internal_edge.evidence[0].source_path == Path("sample/main.py")
    assert _edge(diagram, "sample.main", "requests").weight == 2
    assert _edge(diagram, "sample.main", "decimal").weight == 1


def test_from_import_prefers_known_submodule_and_falls_back_to_package(tmp_path):
    package = _package(tmp_path)
    (package / "models.py").write_text("class Entity: pass\n", encoding="utf-8")
    (package / "consumer.py").write_text(
        "from . import models\nfrom .models import Entity, Missing\n",
        encoding="utf-8",
    )

    diagram = DependencyDiagram.create_from_path(package, show_legend=False)

    assert _edge(diagram, "sample.consumer", "sample.models").weight == 2


def test_relative_imports_at_multiple_levels_and_unresolved_imports(tmp_path):
    package = _package(tmp_path)
    domain = package / "domain"
    domain.mkdir()
    (domain / "__init__.py").write_text("", encoding="utf-8")
    (domain / "entities.py").write_text("class Entity: pass\n", encoding="utf-8")
    feature = package / "feature"
    feature.mkdir()
    (feature / "__init__.py").write_text("", encoding="utf-8")
    (feature / "service.py").write_text(
        "from ..domain import entities\nfrom ...missing import value\n",
        encoding="utf-8",
    )

    diagram = DependencyDiagram.create_from_path(package, show_legend=False)

    assert _edge(diagram, "sample.feature.service", "sample.domain.entities")
    diagnostic = next(
        item
        for item in diagram.diagnostics
        if item.code == "unresolved_relative_import"
    )
    assert diagnostic.path == feature / "service.py"
    assert diagnostic.line == 2

    with pytest.raises(DependencyAnalysisError):
        DependencyDiagram.create_from_path(package, strict=True, show_legend=False)


def test_type_checking_imports_are_detected_filtered_and_merged(tmp_path):
    package = _package(tmp_path)
    (package / "models.py").write_text("class Model: pass\n", encoding="utf-8")
    (package / "consumer.py").write_text(
        "import typing as t\n"
        "from typing import TYPE_CHECKING as TC\n"
        "if t.TYPE_CHECKING:\n"
        "    from . import models\n"
        "if TC:\n"
        "    import optional_types\n"
        "else:\n"
        "    import runtime_dep\n",
        encoding="utf-8",
    )

    diagram = DependencyDiagram.create_from_path(package, show_legend=False)
    assert _edge(diagram, "sample.consumer", "sample.models").type_checking_only is True
    assert (
        _edge(diagram, "sample.consumer", "optional_types").type_checking_only is True
    )
    assert _edge(diagram, "sample.consumer", "runtime_dep").type_checking_only is False

    filtered = DependencyDiagram.create_from_path(
        package, include_type_checking=False, show_legend=False
    )
    assert "optional_types" not in filtered.analysis.nodes
    assert not any(edge.target == "sample.models" for edge in filtered.analysis.edges)
    assert "runtime_dep" in filtered.analysis.nodes


def test_runtime_and_type_checking_sites_merge_into_a_runtime_edge(tmp_path):
    package = _package(tmp_path)
    (package / "consumer.py").write_text(
        "from typing import TYPE_CHECKING\n"
        "import shared_dependency\n"
        "if TYPE_CHECKING:\n"
        "    import shared_dependency\n",
        encoding="utf-8",
    )

    diagram = DependencyDiagram.create_from_path(package, show_legend=False)
    edge = _edge(diagram, "sample.consumer", "shared_dependency")

    assert edge.weight == 2
    assert edge.type_checking_only is False
    assert {item.type_checking for item in edge.evidence} == {False, True}


def test_duplicate_statements_affect_weight_but_not_metrics(tmp_path):
    package = _package(tmp_path)
    (package / "target.py").write_text("VALUE = 1\n", encoding="utf-8")
    (package / "source.py").write_text(
        "from .target import VALUE, Missing\n"
        "from .target import VALUE\n"
        "from .target import VALUE\n",
        encoding="utf-8",
    )

    diagram = DependencyDiagram.create_from_path(package, show_legend=False)

    edge = _edge(diagram, "sample.source", "sample.target")
    assert edge.weight == 3
    assert len(edge.evidence) == 3
    source_metrics = diagram.analysis.nodes["sample.source"].metrics
    target_metrics = diagram.analysis.nodes["sample.target"].metrics
    assert (source_metrics.fan_out, source_metrics.ce) == (1, 1)
    assert (target_metrics.fan_in, target_metrics.ca) == (1, 1)
    assert source_metrics.instability == 1.0
    assert target_metrics.instability == 0.0


def test_isolated_nodes_self_imports_and_cycles_have_stable_membership(tmp_path):
    package = _package(tmp_path)
    (package / "a.py").write_text("from . import b\n", encoding="utf-8")
    (package / "b.py").write_text("from . import a\n", encoding="utf-8")
    (package / "self_ref.py").write_text("import sample.self_ref\n", encoding="utf-8")
    (package / "isolated.py").write_text("VALUE = 1\n", encoding="utf-8")

    diagram = DependencyDiagram.create_from_path(package, show_legend=False)

    assert diagram.analysis.cycles == (
        ("sample.a", "sample.b"),
        ("sample.self_ref",),
    )
    assert _edge(diagram, "sample.a", "sample.b").in_cycle
    assert _edge(diagram, "sample.b", "sample.a").in_cycle
    self_node = diagram.analysis.nodes["sample.self_ref"]
    assert self_node.cycle_size == 1
    assert self_node.metrics.ca == self_node.metrics.ce == 0
    isolated = diagram.analysis.nodes["sample.isolated"]
    assert isolated.metrics.instability == 0.0
    assert isolated.cycle_id is None


def test_package_granularity_aggregates_sources_edges_and_metrics(tmp_path):
    package = _package(tmp_path)
    left = package / "left"
    right = package / "right"
    left.mkdir()
    right.mkdir()
    (left / "__init__.py").write_text("", encoding="utf-8")
    (right / "__init__.py").write_text("", encoding="utf-8")
    (left / "one.py").write_text("from ..right import two\n", encoding="utf-8")
    (left / "extra.py").write_text("from ..right import two\n", encoding="utf-8")
    (right / "two.py").write_text("VALUE = 1\n", encoding="utf-8")

    diagram = DependencyDiagram.create_from_path(
        package, granularity="package", show_legend=False
    )

    assert set(diagram.analysis.nodes) == {"sample", "sample.left", "sample.right"}
    edge = _edge(diagram, "sample.left", "sample.right")
    assert edge.weight == 2
    assert diagram.analysis.nodes["sample.left"].kind == NodeKind.INTERNAL_PACKAGE
    assert len(diagram.analysis.nodes["sample.left"].source_paths) == 3
    assert diagram.analysis.nodes["sample.left"].metrics.ce == 1
    assert diagram.analysis.nodes["sample.right"].metrics.ca == 1


def test_package_granularity_removes_intra_package_edges(tmp_path):
    package = _package(tmp_path)
    (package / "a.py").write_text("from . import b\n", encoding="utf-8")
    (package / "b.py").write_text("from . import a\n", encoding="utf-8")

    diagram = DependencyDiagram.create_from_path(
        package, granularity="package", show_legend=False
    )

    assert set(diagram.analysis.nodes) == {"sample"}
    assert diagram.analysis.edges == ()
    assert diagram.analysis.cycles == ()


def test_source_root_namespace_packages_and_namespace_filter(tmp_path):
    source_root = tmp_path / "src"
    package = source_root / "acme" / "widgets"
    package.mkdir(parents=True)
    (package / "core.py").write_text("from . import helpers\n", encoding="utf-8")
    (package / "helpers.py").write_text("VALUE = 1\n", encoding="utf-8")
    other = source_root / "other"
    other.mkdir()
    (other / "module.py").write_text("VALUE = 1\n", encoding="utf-8")

    diagram = DependencyDiagram.create_from_path(
        source_root, namespace="acme.widgets", show_legend=False
    )

    assert diagram.analysis.root_name == "acme.widgets"
    assert set(diagram.analysis.nodes) == {
        "acme.widgets",
        "acme.widgets.core",
        "acme.widgets.helpers",
    }
    assert diagram.analysis.nodes["acme.widgets"].kind == NodeKind.INTERNAL_PACKAGE
    assert _edge(diagram, "acme.widgets.core", "acme.widgets.helpers")


def test_external_standard_library_and_test_filters(tmp_path):
    package = _package(tmp_path)
    (package / "main.py").write_text(
        "import json\nimport third_party\n", encoding="utf-8"
    )
    tests = package / "tests"
    tests.mkdir()
    (tests / "test_main.py").write_text("import test_dependency\n", encoding="utf-8")
    (package / "ignored.py").write_text("import ignored_dep\n", encoding="utf-8")

    defaults = DependencyDiagram.create_from_path(
        package, exclude_patterns=("ignored.py",), show_legend=False
    )
    assert "third_party" in defaults.analysis.nodes
    assert "json" not in defaults.analysis.nodes
    assert "sample.tests.test_main" not in defaults.analysis.nodes
    assert "sample.ignored" not in defaults.analysis.nodes

    internal_only = DependencyDiagram.create_from_path(
        package, include_external=False, show_legend=False
    )
    assert "third_party" not in internal_only.analysis.nodes

    all_context = DependencyDiagram.create_from_path(
        package,
        include_standard_library=True,
        exclude_tests=False,
        show_legend=False,
    )
    assert all_context.analysis.nodes["json"].kind == NodeKind.STANDARD_LIBRARY
    assert "sample.tests.test_main" in all_context.analysis.nodes
    assert "test_dependency" in all_context.analysis.nodes


def test_internal_module_name_takes_precedence_over_standard_library(tmp_path):
    source_root = tmp_path / "source"
    source_root.mkdir()
    (source_root / "json.py").write_text("VALUE = 1\n", encoding="utf-8")
    (source_root / "consumer.py").write_text("import json\n", encoding="utf-8")

    diagram = DependencyDiagram.create_from_path(
        source_root, include_standard_library=True, show_legend=False
    )

    assert diagram.analysis.nodes["json"].kind == NodeKind.INTERNAL_MODULE
    assert _edge(diagram, "consumer", "json").kind == DependencyKind.INTERNAL


def test_invalid_syntax_is_diagnosed_and_valid_modules_still_render(tmp_path):
    package = _package(tmp_path)
    (package / "broken.py").write_text("def broken(:\n", encoding="utf-8")
    (package / "valid.py").write_text("import dependency\n", encoding="utf-8")

    diagram = DependencyDiagram.create_from_path(package, show_legend=False)

    assert "sample.broken" in diagram.analysis.nodes
    diagnostic = next(
        item for item in diagram.diagnostics if item.code == "invalid_syntax"
    )
    assert diagnostic.severity == DiagnosticSeverity.ERROR
    assert diagnostic.path == package / "broken.py"
    assert "dependency" in diagram.analysis.nodes


def test_unreadable_file_is_diagnosed(monkeypatch, tmp_path):
    package = _package(tmp_path)
    blocked = package / "blocked.py"
    blocked.write_text("import dependency\n", encoding="utf-8")
    real_open = dependency_module.tokenize.open

    def unavailable(path):
        if Path(path) == blocked:
            raise OSError("permission denied")
        return real_open(path)

    monkeypatch.setattr(dependency_module.tokenize, "open", unavailable)

    diagram = DependencyDiagram.create_from_path(package, show_legend=False)

    diagnostic = next(
        item for item in diagram.diagnostics if item.code == "unreadable_source"
    )
    assert diagnostic.path == blocked


@pytest.mark.parametrize(
    "setup, exception",
    [
        (lambda path: path / "missing", FileNotFoundError),
        (
            lambda path: (path / "notes.txt"),
            ValueError,
        ),
        (lambda path: path / "empty", ValueError),
    ],
)
def test_invalid_inputs_raise_actionable_errors(tmp_path, setup, exception):
    target = setup(tmp_path)
    if target.suffix:
        target.write_text("notes", encoding="utf-8")
    elif target.name == "empty":
        target.mkdir()
    with pytest.raises(exception):
        DependencyDiagram.create_from_path(target)


def test_duplicate_module_names_are_rejected(tmp_path):
    source_root = tmp_path / "source"
    source_root.mkdir()
    (source_root / "conflict.py").write_text("", encoding="utf-8")
    namespace = source_root / "conflict"
    namespace.mkdir()
    (namespace / "child.py").write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="Duplicate module name 'conflict'"):
        DependencyDiagram.create_from_path(source_root)


def test_empty_regular_package_and_no_edge_graph_are_valid(tmp_path):
    package = _package(tmp_path)

    diagram = DependencyDiagram.create_from_path(package, show_legend=False)

    assert set(diagram.analysis.nodes) == {"sample"}
    assert diagram.analysis.edges == ()
    ElementTree.fromstring(diagram.file.xml)


def test_rendering_styles_tooltips_layout_and_options_are_forwarded(tmp_path):
    package = _package(tmp_path)
    (package / "a.py").write_text(
        "from . import b\nfrom . import b\n", encoding="utf-8"
    )
    (package / "b.py").write_text("from . import a\n", encoding="utf-8")

    diagram = DependencyDiagram.create_from_path(
        package,
        show_metrics=True,
        show_edge_weights=True,
        direction="down",
        link_style="straight",
        layer_spacing=220,
        node_spacing=55,
        component_spacing=120,
        padding=30,
        file_path=tmp_path,
        file_name="Dependencies.drawio",
    )

    assert isinstance(diagram.analysis, DependencyAnalysis)
    assert diagram.file_path == str(tmp_path)
    assert diagram.file_name == "Dependencies.drawio"
    assert diagram.direction == "down"
    assert diagram.layer_spacing == 220
    rendered_edge = next(
        edge
        for edge in diagram.links
        if edge.source is diagram._node_objects["sample.a"]
        and edge.target is diagram._node_objects["sample.b"]
    )
    assert rendered_edge.label == "×2"
    assert rendered_edge.strokeColor == "#B85450"
    assert rendered_edge.strokeWidth == 3
    assert "Import sites: 2" in rendered_edge.tooltip
    single_weight_edge = next(
        edge
        for edge in diagram.links
        if edge.source is diagram._node_objects["sample.b"]
        and edge.target is diagram._node_objects["sample.a"]
    )
    assert single_weight_edge.label is None
    assert ElementTree.fromstring(single_weight_edge.xml).get("label") == ""
    assert "Ca" in diagram._node_objects["sample.a"].value
    assert diagram._node_objects["sample.a"].fillColor == "#F8CECC"
    ElementTree.fromstring(diagram.file.xml)
    written = diagram.write()
    assert written == str(tmp_path / "Dependencies.drawio")
    assert (tmp_path / "Dependencies.drawio").is_file()


def test_type_checking_edges_are_dashed_and_external_nodes_are_compact(tmp_path):
    package = _package(tmp_path)
    (package / "main.py").write_text(
        "from typing import TYPE_CHECKING\n"
        "if TYPE_CHECKING:\n"
        "    import optional_dependency\n",
        encoding="utf-8",
    )

    diagram = DependencyDiagram.create_from_path(package, show_legend=False)
    dependency = _edge(diagram, "sample.main", "optional_dependency")
    rendered = next(
        edge
        for edge in diagram.links
        if edge.source is diagram._node_objects[dependency.source]
        and edge.target is diagram._node_objects[dependency.target]
    )
    assert rendered.pattern == "dashed_medium"
    assert diagram._node_objects["optional_dependency"].width <= 260


def test_disconnected_layout_and_analysis_order_are_deterministic(tmp_path):
    package = _package(tmp_path)
    (package / "z.py").write_text("import z_external\n", encoding="utf-8")
    (package / "a.py").write_text("import a_external\n", encoding="utf-8")

    first = DependencyDiagram.create_from_path(package, show_legend=False)
    second = DependencyDiagram.create_from_path(package, show_legend=False)

    assert list(first.analysis.nodes) == list(second.analysis.nodes)
    assert first.analysis.edges == second.analysis.edges
    assert {node_id: obj.position for node_id, obj in first._node_objects.items()} == {
        node_id: obj.position for node_id, obj in second._node_objects.items()
    }
    assert len(set(obj.position for obj in first._node_objects.values())) == len(
        first._node_objects
    )


@pytest.mark.parametrize("direction", ["right", "down"])
@pytest.mark.parametrize("link_style", ["orthogonal", "straight", "curved"])
def test_routes_avoid_unrelated_nodes_for_every_link_style(
    tmp_path, direction, link_style
):
    package = _package(tmp_path)
    (package / "a.py").write_text(
        "from . import b\nfrom . import c\n", encoding="utf-8"
    )
    (package / "b.py").write_text("from . import c\n", encoding="utf-8")
    (package / "c.py").write_text("", encoding="utf-8")

    diagram = DependencyDiagram.create_from_path(
        package,
        direction=direction,
        link_style=link_style,
        show_legend=False,
    )

    def crosses_interior(first, second, obj):
        left, top = obj.position
        right, bottom = left + obj.width, top + obj.height
        if first[1] == second[1]:
            segment_left, segment_right = sorted((first[0], second[0]))
            return (
                top < first[1] < bottom
                and max(segment_left, left) < min(segment_right, right)
            )
        segment_top, segment_bottom = sorted((first[1], second[1]))
        return (
            left < first[0] < right
            and max(segment_top, top) < min(segment_bottom, bottom)
        )

    for dependency, path in zip(diagram.analysis.edges, diagram._routed_paths):
        assert all(
            not crosses_interior(first, second, obj)
            for node_id, obj in diagram._node_objects.items()
            if node_id not in {dependency.source, dependency.target}
            for first, second in zip(path, path[1:])
        )

    outgoing = [
        edge
        for dependency, edge in zip(diagram.analysis.edges, diagram.links)
        if dependency.source == "sample.a"
    ]
    assert len({(edge.exitX, edge.exitY) for edge in outgoing}) == len(outgoing)
    assert any(edge.geometry.points for edge in diagram.links)


def test_obstacle_aware_routes_are_deterministic(tmp_path):
    package = _package(tmp_path)
    (package / "a.py").write_text(
        "from . import b\nfrom . import c\n", encoding="utf-8"
    )
    (package / "b.py").write_text("from . import c\n", encoding="utf-8")
    (package / "c.py").write_text("", encoding="utf-8")

    first = DependencyDiagram.create_from_path(package, show_legend=False)
    second = DependencyDiagram.create_from_path(package, show_legend=False)

    assert first._routed_paths == second._routed_paths
    assert [
        (edge.exitX, edge.exitY, edge.entryX, edge.entryY)
        for edge in first.links
    ] == [
        (edge.exitX, edge.exitY, edge.entryX, edge.entryY)
        for edge in second.links
    ]
    assert any(edge.jumpStyle == "arc" for edge in first.links)


def test_single_python_file_and_missing_namespace(tmp_path):
    module = tmp_path / "single.py"
    module.write_text("import dependency\n", encoding="utf-8")

    diagram = DependencyDiagram.create_from_path(module, show_legend=False)
    assert {"single", "dependency"} == set(diagram.analysis.nodes)

    with pytest.raises(ValueError, match="was not found"):
        DependencyDiagram.create_from_path(
            tmp_path, namespace="unknown", show_legend=False
        )


def test_single_file_inside_regular_package_keeps_package_context(tmp_path):
    package = _package(tmp_path)
    (package / "target.py").write_text("VALUE = 1\n", encoding="utf-8")
    source = package / "source.py"
    source.write_text("from . import target\n", encoding="utf-8")

    diagram = DependencyDiagram.create_from_path(source, show_legend=False)

    assert diagram.analysis.root_name == "sample"
    assert set(diagram.analysis.nodes) == {"sample", "sample.source"}
    assert _edge(diagram, "sample.source", "sample")


def test_invalid_options_are_rejected(tmp_path):
    package = _package(tmp_path)
    with pytest.raises(ValueError, match="granularity"):
        DependencyDiagram.create_from_path(package, granularity="class")
    with pytest.raises(ValueError, match="direction"):
        DependencyDiagram.create_from_path(package, direction="left")
    with pytest.raises(ValueError, match="positive integer"):
        DependencyDiagram.create_from_path(package, node_spacing=0)


def test_large_graph_is_rendered_with_a_warning_diagnostic(tmp_path):
    source_root = tmp_path / "large"
    source_root.mkdir()
    for index in range(101):
        (source_root / f"module_{index:03}.py").write_text("", encoding="utf-8")

    diagram = DependencyDiagram.create_from_path(source_root, show_legend=False)

    assert len(diagram.analysis.nodes) == 101
    warning = next(item for item in diagram.diagnostics if item.code == "large_graph")
    assert warning.severity == DiagnosticSeverity.WARNING
