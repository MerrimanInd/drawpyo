import drawpyo
from os import path

file = drawpyo.File()
file.file_path = path.join(path.expanduser("~"), "Test Drawpyo Charts")
file.file_name = "Text Formatting.drawio"
page = drawpyo.Page(file=file)


text_format = drawpyo.diagram.TextFormat(bold=True, italic=True)

item = drawpyo.diagram.Object(page=page)
item.value = "test text"
item.text_format = text_format

file.write()
