![CI](https://github.com/MerrimanInd/drawpyo/actions/workflows/ci.yml/badge.svg) ![GitHub License](https://img.shields.io/github/license/MerrimanInd/drawpyo) ![PyPI Version](https://img.shields.io/pypi/v/drawpyo) ![PyPI Downloads](https://img.shields.io/pypi/dm/drawpyo)

<p align="left">
  <img src="docs/img/logo.png" alt="drawpyo logo"/>
</p>

Drawpyo is a Python library for programmatically generating Diagrams.net/Draw.io charts. It enables creating a diagram object, placing and styling objects, then writing the object to a file.

# History/Justification

I love Draw.io! Compared to expensive and heavy commercial options like Visio and Miro, Draw.io's free and lightweight app allows wider and more universal distribution of diagrams. Because the files are stored in plaintext they can be versioned alongside code in a repository as documentation. The XML-based file format makes these diagrams semi-portable, and could easily be ported to other applications if Draw.io ever failed you. For these reason, I think it's one of the best options for documentation diagrams.

When I had a need to generate heirarchical tree diagrams of requirement structures I was surprised to find there wasn't even a single existing Python library for working with these files. I took the project home and spent a weekend building the initial functionality. I've been adding functionality, robustness, and documentation intermittently since.

# Full Documentation

Available here!

https://merrimanind.github.io/drawpyo/

# Discord Server

https://discord.gg/CSMHupUvRp

# Basic Usage

The basic mode of interacting with drawpyo is to manually create, style, and place objects just like you would using the Draw.io UI. There are a number of ways to style objects and you can write your own functionality for automatically handling style or placement.

## Make a new file

```python
import drawpyo
file = drawpyo.File()
file.file_path = r"C:\drawpyo"
file.file_name = "Test Generated Edges.drawio"
# Add a page
page = drawpyo.Page(file=file)
```

## Add an object

```python
item = drawpyo.diagram.Object(page=page, value="new object")
item.position = (0, 0)
```

## Create an object from the base style libraries available in the Draw.io UI

```python
item_from_lib = drawpyo.diagram.object_from_library(
    page=page,
    library="general",
    obj_name="process",
    value="New Process",
    )
```

## Style an object from a string

```python
item_from_stylestr = drawpyo.diagram.Object(page=page)
item_from_stylestr.apply_style_string("rounded=1;whiteSpace=wrap;html=1;fillColor=#6a00ff;fontColor=#ffffff;strokeColor=#000000;gradientColor=#FF33FF;strokeWidth=4;")
```

## Write the file

```python
file.write()
```

## Usage with Diagram Types

Drawpyo also provides higher-level functionality that goes beyond what the Draw.io app offers. These **diagram types** allow you to generate complete structures automatically, without manually placing every element.

Currently, Drawpyo supports:

* **Tree Diagrams**
* **Binary Tree Diagrams**
* **Bar Charts**
* **Pie Charts**
* **Color Legends**

For more details, refer to the [documentation](https://merrimanind.github.io/drawpyo/).

Work has also begun on additional diagram types, including:

* Automatic class/object/inheritance diagrams from a Python module
* Directed and undirected graphs from adjacency lists
* Flowcharts
* Process diagrams
