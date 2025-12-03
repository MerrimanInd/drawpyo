import drawpyo
from os import path

file = drawpyo.File()
file.file_path = path.join(path.expanduser("~"), "Test Drawpyo Charts")
file.file_name = "Test Generated Pie.drawio"
page = drawpyo.Page(file=file)

new_slice = drawpyo.diagram.PieSlice(title="Slice", startAngle=0.3, slice_value=0.2, page=page, width=200)

file.write()
