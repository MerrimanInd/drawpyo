# drawpyo

Drawpyo is a Python library for programmatically generating Diagrams.net/Draw.io charts. It enables creating a diagram object, placing and styling objects, then writing the object to a file.

# History/Justification

I love Draw.io! Compared to expensive and heavy commercial options like Visio and Miro, Draw.io's free and lightweight app allows wider and more universal distribution of diagrams. Because the files are stored in plaintext they can be versioned alongside code in a repository as documentation. The XML-based file format makes these diagrams semi-portable, and could easily be ported to other applications if Draw.io ever failed you. For these reason, I think it's one of the best options for documentation diagrams.

When I had a need to generate heirarchical tree diagrams of requirement structures I was surprised to find there wasn't even a single existing Python library for working with these files. I took the project home and spent a weekend building the initial functionality. I've been adding functionality, robustness, and documentation intermittently since.

# Basic Usage

The basic mode of interacting with drawpyo is to manually create, style, and place objects just like you would using the Draw.io UI. There are a number of ways to style objects and you can write your own functionality for automatically handling style or placement.

## Make a new file

```python
import drawpyo
diagram = drawpyo.File()
file.file_path = r"C:\drawpyo"
file.file_name = "Test Generated Edges.drawio"
# Add a page
page = drawpy.Page(file=file)
```

## Add an object

```python
item = drawpyo.diagram.BasicObject(page=page, value="new object")
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
item_from_stylestr = drawpyo.diagram.BasicObject(page=page)
item_from_stylestr.apply_style_string("rounded=1;whiteSpace=wrap;html=1;fillColor=#6a00ff;fontColor=#ffffff;strokeColor=#000000;gradientColor=#FF33FF;strokeWidth=4;")
```

## Write the file

```python
file.write()
```

# Usage with a diagram type

There is also functionality available in drawpyo that extends what can be done in Draw.io's app! These diagram types allow for easy and automatic creation of specific diagrams.

The only diagram type that's released is the tree diagram. Varying level of conceptual work has been started for:

- Automatic class/object/inheritance diagrams of a python module

- Flowcharts

- Process diagrams

## Working with TreeDiagrams

Create a new tree diagram:

```python
from drawpyo.diagram_types import TreeDiagram, LeafObject

tree = TreeDiagram(
	file_path = path.join(path.expanduser('~'), "Test Drawpyo Charts"),
    file_name = "Coffee Grinders.drawio",
    direction = "down",
    link_style = "orthogonal",
    )
```

The direction property sets which way the leaf nodes grow from the root: up, down, left, or right. The link_style can be orthogonal, straight, or curved.

Create some LeafObjects:

```python
# Top object
grinders = LeafObject(tree=tree, value="Appliances for Grinding Coffee", base_style="rounded rectangle")

# Main categories
blade_grinders = LeafObject(tree=tree, value="Blade Grinders", trunk=grinders)
burr_grinders = LeafObject(tree=tree, value="Burr Grinders", trunk=grinders)
blunt_objects = LeafObject(tree=tree, value="Blunt Objects", trunk=grinders)
```

Note that the base_style was manually declared for the first object. But LeafObjects will default to "rounded rectangle" so it's not necessary for every one. Any LeafObject can be a parent, so you can keep adding objects down the tree:

```python
# Other
elec_blade = LeafObject(tree=tree, value="Electric Blade Grinder", trunk=blade_grinders)
mnp = LeafObject(tree=tree, value="Mortar and Pestle", trunk=blunt_objects)

# Conical Burrs
conical = LeafObject(tree=tree, value="Conical Burrs", trunk=burr_grinders)
elec_conical = LeafObject(tree=tree, value="Electric", trunk=conical)
manual_conical = LeafObject(tree=tree, value="Manual", trunk=conical)
```

> **Important Note:** TreeDiagrams do not currently support LeafObjects with multiple parents! It may not ever as this seriously complicates the auto layout process. However, you can add links between any two objects in the tree and render them in the diagram. They just may look ugly until you manually rearrange the diagram.

Finally, before writing the diagram you'll want to run the magic penultimate step: auto layout.

```python
tree.auto_layout()
tree.write()
```
