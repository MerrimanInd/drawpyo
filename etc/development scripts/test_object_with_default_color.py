import drawpyo
from os import path

file = drawpyo.File()
file.file_path = path.join(path.expanduser("~"), "Test Drawpyo Charts")
file.file_name = "Default Colors Object.drawio"
page = drawpyo.Page(file=file)


base_obj = drawpyo.diagram.Object(page=page, fillColor=drawpyo.DefaultColors.BLUE5)


file.write()
