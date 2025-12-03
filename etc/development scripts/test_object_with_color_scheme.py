import drawpyo
from os import path

file = drawpyo.File()
file.file_path = path.join(path.expanduser("~"), "Test Drawpyo Charts")
file.file_name = "Color Scheme Object.drawio"
page = drawpyo.Page(file=file)

color_scheme = drawpyo.ColorScheme(
    fill_color=drawpyo.StandardColor.BLUE5,
    stroke_color="#AA6600",
    font_color="#AA6600",
)
color_scheme_obj = drawpyo.diagram.Object(
    value="Color Scheme", page=page, color_scheme=color_scheme
)
base_obj = drawpyo.diagram.Object(value="No Color Scheme", page=page, position=(0, 100))


file.write()
