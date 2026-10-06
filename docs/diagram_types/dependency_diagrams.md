# Python Dependency Diagrams

`DependencyDiagram` statically analyzes Python source and draws imports between
modules or packages. The analyzed source is parsed with Python's `ast` module;
it is never imported or executed.

An edge points from the importing module or package to the dependency it
imports. The diagram distinguishes internal modules and packages, standard
library modules, and third-party or otherwise external dependencies. Cyclic
dependencies are highlighted.

## Create a Diagram

Pass a Python package, source directory, or `.py` file to `create_from_path`:

```python
from drawpyo.diagram_types import DependencyDiagram

diagram = DependencyDiagram.create_from_path(
    "src/example_package",
    file_path="path/to/diagrams",
    file_name="Package Dependencies.drawio",
    granularity="module",
)

diagram.write()
```

The default view includes internal and third-party dependencies, excludes
standard-library dependencies and test modules, and includes imports guarded
by `TYPE_CHECKING`. External dependencies are context nodes only and are not
recursively analyzed.

## Source Roots and Namespaces

A directory containing `__init__.py` is treated as a package root. The root
package uses the directory name, and its `__init__.py` is represented by that
package name rather than by an `.__init__` module.

A directory without `__init__.py` is treated as a source root, like `src/`.
Module names are derived from paths relative to that directory. Namespace
package directories are represented as package nodes even when they have no
`__init__.py`.

Use `namespace` to restrict a source root to one package subtree:

```python
diagram = DependencyDiagram.create_from_path(
    "src",
    namespace="company.analytics",
)
```

When analyzing a namespace package directly, pass its containing source root
and select the namespace. This makes every missing parent namespace component
explicit instead of guessing it from a directory basename.

## Granularity

`granularity="module"` creates one node for each Python module and package.

`granularity="package"` maps each module to its deepest containing package.
Imports between the same package pair are merged, and their import-site counts
are added. Imports that remain within one aggregated package are omitted.
Loose top-level modules with no package ancestor remain module nodes.

## Filtering and Display Options

| Parameter | Default | Effect |
| --- | --- | --- |
| `granularity` | `"module"` | Use module or package nodes. |
| `include_external` | `True` | Include third-party and otherwise unresolved absolute imports. |
| `include_standard_library` | `False` | Include standard-library context nodes. |
| `include_type_checking` | `True` | Include imports guarded directly by `TYPE_CHECKING`. |
| `exclude_tests` | `True` | Exclude test directories and conventional test filenames. |
| `exclude_patterns` | `()` | Add relative POSIX-style glob exclusions. |
| `namespace` | `None` | Restrict a source-root scan to a dotted namespace. |
| `strict` | `False` | Raise on incomplete source analysis instead of retaining diagnostics. |
| `show_metrics` | `False` | Add coupling values to internal node labels. |
| `show_edge_weights` | `False` | Label repeated dependencies and scale their edge width. |
| `show_legend` | `True` | Add the node and edge style legend. |
| `direction` | `"right"` | Lay out dependencies left-to-right; `"down"` is also supported. |
| `link_style` | `"orthogonal"` | Draw routed links as orthogonal, piecewise straight, or curved. |

Common virtual environments, caches, build outputs, version-control folders,
and hidden tool directories are ignored automatically.

## Layout and Routing

Dependency diagrams reserve corridors between nodes and route every connector
around unrelated node shapes. Connection points are spread across node faces so
that fan-in and fan-out remain distinguishable. The router also reduces shared
segments and crossings where possible and uses line jumps for crossings that
cannot be avoided.

Obstacle avoidance applies to every `link_style`. Consequently, `straight`
means piecewise-straight: a link remains a single straight segment when the
path is clear and receives bends when required to avoid a node. Layout and
routing are deterministic for the same analysis and options. Spacing options
are treated as requested minimums; the generator may reserve additional room
when a routing corridor requires it.

## Import Resolution

Absolute imports retain their stated module path. Relative imports are
resolved from the importing module's package. For an import such as
`from package import name`, the analyzer uses `package.name` when that exact
internal submodule exists; otherwise it records a dependency on `package`
because static analysis cannot know whether `name` is an attribute or an
unavailable submodule.

Imports inside functions, methods, classes, and ordinary conditional branches
are treated like top-level imports. Direct guards using `TYPE_CHECKING`, an
alias imported from `typing`, or `typing_alias.TYPE_CHECKING` are detected and
drawn with dashed edges. If a dependency has both runtime and type-only import
sites, its merged edge is solid.

One edge weight is counted per import statement and resolved target. Multiple
names in one `from` statement that resolve to the same target count once;
repeated statements count separately. Source paths and line numbers are kept
as edge evidence and shown in tooltips. Stored source and evidence paths are
relative to the inferred source root; `analysis.source_path` retains the
absolute input path.

Standard-library classification uses the running interpreter's
`sys.stdlib_module_names` and built-in module names. A discovered internal
module always takes precedence over that classification. Every other
non-internal absolute import is classified as external without probing the
environment.

## Metrics and Cycles

Metrics are calculated from distinct internal import relationships:

- fan-in and afferent coupling (`Ca`) count internal nodes importing a node;
- fan-out and efferent coupling (`Ce`) count internal nodes imported by it;
- instability is `Ce / (Ca + Ce)`, or `0.0` for an isolated node.

Repeated imports affect edge weight, not coupling. Standard-library and
external edges do not affect coupling. These values measure static import
coupling only; they do not describe runtime calls or every form of
architectural coupling.

Strongly connected components are calculated from the internal graph. A
component with multiple nodes is a cycle, as is a one-node component with an
explicit self-import. Cycle nodes and edges use warning colors. Full SCC and
cycle memberships are available from `diagram.analysis`.

## Diagnostics and Limitations

Invalid syntax, unreadable nested files, and unresolved relative imports are
skipped and recorded in `diagram.analysis.diagnostics`. Pass `strict=True` to
raise `DependencyAnalysisError` when these conditions occur. Missing paths,
invalid input types, duplicate module names, missing namespaces, and source
roots with no Python files always raise immediately.

Dynamic imports through `importlib.import_module()`, `__import__()`, generated
code, and runtime call relationships are not analyzed. Conditions other than
direct `TYPE_CHECKING` guards are not evaluated, so imports in those branches
are conservatively included.
