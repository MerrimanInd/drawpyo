
import drawpyo

chart = drawpyo.diagram_types.TreeDiagram(file_path = r"C:\drawpyo\Test Draw.io Charts",
                                               file_name = "Tree Diagram.drawio")

top_level = drawpyo.diagram_types.LeafObject(value="top level item")
mid_level = drawpyo.diagram_types.LeafObject(value="mid level item", trunk=top_level)
bottom_level = drawpyo.diagram_types.LeafObject(value="bottom level item", trunk=mid_level)

chart.add_object(top_level, level=0)
chart.add_object(mid_level, level=1)
chart.add_object(bottom_level, level=2)

#file.write()
