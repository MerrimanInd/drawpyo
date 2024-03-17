import drawpyo
from os import path

file = drawpyo.File()
file.file_path = path.join(path.expanduser('~'), "Test Drawpyo Charts")
file.file_name = "New Process Generation.drawio"
page = drawpyo.Page(file=file)


base_obj = drawpyo.diagram.BasicObject(page=page,
                                       rounded=1)


file.write()