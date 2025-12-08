from os import path
from drawpyo.diagram_types.binary_tree import BinaryNodeObject, BinaryTreeDiagram

binaryTree = BinaryTreeDiagram(
    file_path=path.join(path.expanduser("~"), "Test Drawpyo Charts"),
    file_name="Coffee Types.drawio",
    direction="down",
    link_style="orthogonal",
)

# Root - Coffee
coffee = BinaryNodeObject(value="Coffee")

# First level - Hot and Cold
hot_coffee = BinaryNodeObject(value="Hot Coffee")
cold_coffee = BinaryNodeObject(value="Cold Coffee")

# Second level under Hot Coffee
espresso = BinaryNodeObject(value="Espresso")
cappuccino = BinaryNodeObject(value="Cappuccino")

# Second level under Cold Coffee
iced_latte = BinaryNodeObject(value="Iced Latte")
cold_brew = BinaryNodeObject(value="Cold Brew")

# Third level under Hot Coffee's left child (Espresso)
americano = BinaryNodeObject(value="Americano")
macchiato = BinaryNodeObject(value="Macchiato")

# Build the binary tree (Coffee taxonomy)
binaryTree.add_left(coffee, hot_coffee)
binaryTree.add_right(coffee, cold_coffee)

binaryTree.add_left(hot_coffee, espresso)
binaryTree.add_right(hot_coffee, cappuccino)

binaryTree.add_left(cold_coffee, iced_latte)
binaryTree.add_right(cold_coffee, cold_brew)

# Add extra binary subtree under hot coffee's left child (espresso)
binaryTree.add_left(espresso, americano)
binaryTree.add_right(espresso, macchiato)

grp = binaryTree.auto_layout()
binaryTree.write()
