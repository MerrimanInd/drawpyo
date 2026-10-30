# Loading Existing Draw.io Diagrams with Drawpyo

Drawpyo provides an **API to load existing Draw.io diagrams** into Python objects, allowing inspection, modification, and analysis programmatically.

---

## Overview

The main function for loading diagrams is:

```python
from drawpyo import load_diagram
```

`load_diagram(file_path: str) -> ParsedDiagram` reads a `.drawio` or `.xml` file and returns a **`ParsedDiagram`** object.

This object represents all shapes, containers, and edges in a structured, accessible form.

### Key Features

* **Full hierarchy support:** Parent-child relationships are preserved. Nested objects inside containers maintain their relative positions.
* **Geometry preservation:** All positions (`x`, `y`) and dimensions (`width`, `height`) are maintained exactly as in Draw.io. Relative offsets for child objects are automatically applied.
* **Edges supported:** Connections between objects are imported as `Edge` objects, including source, target, and any intermediate points.
* **ID mapping:** Every object can be accessed by its original Draw.io cell ID.
* **Error handling:** Malformed XML or invalid Draw.io files raise clear exceptions.

---

## ParsedDiagram Structure

A `ParsedDiagram` has:

| Attribute       | Description                                                     |
| --------------- | --------------------------------------------------------------- |
| `shapes`        | List of `Object` instances (vertices, containers)               |
| `edges`         | List of `Edge` instances (connections between objects)          |
| `_id_map`       | Internal mapping of Draw.io cell IDs to objects for fast access |
| `get_by_id(id)` | Retrieve a shape or edge by its original Draw.io ID             |
| `element_count` | Total number of shapes + edges in the diagram                   |
| `add_to(page, ...)` | Attach imported shapes and edges to a `Page` (see below)    |

---

## Adding a Parsed Diagram to a Page

After loading a diagram, attach its elements to a page with `ParsedDiagram.add_to()`. This sets each element's page, registers it for export, optionally shifts top-level geometry by an offset, and rewrites Draw.io page links on `UserObject` elements.

```python
from drawpyo import File, Page, load_diagram

diagram = load_diagram("source.drawio")
output = File()
page = Page(file=output, name=diagram.name or "Imported")

diagram.add_to(page)  # optional: offset=(dx, dy), include_shapes=..., include_edges=...
output.write()
```

| Parameter        | Default | Description |
| ---------------- | ------- | ----------- |
| `page`           | —       | Target `Page` to receive shapes and edges |
| `offset`         | `(0, 0)` | Added to top-level object positions and edge waypoint coordinates |
| `include_shapes` | `True`  | When `False`, shapes are left unattached |
| `include_edges`  | `True`  | When `False`, edges are left unattached |

For multipage files, load each page with `load_diagrams()` and call `add_to()` once per `ParsedDiagram`.

---

## Basic Usage

```python
from drawpyo import load_diagram

# Load diagram
diagram = load_diagram("example.drawio")

# Print total counts
print(f"Shapes: {len(diagram.shapes)}")
print(f"Edges: {len(diagram.edges)}")
print(f"Total elements: {diagram.element_count}")

# Access a specific shape
shape_id = "2292288764992"
shape = diagram.get_by_id(shape_id)
print(f"Shape value: {shape.value}")
print(f"Geometry: x={shape.geometry.x}, y={shape.geometry.y}, width={shape.geometry.width}, height={shape.geometry.height}")
```

---

## Working with Nested Objects

Draw.io allows containers, swimlanes, and groups. Drawpyo preserves the hierarchy and applies **absolute positioning** recursively:

```python
# Access a parent container
parent_container = diagram.get_by_id("2292288764992")

# List all child objects
for child in parent_container.objects:
    print(f"- {child.value} at ({child.geometry.x}, {child.geometry.y})")
```

This ensures that when a container is moved, its children maintain their relative positions.
