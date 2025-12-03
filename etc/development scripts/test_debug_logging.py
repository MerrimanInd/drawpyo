import drawpyo
from os import path

drawpyo.logger.setLevel("DEBUG")

file = drawpyo.File()
file.file_path = path.join(path.expanduser("~"), "Test Drawpyo Charts")
file.file_name = "Test List with Debug Logging.drawio"
page = drawpyo.Page(file=file)

new_list = drawpyo.diagram.List(title="List", page=page, width=200, position=(100, 100))

new_list.add_item("item 1")
new_list.add_item("item B")
new_list.add_item("item iii")

new_list.autosize()

# new_list.remove_item("item B")

file.write()
