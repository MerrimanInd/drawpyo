import drawpyo
from os import path

file = drawpyo.File()
file.file_path = path.join(path.expanduser("~"), "Test Drawpyo Charts")
file.file_name = "Test Generated Containers.drawio"
page = drawpyo.Page(file=file)

new_container = drawpyo.diagram.object_from_library(
    library="general", obj_name="labeled_horizontal_container", page=page
)
new_container.position = (100, 100)
new_container.value = "Test Container"
# new_container.autosize_to_children = False

block_1 = drawpyo.diagram.object_from_library(
    library="general", obj_name="rectangle", page=page
)
block_1.value = "Block 1"
block_1.parent = new_container
block_1.position_rel_to_parent = (-10, -10)

block_2 = drawpyo.diagram.Object(
    position_rel_to_parent=(300, 300), parent=new_container, value="Block 2", page=page
)

new_container.resize_to_children()

file.write()
