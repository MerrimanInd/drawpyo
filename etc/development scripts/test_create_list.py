import drawpyo
from os import path

file = drawpyo.File()
file.file_path = path.join(path.expanduser("~"), "Test Drawpyo Charts")
file.file_name = "Test Generated List.drawio"
page = drawpyo.Page(file=file)

new_list = drawpyo.diagram.object_from_library(
    library="general", obj_name="list", page=page
)
new_list.value = "New List"


list_objects = ["Item 1", "Item 2", "Item 3"]
item_num = 1
for obj in list_objects:
    list_obj = drawpyo.diagram.object_from_library(
        library="general", obj_name="list_item", page=page
    )
    list_obj.value = obj
    list_obj.geometry.y = item_num * list_obj.height
    list_obj.xml_parent = new_list
    item_num += 1

file.write()
