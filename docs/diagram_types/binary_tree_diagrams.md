# Binary Tree Diagrams

Binary trees are one of the most common hierarchical structures, and this module provides a specialized pair of classes — **BinaryNodeObject** and **BinaryTreeDiagram** — designed to make creating, linking, and laying out binary trees convenient and safe.

BinaryNodeObject enforces the strict "at most two children" rule and exposes intuitive `left` and `right` properties. BinaryTreeDiagram extends TreeDiagram with binary-friendly defaults and helper methods.

---

## Create a Binary Tree

To get started, import the binary tree types and create a `BinaryTreeDiagram`:

```python
from drawpyo.diagram_types import BinaryTreeDiagram

tree = BinaryTreeDiagram(
    file_path="path/to/diagram",
    file_name="Binary Tree.drawio",
)
```

There are a number of configuration parameters available to fine tune the layout of the BinaryTreeDiagram:

| Parameter     | Effect                                    | Default    |
| ------------- | ----------------------------------------- | ---------- |
| level_spacing | Vertical spacing between levels           | 80         |
| item_spacing  | Horizontal spacing between sibling groups | 20         |
| group_spacing | Spacing between unrelated groups          | 30         |
| link_style    | Edge connection style                     | "straight" |
| padding       | Spacing between objects within a group    | 10         |

---

## Add Nodes

Binary trees use **BinaryNodeObject**, a subclass of NodeObject that provides two dedicated child slots: `left` and `right`.

```python
from drawpyo.diagram_types import BinaryNodeObject

root = BinaryNodeObject(tree=tree, value="Root")
left = BinaryNodeObject(tree=tree, value="Left Branch")
right = BinaryNodeObject(tree=tree, value="Right Branch")
```

### Using the `left` and `right` setters

Every BinaryNodeObject has:

* exactly **two child slots**, always present
* direct accessors: `node.left` and `node.right`

Assign children:

```python
root.left = left
root.right = right
```

Changing a child's side automatically fixes its parent relationship:

```python
root.left = right     # reassigns and detaches from old parent
```

Setting a side to `None` removes the child:

```python
root.right = None
```

---

## Using BinaryTreeDiagram convenience methods

BinaryTreeDiagram provides small helpers to ensure consistency and type safety:

```python
tree.add_left(root, left)
tree.add_right(root, right)
```

Both methods:

* ensure parent and child are BinaryNodeObjects
* automatically register both under the same `BinaryTreeDiagram`

---

## Rules and Guarantees

BinaryNodeObject enforces strict binary-tree behavior.

### Child Slot Normalization

Nodes always maintain exactly two slots:

```
[left, right]
```

If you supply fewer than two children on creation:

```python
node = BinaryNodeObject(tree_children=[child])
```

…it becomes:

```
[child, None]
```

If you supply more than two:

```python
BinaryNodeObject(tree_children=[a, b, c])
```

→ Raises `ValueError`.

### Moving Nodes Between Parents

Assigning a node as a child:

* detaches it from any existing parent
* prevents a node from occupying *both* sides at once
* prevents more than two unique children

### Parent Safety

BinaryTreeDiagram forbids attaching non-binary nodes:

```python
tree.add_left(parent, not_a_binary_node)
```
→ Raises `TypeError`.

---

## Full Example

```python
from drawpyo.diagram_types import BinaryTreeDiagram, BinaryNodeObject

# Create the diagram
tree = BinaryTreeDiagram(
    file_path="~/Binary Trees",
    file_name="SimpleBinary.drawio"
)

# Root
root = BinaryNodeObject(tree=tree, value="Root Node")

# Children
a = BinaryNodeObject(tree=tree, value="Left Child")
b = BinaryNodeObject(tree=tree, value="Right Child")

# Attach via setters
root.left = a
root.right = b

# Further branching
a.left  = BinaryNodeObject(tree=tree, value="A1")
a.right = BinaryNodeObject(tree=tree, value="A2")
b.left  = BinaryNodeObject(tree=tree, value="B1")

tree.auto_layout()

tree = BinaryTreeDiagram.from_dict(
    data,
    file_path= "~/Test Drawpyo Charts",
    file_name="Minimal Binary Tree.drawio",
    direction="down",
    colors=["#DDDDDD","#BBBBBB"],
    coloring="directional",
)

tree.write()
```