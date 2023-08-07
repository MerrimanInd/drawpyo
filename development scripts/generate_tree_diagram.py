
import drawpyo

tree = drawpyo.diagram_types.TreeDiagram(file_path = r"C:\drawpyo\Test Draw.io Charts",
                                               file_name = "Tree Diagram.drawio")

top_level = drawpyo.diagram_types.LeafObject(tree=tree, value="top level item")

mid_level_1 = drawpyo.diagram_types.LeafObject(tree=tree, value="mid level item 1", trunk=top_level)
mid_level_2 = drawpyo.diagram_types.LeafObject(tree=tree, value="mid level item 2", trunk=top_level)


bottom_level_1 = drawpyo.diagram_types.LeafObject(tree=tree, value="bottom level item 1", trunk=mid_level_1)
bottom_level_2 = drawpyo.diagram_types.LeafObject(tree=tree, value="bottom level item 2", trunk=mid_level_1)
bottom_level_3 = drawpyo.diagram_types.LeafObject(tree=tree, value="bottom level item 3", trunk=mid_level_2)
bottom_level_4 = drawpyo.diagram_types.LeafObject(tree=tree, value="bottom level item 4", trunk=mid_level_2)


# tree.levels = {'top': 0,
#                 'mid': 1,
#                 'bottom': 2}
# tree.add_object(top_level, level="top")
# tree.add_object(mid_level_1, level="mid")
# tree.add_object(bottom_level_1, level="bottom")

# tree.add_object(top_level)
# tree.add_object(mid_level)
# tree.add_object(bottom_level)

#tree.sort_into_levels()
#tree.group_all_levels()
tree.auto_layout()

tree.write()