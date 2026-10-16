# Class Diagrams

`ClassDiagram` creates a UML-style view of the classes and inheritance
relationships in an imported Python module or package. Class boxes contain the
fields and methods declared directly on each class, and inheritance is shown
with an unfilled triangular arrow pointing to the base class.

## Create a Diagram

Import the package to inspect, then pass the module object to
`create_from_module`:

```python
import drawpyo
from drawpyo.diagram_types import ClassDiagram

diagram = ClassDiagram.create_from_module(
    drawpyo,
    file_path="path/to/diagrams",
    file_name="Drawpyo classes.drawio",
)

diagram.write()
```

The diagram is laid out automatically. Standard tree formatting options such
as `direction`, `link_style`, `level_spacing`, and `item_spacing` can be passed
to `create_from_module` alongside the file options.

## Discovery Options

| Parameter | Default | Effect |
| --------- | ------- | ------ |
| `recursive` | `True` | For a package, discover and import its submodules before inspecting them. |
| `include_private` | `False` | Include underscore-prefixed classes and members. Python bookkeeping attributes remain hidden. |
| `include_external` | `True` | Add compact nodes for immediate bases defined outside the inspected package. `object` is always omitted. |

Recursive discovery imports package submodules normally, so their import-time
code runs. If a submodule cannot be imported, `create_from_module` raises an
`ImportError` that identifies that submodule. Pass `recursive=False` to inspect
only classes exposed by the supplied module object.

## Class Contents

Owned class boxes show:

- directly declared annotated fields and class attributes;
- properties, using their return annotation when available;
- directly declared instance, class, and static methods;
- parameter and return annotations available through Python introspection.

Inherited members and field values are omitted. Drawpyo does not instantiate
classes or access property values while building the diagram. External base
classes are shown as name-only context nodes.

For multiple inheritance, the first declared base controls tree placement and
every additional direct base receives its own UML inheritance connector.

