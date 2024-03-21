import drawpyo
from os import path

file = drawpyo.File()
file.file_path = path.join(path.expanduser('~'), "Test Drawpyo Charts")
file.file_name = "Create and delete.drawio"

page_1 = drawpyo.Page(file=file)
page_2 = drawpyo.Page(file=file, name="Page-2")
page_3 = drawpyo.Page(file=file)
page_4 = drawpyo.Page(file=file)

file.remove_page(page_1)
file.remove_page('Page-2')
file.remove_page(0)
page_4.remove()