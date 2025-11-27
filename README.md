![CI](https://github.com/MerrimanInd/drawpyo/actions/workflows/ci.yml/badge.svg) ![GitHub License](https://img.shields.io/github/license/MerrimanInd/drawpyo) ![PyPI Version](https://img.shields.io/pypi/v/drawpyo) ![PyPI Downloads](https://img.shields.io/pypi/dm/drawpyo)

<p align="center">
  <img src="assets/logo.png" alt="drawpyo logo" width="140"/>
</p>

# drawpyo

drawpyo is a Python library for programmatically generating Diagrams.net / Draw.io charts. It enables you to create diagram files, place and style objects, and export fully compatible `.drawio` documents that can be opened in the Draw.io (Diagrams.net) desktop or web applications.

---

## Table of Contents

- [History / Justification](#history--justification)
- [Full Documentation](#full-documentation)
- [Basic Usage](#basic-usage)
  - [Make a new file](#make-a-new-file)
  - [Add an object](#add-an-object)
  - [Create an object from a Draw.io library](#create-an-object-from-the-base-style-libraries-available-in-the-drawio-ui)
  - [Style an object using a style string](#style-an-object-from-a-string)
  - [Write the file](#write-the-file)
- [Usage with a Diagram Type](#usage-with-a-diagram-type)
- [Working with TreeDiagrams](#working-with-treediagrams)
  - [Create a new TreeDiagram](#create-a-new-tree-diagram)
  - [Create NodeObjects](#create-some-nodeobjects)
  - [Auto layout and write](#auto-layout-and-write)
  - [Configuration Summary](#configuration-summary)
  - [Limitations](#limitations)
- [License](#license)


---

## History / Justification

Draw.io is a free, lightweight alternative to heavier commercial tools such as Visio and Miro. Because files are stored in plaintext XML, they can be versioned alongside source code and treated as first-class documentation assets. The XML-based file format is also relatively portable and can be transformed or migrated if needed.

drawpyo was created to fill a gap: there was no Python library focused on generating and manipulating Draw.io diagrams programmatically, especially for hierarchical requirement and tree structures. The initial version was built to support automated generation of hierarchical diagrams and has been extended over time with additional functionality, robustness, and documentation.

---

## Full Documentation

The complete documentation, including API reference and additional examples, is available at:

https://merrimanind.github.io/drawpyo/

---

## Basic Usage

The basic mode of interacting with drawpyo is similar to working directly in the Draw.io UI: you create objects, position them on a page, apply styles, and then write the resulting diagram to a `.drawio` file.

You can either manage all placement and styling manually or build higher-level abstractions on top of drawpyo to automate those responsibilities.

### Make a new file

```python
import drawpyo

file = drawpyo.File()
file.file_path = r"C:\drawpyo"
file.file_name = "Test Generated Edges.drawio"

# Add a page
page = drawpyo.Page(file=file)
```

### Add an object

```python
item = drawpyo.diagram.Object(page=page, value="new object")
item.position = (0, 0)
```

### Create an object from the base style libraries available in the Draw.io UI

```python
item_from_lib = drawpyo.diagram.object_from_library(
    page=page,
    library="general",
    obj_name="process",
    value="New Process",
)
```

### Style an object from a string

```python
item_from_stylestr = drawpyo.diagram.Object(page=page)
item_from_stylestr.apply_style_string(
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#6a00ff;"
    "fontColor=#ffffff;strokeColor=#000000;gradientColor=#FF33FF;"
    "strokeWidth=4;"
)
```

### Write the file

```python
file.write()
```

This will produce a `.drawio` file at the configured `file_path` with the specified `file_name`.

---

## Usage with a Diagram Type

In addition to direct, low-level manipulation of Draw.io objects, drawpyo provides higher-level **diagram types** that encapsulate common patterns and auto-layout behavior.

These are intended for scenarios where you want to generate a diagram from structured data without manually positioning each element.

Concepts under active or planned development include:

- Automatic class/object/inheritance diagrams for Python modules
- Flowcharts
- Process diagrams

The currently released diagram type is the **tree diagram**, described below.

---

## Working with TreeDiagrams

Tree diagrams are a core feature that extend what Draw.io provides out of the box. A `TreeDiagram` manages hierarchical node relationships and handles layout automatically.

A typical workflow is:

1. Create a `TreeDiagram` instance.
2. Create `NodeObject` instances and connect them via `tree_parent`.
3. Call `auto_layout()` on the tree.
4. Call `write()` to generate the `.drawio` file.

### Create a new tree diagram

```python
from os import path
from drawpyo.diagram_types import TreeDiagram, NodeObject

tree = TreeDiagram(
    file_path=path.join(path.expanduser("~"), "Test Drawpyo Charts"),
    file_name="Coffee Grinders.drawio",
    direction="down",
    link_style="orthogonal",
)
```

The `direction` property controls which way the leaf nodes grow from the root: `"up"`, `"down"`, `"left"`, or `"right"`.  
The `link_style` can be `"orthogonal"`, `"straight"`, or `"curved"`.

### Create some NodeObjects

```python
# Top object
grinders = NodeObject(
    tree=tree,
    value="Appliances for Grinding Coffee",
    base_style="rounded rectangle",
)

# Main categories
blade_grinders = NodeObject(tree=tree, value="Blade Grinders", tree_parent=grinders)
burr_grinders = NodeObject(tree=tree, value="Burr Grinders", tree_parent=grinders)
blunt_objects = NodeObject(tree=tree, value="Blunt Objects", tree_parent=grinders)
```

Note: `base_style` was manually declared for the first object above. `NodeObject` defaults to `"rounded rectangle"`, so you do not need to pass this for every node unless you want to override the default.

Any `NodeObject` can be a parent, allowing you to construct trees of arbitrary depth:

```python
# Other
elec_blade = NodeObject(
    tree=tree,
    value="Electric Blade Grinder",
    tree_parent=blade_grinders,
)
mnp = NodeObject(
    tree=tree,
    value="Mortar and Pestle",
    tree_parent=blunt_objects,
)

# Conical Burrs
conical = NodeObject(tree=tree, value="Conical Burrs", tree_parent=burr_grinders)
elec_conical = NodeObject(tree=tree, value="Electric", tree_parent=conical)
manual_conical = NodeObject(tree=tree, value="Manual", tree_parent=conical)
```

### Auto layout and write

Before writing the diagram, apply the automatic layout:

```python
tree.auto_layout()
tree.write()
```

`auto_layout()` computes positions for all `NodeObject` instances based on the configured direction and link style. After this, the diagram is written as a `.drawio` file using `write()`.

### Configuration Summary

Key parameters for `TreeDiagram`:

- `file_path`: Target directory for the generated `.drawio` file.
- `file_name`: Name of the generated `.drawio` file.
- `direction`: Growth direction of the tree. One of `"up"`, `"down"`, `"left"`, `"right"`.
- `link_style`: Link rendering style. One of `"orthogonal"`, `"straight"`, `"curved"`.

Key properties for `NodeObject`:

- `tree`: The `TreeDiagram` instance the node belongs to.
- `value`: Displayed label text for the node.
- `tree_parent`: Parent `NodeObject` to create a hierarchy.
- `base_style`: Optional base style for the node shape; defaults to `"rounded rectangle"`.

### Limitations

> Important Note: `TreeDiagram` does not currently support `NodeObject` instances with multiple parents.

Supporting multiple parents significantly complicates the automatic layout process. You may still create explicit links between any two objects in the tree and render them in the diagram, but these additional links may require manual adjustment of the layout within Draw.io for optimal presentation.

---

Refer to the repository and documentation for further details on running the test suite and contributing changes.

---

## License

This project is licensed under the terms specified in the `LICENSE` file in this repository.
