import drawpyo
from os import path

file = drawpyo.File()
file.file_path = path.join(path.expanduser("~"), "Test Drawpyo Charts")
file.file_name = "Test Generated List.drawio"
page = drawpyo.Page(file=file)

new_list = drawpyo.diagram.List(title="List of Stuff", page=page, width=200)

new_list.add_item("item 1")
new_list.add_item("item B")
new_list.add_item("item iii")

new_list.autosize()

file.write()
