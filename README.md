![CI](https://github.com/MerrimanInd/drawpyo/actions/workflows/ci.yml/badge.svg) ![GitHub License](https://img.shields.io/github/license/MerrimanInd/drawpyo) ![PyPI Version](https://img.shields.io/pypi/v/drawpyo) ![PyPI Downloads](https://img.shields.io/pypi/dm/drawpyo)

<p align="left">
  <img src="docs/img/logo.png" alt="drawpyo logo"/>
</p>

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

## Usage with Diagram Types

Drawpyo also provides higher-level functionality that goes beyond what the Draw.io app offers. These **diagram types** allow you to generate complete structures automatically, without manually placing every element.

Currently, Drawpyo supports:

* **Tree Diagrams**
* **Bar Charts**

For more details, refer to the [documentation](https://merrimanind.github.io/drawpyo/).

Work has also begun on additional diagram types, including:

* Automatic class/object/inheritance diagrams from a Python module
* Flowcharts
* Process diagrams
