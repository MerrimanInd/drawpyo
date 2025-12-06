from os import path
from drawpyo.diagram_types.binaryTree import BinaryNodeObject, BinaryTreeDiagram

binaryTree = BinaryTreeDiagram(
    file_path=path.join(path.expanduser("~"), "Test Drawpyo Charts"),
    file_name="Family Tree.drawio",
    direction="down",
    link_style="orthogonal",
)

BinaryNodeObject()

# Root (grandparent)
grandparent = BinaryNodeObject(value="John (Grandparent)")

# First generation (children of John)
alice = BinaryNodeObject(value="Alice (child)")
bob = BinaryNodeObject(value="Bob (child)")

# Second generation under Alice
claire = BinaryNodeObject(value="Claire (grandchild)")
dylan = BinaryNodeObject(value="Dylan (grandchild)")

# Second generation under Bob
eve = BinaryNodeObject(value="Eve (grandchild)")
frank = BinaryNodeObject(value="Frank (grandchild)")

# Third generation: adding an extra binary subinaryTreeree under Bob's left child (Eve)
gina = BinaryNodeObject(value="Gina (great-grandchild)")
hank = BinaryNodeObject(value="Hank (great-grandchild)")

aeva = BinaryNodeObject(value="Aeva (great-grandchild)")

# Build the binary tree (Family tree)
binaryTree.add_left(grandparent, alice)
binaryTree.add_right(grandparent, bob)

binaryTree.add_left(alice, claire)
binaryTree.add_right(alice, dylan)

binaryTree.add_left(bob, eve)
binaryTree.add_right(bob, frank)

# Add the extra binary subinaryTreeree under parent's right child's left child (bob -> eve)
binaryTree.add_left(eve, gina)
binaryTree.add_right(eve, hank)

binaryTree.add_right(claire, aeva)

grp = binaryTree.auto_layout()
binaryTree.write()
