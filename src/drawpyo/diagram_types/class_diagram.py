from __future__ import annotations

import html
import importlib
import inspect
import pkgutil
from types import ModuleType
from typing import Any, Dict, Iterable, List, Optional, Tuple

from ..diagram.edges import Edge
from ..diagram.text_format import TextFormat
from .tree import NodeObject, TreeDiagram, TreeGroup


_PYTHON_BOOKKEEPING_NAMES = {
    "__annotate_func__",
    "__annotations__",
    "__classcell__",
    "__dict__",
    "__doc__",
    "__firstlineno__",
    "__module__",
    "__qualname__",
    "__slots__",
    "__static_attributes__",
    "__type_params__",
    "__weakref__",
}


class ClassDiagram(TreeDiagram):
    """A UML-style inheritance diagram built from a Python module or package."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._class_nodes: Dict[type, NodeObject] = {}
        self._additional_inheritances: List[Tuple[NodeObject, NodeObject]] = []

    @classmethod
    def create_from_module(
        cls,
        module: ModuleType,
        *,
        recursive: bool = True,
        include_private: bool = False,
        include_external: bool = True,
        **diagram_kwargs: Any,
    ) -> ClassDiagram:
        """Create and lay out a class diagram from an imported Python module.

        When ``module`` is a package and ``recursive`` is true, its submodules
        are imported and inspected as well. Classes from outside the supplied
        module are included only when they are immediate bases of an included
        class, and their members are not inspected.

        Args:
            module: An imported Python module or package.
            recursive: Import and inspect submodules when ``module`` is a package.
            include_private: Include underscore-prefixed classes and members.
            include_external: Include immediate external bases, except ``object``.
            **diagram_kwargs: Arguments forwarded to :class:`TreeDiagram`.

        Returns:
            A populated and automatically laid-out ``ClassDiagram``.
        """
        if not isinstance(module, ModuleType):
            raise TypeError("module must be an imported Python module or package")

        diagram = cls(**diagram_kwargs)
        diagram.process_module(
            module,
            recursive=recursive,
            include_private=include_private,
            include_external=include_external,
        )
        diagram.auto_layout()
        return diagram

    def process_module(
        self,
        module: ModuleType,
        *,
        recursive: bool = True,
        include_private: bool = False,
        include_external: bool = True,
    ) -> None:
        """Inspect ``module`` and add its classes to this diagram.

        This method populates the diagram but does not run layout. Most callers
        should use :meth:`create_from_module` instead.
        """
        if not isinstance(module, ModuleType):
            raise TypeError("module must be an imported Python module or package")
        if self.objects:
            raise ValueError("process_module can only populate an empty ClassDiagram")

        owned_classes = self._discover_classes(
            module, recursive=recursive, include_private=include_private
        )
        owned_set = set(owned_classes)

        external_bases = set()
        if include_external:
            root_name = module.__name__
            root_prefix = root_name + "."
            for class_obj in owned_classes:
                for base in class_obj.__bases__:
                    base_module = getattr(base, "__module__", "")
                    is_external = (
                        base_module != root_name
                        and not base_module.startswith(root_prefix)
                    )
                    if base is not object and base not in owned_set and is_external:
                        external_bases.add(base)

        for class_obj in sorted(owned_classes, key=self._qualified_class_name):
            self._class_nodes[class_obj] = self._create_class_node(
                class_obj, include_members=True, include_private=include_private
            )

        for class_obj in sorted(external_bases, key=self._qualified_class_name):
            self._class_nodes[class_obj] = self._create_class_node(
                class_obj, include_members=False, include_private=False
            )

        for class_obj in sorted(owned_classes, key=self._qualified_class_name):
            displayed_bases = [
                base for base in class_obj.__bases__ if base in self._class_nodes
            ]
            if not displayed_bases:
                continue

            class_node = self._class_nodes[class_obj]
            primary_base_node = self._class_nodes[displayed_bases[0]]
            class_node.tree_parent = primary_base_node

            for base in displayed_bases[1:]:
                self._additional_inheritances.append(
                    (class_node, self._class_nodes[base])
                )

    @classmethod
    def _discover_classes(
        cls,
        module: ModuleType,
        *,
        recursive: bool,
        include_private: bool,
    ) -> List[type]:
        root_name = module.__name__
        root_prefix = root_name + "."

        def is_owned(class_obj: type) -> bool:
            class_module = getattr(class_obj, "__module__", "")
            return class_module == root_name or class_module.startswith(root_prefix)

        classes = set()
        for inspected_module in cls._iter_modules(module, recursive=recursive):
            for _, class_obj in inspect.getmembers(inspected_module, inspect.isclass):
                if not is_owned(class_obj):
                    continue
                if not include_private and class_obj.__name__.startswith("_"):
                    continue
                classes.add(class_obj)

        return sorted(classes, key=cls._qualified_class_name)

    @staticmethod
    def _iter_modules(module: ModuleType, *, recursive: bool) -> Iterable[ModuleType]:
        yield module
        package_path = getattr(module, "__path__", None)
        if not recursive or package_path is None:
            return

        prefix = module.__name__ + "."

        def discovery_error(name: str) -> None:
            raise ImportError(f"Could not discover package submodule '{name}'")

        try:
            module_names = sorted(
                module_info.name
                for module_info in pkgutil.walk_packages(
                    package_path, prefix=prefix, onerror=discovery_error
                )
            )
        except Exception as exc:
            if isinstance(exc, ImportError) and str(exc).startswith(
                "Could not discover package submodule"
            ):
                raise
            raise ImportError(
                f"Could not discover submodules of package '{module.__name__}'"
            ) from exc

        for module_name in module_names:
            try:
                yield importlib.import_module(module_name)
            except Exception as exc:
                raise ImportError(
                    f"Could not import submodule '{module_name}'"
                ) from exc

    def _create_class_node(
        self,
        class_obj: type,
        *,
        include_members: bool,
        include_private: bool,
    ) -> NodeObject:
        class_name = self._qualified_class_name(class_obj)
        fields: List[str] = []
        methods: List[str] = []
        if include_members:
            fields = self._class_fields(class_obj, include_private=include_private)
            methods = self._class_methods(class_obj, include_private=include_private)

        label = self._class_label(
            class_name, fields=fields, methods=methods, include_members=include_members
        )
        member_lines = fields + methods
        longest_line = max([len(class_name)] + [len(line) for line in member_lines])
        width = max(180, min(480, 24 + longest_line * 7))
        height = 42
        if include_members:
            height += max(1, len(fields)) * 18 + max(1, len(methods)) * 18 + 14

        node = NodeObject(
            tree=self,
            value=label,
            width=width,
            height=height,
            rounded=0,
            text_format=TextFormat(
                formattedText=True,
                align="left",
                verticalAlign="top",
                spacing=6,
            ),
        )
        node.python_class = class_obj
        return node

    @staticmethod
    def _class_label(
        class_name: str,
        *,
        fields: List[str],
        methods: List[str],
        include_members: bool,
    ) -> str:
        header = (
            '<div style="text-align: center;"><b>'
            + html.escape(class_name)
            + "</b></div>"
        )
        if not include_members:
            return header

        field_text = "<br>".join(html.escape(field) for field in fields) or "<br>"
        method_text = "<br>".join(html.escape(method) for method in methods) or "<br>"
        return (
            header
            + '<hr><div style="text-align: left;">'
            + field_text
            + "</div>"
            + '<hr><div style="text-align: left;">'
            + method_text
            + "</div>"
        )

    @classmethod
    def _class_fields(cls, class_obj: type, *, include_private: bool) -> List[str]:
        namespace = vars(class_obj)
        try:
            annotations = inspect.get_annotations(class_obj, eval_str=False)
        except (TypeError, ValueError):
            annotations = namespace.get("__annotations__", {})
        fields: Dict[str, str] = {}

        for name, annotation in annotations.items():
            if cls._include_member(name, include_private=include_private):
                fields[name] = cls._format_annotation(annotation)

        for name, value in namespace.items():
            if name in fields or not cls._include_member(
                name, include_private=include_private
            ):
                continue
            if isinstance(value, property):
                annotation = inspect.Signature.empty
                if value.fget is not None:
                    try:
                        annotation = inspect.signature(
                            value.fget, eval_str=False
                        ).return_annotation
                    except (TypeError, ValueError):
                        pass
                fields[name] = cls._format_annotation(annotation)
            elif isinstance(value, (staticmethod, classmethod)):
                continue
            elif (
                inspect.isroutine(value)
                or inspect.isclass(value)
                or inspect.ismodule(value)
            ):
                continue
            elif inspect.isdatadescriptor(value):
                continue
            else:
                fields[name] = cls._format_annotation(type(value))

        return [
            f"{name}: {annotation}" if annotation else name
            for name, annotation in sorted(fields.items())
        ]

    @classmethod
    def _class_methods(cls, class_obj: type, *, include_private: bool) -> List[str]:
        methods = []
        for name, value in vars(class_obj).items():
            if not cls._include_member(name, include_private=include_private):
                continue

            drop_first_parameter = False
            if isinstance(value, staticmethod):
                function = value.__func__
            elif isinstance(value, classmethod):
                function = value.__func__
                drop_first_parameter = True
            elif inspect.isroutine(value):
                function = value
                drop_first_parameter = True
            else:
                continue

            try:
                signature = inspect.signature(function, eval_str=False)
                if drop_first_parameter and signature.parameters:
                    signature = signature.replace(
                        parameters=list(signature.parameters.values())[1:]
                    )
                methods.append(f"{name}{signature}")
            except (TypeError, ValueError):
                methods.append(f"{name}()")

        return sorted(methods)

    @staticmethod
    def _include_member(name: str, *, include_private: bool) -> bool:
        if name in _PYTHON_BOOKKEEPING_NAMES:
            return False
        return include_private or not name.startswith("_")

    @staticmethod
    def _format_annotation(annotation: Any) -> str:
        if annotation is inspect.Signature.empty:
            return ""
        if isinstance(annotation, str):
            return annotation
        try:
            return inspect.formatannotation(annotation)
        except (TypeError, ValueError):
            return getattr(annotation, "__qualname__", str(annotation))

    @staticmethod
    def _qualified_class_name(class_obj: type) -> str:
        module_name = getattr(class_obj, "__module__", "")
        class_name = getattr(class_obj, "__qualname__", class_obj.__name__)
        return f"{module_name}.{class_name}" if module_name else class_name

    def connect(
        self, source: NodeObject, target: NodeObject, label: Optional[str] = None
    ) -> None:
        """Connect a tree parent and child using UML inheritance semantics."""
        self._connect_inheritance(subclass=target, superclass=source, label=label)

    def _connect_inheritance(
        self,
        *,
        subclass: NodeObject,
        superclass: NodeObject,
        label: Optional[str] = None,
    ) -> None:
        edge = Edge(page=self.page, source=subclass, target=superclass, label=label)
        edge.apply_attribute_dict(self.link_style_dict)
        edge.line_end_target = "block"
        edge.endFill_target = False

        if self.direction == "down":
            edge.exitX, edge.exitY = 0.5, 0
            edge.entryX, edge.entryY = 0.5, 1
        elif self.direction == "up":
            edge.exitX, edge.exitY = 0.5, 1
            edge.entryX, edge.entryY = 0.5, 0
        elif self.direction == "left":
            edge.exitX, edge.exitY = 1, 0.5
            edge.entryX, edge.entryY = 0, 0.5
        elif self.direction == "right":
            edge.exitX, edge.exitY = 0, 0.5
            edge.entryX, edge.entryY = 1, 0.5
        self.links.append(edge)

    def auto_layout(self) -> TreeGroup:
        top_group = super().auto_layout()
        for subclass, superclass in self._additional_inheritances:
            self._connect_inheritance(subclass=subclass, superclass=superclass)
        return top_group
