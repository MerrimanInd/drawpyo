from drawpyo.diagram_types import TreeDiagram, LeafObject

tree = TreeDiagram(file_path = r"C:\drawpyo\Test Draw.io Charts",
                   file_name = "Coffee Grinders.drawio",
                   direction = "down",
                   link_style = "orthogonal"
                   )

# Top object
grinders = LeafObject(tree=tree, value="Appliances for Grinding Coffee", base_style="rounded rectangle")

# Main categories
blade_grinders = LeafObject(tree=tree, value="Blade Grinders", trunk=grinders)
burr_grinders = LeafObject(tree=tree, value="Burr Grinders", trunk=grinders)
blunt_objects = LeafObject(tree=tree, value="Blunt Objects", trunk=grinders)

# Other
elec_blade = LeafObject(tree=tree, value="Electric Blade Grinder", trunk=blade_grinders)
mnp = LeafObject(tree=tree, value="Mortar and Pestle", trunk=blunt_objects)

# Conical Burrs
conical = LeafObject(tree=tree, value="Conical Burrs", trunk=burr_grinders)
elec_conical = LeafObject(tree=tree, value="Electric", trunk=conical)
manual_conical = LeafObject(tree=tree, value="Manual", trunk=conical)

HarioSkerton = LeafObject(tree=tree, value="Hario Skerton", trunk=manual_conical)
Comandante = LeafObject(tree=tree, value="Comandante", trunk=manual_conical)
JZpresso = LeafObject(tree=tree, value="ZJpresso JX-Pro", trunk=manual_conical)
weberHG2 = LeafObject(tree=tree, value="Weber HG-2", trunk=manual_conical)

BaratzaEnc = LeafObject(tree=tree, value="Baratza Encore", trunk=elec_conical)
Niche = LeafObject(tree=tree, value="Niche Zero", trunk=elec_conical)
WeberKey = LeafObject(tree=tree, value="Weber Key", trunk=elec_conical)

# Flat Burrs
flat = LeafObject(tree=tree, value="Flat Burrs", trunk=burr_grinders)

DF64 = LeafObject(tree=tree, value="Turin DF64", trunk=flat)
FellowOde = LeafObject(tree=tree, value="Fellow Ode", trunk=flat)
LagomP64 = LeafObject(tree=tree, value="Lagom P64", trunk=flat)

grp = tree.auto_layout()
tree.write()