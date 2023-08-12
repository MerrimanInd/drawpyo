import drawpyo

tree = drawpyo.diagram_types.TreeDiagram(file_path = r"C:\drawpyo\Test Draw.io Charts",
                                               file_name = "Tree Diagram.drawio",
                                               direction= "down")


# Define a handful of LeafObjects, give them value names

top_level = drawpyo.diagram_types.LeafObject(tree=tree, value="top level item")

mid_level_1 = drawpyo.diagram_types.LeafObject(tree=tree, value="mid level item 1", trunk=top_level)
mid_level_2 = drawpyo.diagram_types.LeafObject(tree=tree, value="mid level item 2", trunk=top_level)

bottom_level_1 = drawpyo.diagram_types.LeafObject(tree=tree, value="bottom level item 1", trunk=mid_level_1)
bottom_level_2 = drawpyo.diagram_types.LeafObject(tree=tree, value="bottom level item 2", trunk=mid_level_1)
bottom_level_3 = drawpyo.diagram_types.LeafObject(tree=tree, value="bottom level item 3", trunk=mid_level_2)
bottom_level_4 = drawpyo.diagram_types.LeafObject(tree=tree, value="bottom level item 4", trunk=mid_level_2)
bottom_level_5 = drawpyo.diagram_types.LeafObject(tree=tree, value="bottom level item 5", trunk=mid_level_2)

basement_level_1 = drawpyo.diagram_types.LeafObject(tree=tree, value="basement level 1", trunk=bottom_level_3)
basement_level_2 = drawpyo.diagram_types.LeafObject(tree=tree, value="basement level 2", trunk=bottom_level_3)


grp = tree.auto_layout()
tree.write()