
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


# Optionally, you can name the levels for clarity
tree.levels = {'top': 0,
                'mid': 1,
                'bottom': 2}

# You can add LeafObjects to the tree and assign them to a level with either a
# defined name or a number. 0 is always the trunk level.

# tree.add_object(top_level, level="top")
tree.add_object(mid_level_1, level="mid")
# tree.add_object(bottom_level_1, level="bottom")

# You can also add items independently if they didn't have a tree attribute
# assigned at instantiation.
tree.add_object(top_level)
# tree.add_object(mid_level)
# tree.add_object(bottom_level)


# Finally, set the layout automatically and write the tree to a file.
tree.auto_layout()
tree.write()