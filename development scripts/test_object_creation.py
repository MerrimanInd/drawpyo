import drawpyo

file = drawpyo.File()
file.file_path = r"C:\drawpyo\Test Draw.io Charts"
file.file_name = "Test Generated Objects.drawio"
page = drawpyo.Page(file=file)

object_types = []

base_styles = [
    # "text",
    "ellipse",
    "square",
    "circle",
    "process",
    "diamond",
    "parallelogram",
    "hexagon",
    "triangle",
    "cylinder",
    "cloud",
    "document",
    "internal_storage",
    "cube",
    "step",
    "trapezoid",
    "tape",
    "note",
    "card",
    "callout",
    "actor",
    "or",
    "and",
    "data_storage",
    "container",
    "labeled_container",
    "labeled_horizontal_container",
]

items = []
vert_space = 50
vert_pos = 0
for style in base_styles:
    # item = drawpyo.diagram.BasicObject(
    #     page=page, value=style, base_style=style
    # )
    item = drawpyo.diagram.object_from_library(library="general", obj_name=style, page=page)
    item.value = style
    vert_pos = vert_pos + vert_space + item.geometry.height
    item.position = (0, vert_pos)
    items.append(item)

file.write()