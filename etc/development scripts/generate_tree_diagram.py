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
blade_grinders = NodeObject(tree=tree, value="Blade Grinders", parent=grinders)
burr_grinders = NodeObject(tree=tree, value="Burr Grinders", parent=grinders)
blunt_objects = NodeObject(tree=tree, value="Blunt Objects", parent=grinders)

# Other
elec_blade = NodeObject(
    tree=tree, value="Electric Blade Grinder", parent=blade_grinders
)
mnp = NodeObject(tree=tree, value="Mortar and Pestle", parent=blunt_objects)

# Conical Burrs
conical = NodeObject(tree=tree, value="Conical Burrs", parent=burr_grinders)
elec_conical = NodeObject(tree=tree, value="Electric", parent=conical)
manual_conical = NodeObject(tree=tree, value="Manual", parent=conical)

HarioSkerton = NodeObject(tree=tree, value="Hario Skerton", parent=manual_conical)
Comandante = NodeObject(tree=tree, value="Comandante", parent=manual_conical)
JZpresso = NodeObject(tree=tree, value="ZJpresso JX-Pro", parent=manual_conical)
weberHG2 = NodeObject(tree=tree, value="Weber HG-2", parent=manual_conical)

BaratzaEnc = NodeObject(tree=tree, value="Baratza Encore", parent=elec_conical)
Niche = NodeObject(tree=tree, value="Niche Zero", parent=elec_conical)
WeberKey = NodeObject(tree=tree, value="Weber Key", parent=elec_conical)

# Flat Burrs
flat = NodeObject(tree=tree, value="Flat Burrs", parent=burr_grinders)

DF64 = NodeObject(tree=tree, value="Turin DF64", parent=flat)
FellowOde = NodeObject(tree=tree, value="Fellow Ode", parent=flat)
LagomP64 = NodeObject(tree=tree, value="Lagom P64", parent=flat)

grp = tree.auto_layout()
tree.write()
