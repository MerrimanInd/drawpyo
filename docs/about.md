# Conventions and Naming

This library contains quite a lot of camel case (capitalizeEachWord) attributes. While the Python convention is snake case (underscores_between_lowercase) the Draw.io style strings and attributes are camel case. Wherever possible, drawpyo uses the terminology and variable names from Draw.io to make it more intuitive to work between the two apps. However, any attribute that does not have an analogy in the Draw.io app is snake case. While this is a bit confusing I hope it helps to clarify when there's a direct analog between drawpyo and Draw.io and when the variable is a drawpyo abstraction. If this is confusing please share that feedback on the GitHub page or email and it may be changed in future versions!

# Basic Diagrams

Drawpyo's basic functionality provides the same features as using the Draw.io app. You can create files with one or more pages, add objects to them, and position those objects. You can style objects from built-in shape libraries, manually, or from style strings. Those objects can be shapes, containers, or edges to connect them. Finally you can save your diagrams where they can be opened with the Draw.io app.

See the full documentation for these functions in [Basic Diagrams - Usage](usage/basic_usage.md).

---

# Extended Functionality

Drawpyo extends the basic functionality of the Draw.io app with custom diagram types. These custom diagrams have automated styling and layouting to make common or complex diagrams easier to generate.

This video demonstrates an exemplary automatic diagram layout process:

[<img src="https://img.youtube.com/vi/HwUqUZZVMgQ/hqdefault.jpg" width="480" height="270"
/>](https://www.youtube.com/embed/HwUqUZZVMgQ)

## TreeDiagram

This diagram makes creating directed tree graphs easy. Define trees, nodes, and then apply an auto layout.

[Documentation](diagram_types/tree_diagrams.md)

## BarChart

Useful visualization to compare the absolute size of different categories.

[Documentation](diagram_types/bar_charts.md)

## PieChart

Useful visualization to compare the relative size of different categories.

[Documentation](diagram_types/pie_charts.md)

## BinaryTreeDiagram

A binary tree diagram visually represents a hierarchical data structure where each node has at most two children, typically called the left and right child.

[Documentation](diagram_types/binary_tree_diagrams.md)

---

# Loading Existing Diagrams

Drawpyo can also **load existing Draw.io diagrams** into Python objects for further inspection, modification, or analysis. This allows you to work with diagrams created in the Draw.io app directly from Python.

Use the `load_diagram` function to read a `.drawio` or `.xml` file:

```python
from drawpyo import load_diagram

diagram = load_diagram("path/to/diagram.drawio")
```

[Documentation](usage/load_diagrams.md)