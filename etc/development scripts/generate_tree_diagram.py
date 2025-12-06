from drawpyo.diagram_types import TreeDiagram, NodeObject
from os import path

tree = TreeDiagram(
    file_path=path.join(path.expanduser("~"), "Test Drawpyo Charts"),
    file_name="Coffee Grinders.drawio",
    direction="down",
    link_style="orthogonal",
)

# Top object
grinders = NodeObject(
    tree=tree, value="Appliances for Grinding Coffee", base_style="rounded rectangle"
)

# Main categories
blade_grinders = NodeObject(tree=tree, value="Blade Grinders", tree_parent=grinders)
burr_grinders = NodeObject(tree=tree, value="Burr Grinders", tree_parent=grinders)
blunt_objects = NodeObject(tree=tree, value="Blunt Objects", tree_parent=grinders)

# Other
elec_blade = NodeObject(
    tree=tree, value="Electric Blade Grinder", tree_parent=blade_grinders
)
mnp = NodeObject(tree=tree, value="Mortar and Pestle", tree_parent=blunt_objects)

# Conical Burrs
conical = NodeObject(tree=tree, value="Conical Burrs", tree_parent=burr_grinders)
elec_conical = NodeObject(tree=tree, value="Electric", tree_parent=conical)
manual_conical = NodeObject(tree=tree, value="Manual", tree_parent=conical)

HarioSkerton = NodeObject(tree=tree, value="Hario Skerton", tree_parent=manual_conical)
Comandante = NodeObject(tree=tree, value="Comandante", tree_parent=manual_conical)
JZpresso = NodeObject(tree=tree, value="ZJpresso JX-Pro", tree_parent=manual_conical)
weberHG2 = NodeObject(tree=tree, value="Weber HG-2", tree_parent=manual_conical)

BaratzaEnc = NodeObject(tree=tree, value="Baratza Encore", tree_parent=elec_conical)
Niche = NodeObject(tree=tree, value="Niche Zero", tree_parent=elec_conical)
WeberKey = NodeObject(tree=tree, value="Weber Key", tree_parent=elec_conical)

# Flat Burrs
flat = NodeObject(tree=tree, value="Flat Burrs", tree_parent=burr_grinders)

DF64 = NodeObject(tree=tree, value="Turin DF64", tree_parent=flat)
FellowOde = NodeObject(tree=tree, value="Fellow Ode", tree_parent=flat)
LagomP64 = NodeObject(tree=tree, value="Lagom P64", tree_parent=flat)
