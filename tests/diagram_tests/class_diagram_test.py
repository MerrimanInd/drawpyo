import importlib
import inspect
import sys
from types import ModuleType
from xml.etree import ElementTree

import pytest

from drawpyo.diagram_types import ClassDiagram


class ExternalBase:
    external_field: str

    def external_method(self):
        pass


def _sample_module():
    module = ModuleType("sample_library")
    module.ExternalBase = ExternalBase
    exec(
        """
class Base:
    count: int
    title = "drawpyo"
    _hidden_field: bytes

    @property
    def active(self) -> bool:
        return True

    def build(self, value: int) -> str:
        return str(value)

    def _hidden_method(self):
        pass

class Mixin:
    @staticmethod
    def normalize(value: str) -> str:
        return value

    @classmethod
    def create(cls, name: str):
        return cls()

class Derived(Base, Mixin, ExternalBase):
    payload: "Widget<T>"

class _PrivateClass:
    pass
""",
        module.__dict__,
    )
    module.BaseAlias = module.Base
    return module


def test_create_from_module_builds_uml_nodes_and_all_inheritances():
    module = _sample_module()

    diagram = ClassDiagram.create_from_module(module)

    assert set(diagram._class_nodes) == {
        module.Base,
        module.Mixin,
        module.Derived,
        ExternalBase,
    }
    assert len(diagram.objects) == 4
    assert module.Derived in diagram._class_nodes
    assert module._PrivateClass not in diagram._class_nodes
    assert object not in diagram._class_nodes

    derived_node = diagram._class_nodes[module.Derived]
    assert derived_node.tree_parent is diagram._class_nodes[module.Base]

    derived_edges = [edge for edge in diagram.links if edge.source is derived_node]
    assert {edge.target for edge in derived_edges} == {
        diagram._class_nodes[module.Base],
        diagram._class_nodes[module.Mixin],
        diagram._class_nodes[ExternalBase],
    }
    assert all(edge.line_end_target == "block" for edge in derived_edges)
    assert all(edge.endFill_target is False for edge in derived_edges)
    assert all("endArrow=block" in edge.style for edge in derived_edges)
    assert all("endFill=0" in edge.style for edge in derived_edges)


def test_owned_class_labels_include_declared_fields_and_method_signatures():
    module = _sample_module()

    diagram = ClassDiagram.create_from_module(module)
    base_label = diagram._class_nodes[module.Base].value
    mixin_label = diagram._class_nodes[module.Mixin].value
    derived_label = diagram._class_nodes[module.Derived].value
    external_label = diagram._class_nodes[ExternalBase].value

    assert "sample_library.Base" in base_label
    assert "count: int" in base_label
    assert "title: str" in base_label
    assert "active: bool" in base_label
    assert "build(value: int) -&gt; str" in base_label
    assert "_hidden_field" not in base_label
    assert "_hidden_method" not in base_label

    assert "normalize(value: str) -&gt; str" in mixin_label
    assert "create(name: str)" in mixin_label
    assert "payload: Widget&lt;T&gt;" in derived_label

    assert "tests.diagram_tests.class_diagram_test.ExternalBase" in external_label
    assert "<hr>" not in external_label
    assert "external_field" not in external_label
    assert "external_method" not in external_label


def test_private_classes_and_members_can_be_included():
    module = _sample_module()

    diagram = ClassDiagram.create_from_module(module, include_private=True)

    assert module._PrivateClass in diagram._class_nodes
    base_label = diagram._class_nodes[module.Base].value
    assert "_hidden_field: bytes" in base_label
    assert "_hidden_method()" in base_label
    assert "__dict__" not in base_label


def test_external_bases_can_be_excluded():
    module = _sample_module()

    diagram = ClassDiagram.create_from_module(module, include_external=False)

    assert ExternalBase not in diagram._class_nodes
    derived_node = diagram._class_nodes[module.Derived]
    assert {edge.target for edge in diagram.links if edge.source is derived_node} == {
        diagram._class_nodes[module.Base],
        diagram._class_nodes[module.Mixin],
    }


def test_diagram_kwargs_are_forwarded_and_xml_is_valid():
    module = _sample_module()

    diagram = ClassDiagram.create_from_module(
        module,
        direction="right",
        link_style="straight",
        file_name="Inheritance.drawio",
        file_path="/tmp/uml",
    )

    assert diagram.direction == "right"
    assert diagram.link_style == "straight"
    assert diagram.file_name == "Inheritance.drawio"
    assert diagram.file_path == "/tmp/uml"
    ElementTree.fromstring(diagram.file.xml)
    assert "Widget&amp;lt;T&amp;gt;" in diagram.file.xml


def test_recursive_package_discovery_and_reexport_deduplication(tmp_path, monkeypatch):
    package_name = "class_diagram_recursive_fixture"
    package_path = tmp_path / package_name
    package_path.mkdir()
    (package_path / "__init__.py").write_text(
        "from .models import Reexported\n", encoding="utf-8"
    )
    (package_path / "models.py").write_text(
        "class Reexported:\n    pass\n\nclass Child(Reexported):\n    pass\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    package = importlib.import_module(package_name)
    try:
        non_recursive = ClassDiagram.create_from_module(package, recursive=False)
        recursive = ClassDiagram.create_from_module(package, recursive=True)

        assert len(non_recursive.objects) == 1
        assert len(recursive.objects) == 2
        qualified_names = {
            ClassDiagram._qualified_class_name(class_obj)
            for class_obj in recursive._class_nodes
        }
        assert qualified_names == {
            f"{package_name}.models.Reexported",
            f"{package_name}.models.Child",
        }
    finally:
        for name in list(sys.modules):
            if name == package_name or name.startswith(package_name + "."):
                del sys.modules[name]


def test_submodule_import_failures_identify_the_module(tmp_path, monkeypatch):
    package_name = "class_diagram_broken_fixture"
    package_path = tmp_path / package_name
    package_path.mkdir()
    (package_path / "__init__.py").write_text("", encoding="utf-8")
    (package_path / "broken.py").write_text(
        'raise RuntimeError("cannot initialize")\n', encoding="utf-8"
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    package = importlib.import_module(package_name)
    try:
        with pytest.raises(
            ImportError, match=f"Could not import submodule '{package_name}.broken'"
        ):
            ClassDiagram.create_from_module(package)
    finally:
        for name in list(sys.modules):
            if name == package_name or name.startswith(package_name + "."):
                del sys.modules[name]


def test_rejects_non_module_input_and_repopulation():
    with pytest.raises(TypeError, match="imported Python module"):
        ClassDiagram.create_from_module("sample_library")

    module = _sample_module()
    diagram = ClassDiagram()
    diagram.process_module(module)
    with pytest.raises(ValueError, match="empty ClassDiagram"):
        diagram.process_module(module)


def test_empty_module_and_unavailable_signatures_are_handled(monkeypatch):
    empty_module = ModuleType("empty_library")
    empty_diagram = ClassDiagram.create_from_module(empty_module)
    assert empty_diagram.objects == []
    assert empty_diagram.links == []

    module = _sample_module()
    original_signature = inspect.signature

    def unavailable_signature(value, **kwargs):
        if getattr(value, "__name__", "") == "build":
            raise ValueError("signature unavailable")
        return original_signature(value, **kwargs)

    monkeypatch.setattr(
        "drawpyo.diagram_types.class_diagram.inspect.signature",
        unavailable_signature,
    )
    diagram = ClassDiagram.create_from_module(module)
    assert "build()" in diagram._class_nodes[module.Base].value
