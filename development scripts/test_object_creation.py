import drawpyo

file = drawpyo.File()
file.file_path = r"C:\drawpyo\Test Draw.io Charts"
file.file_name = "Test Generated Diagram.drawio"
page = drawpyo.Page(file=file)

object_types = []

base_styles = [
    None,
    "text",
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
    "internal storage",
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
    "data storage",
    "container",
    "labeled container",
    "labeled horizontal container",
]

items = []
vert_space = 50
vert_pos = 0
for style in base_styles:
    item = drawpyo.diagram.BasicObject(
        page=page, value=style, base_style=style
    )
    vert_pos = vert_pos + vert_space + item.geometry.height
    item.position = (0, vert_pos)
    items.append(item)

file.write()
