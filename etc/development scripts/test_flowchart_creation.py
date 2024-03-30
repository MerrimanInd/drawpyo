import drawpyo
from os import path

file = drawpyo.File()
file.file_path = path.join(path.expanduser("~"), "Test Drawpyo Charts")
file.file_name = "Test Generated Flowchart Objects.drawio"
page = drawpyo.Page(file=file)

object_types = []

base_styles = [
    "annotation_1",
    "annotation_2",
    "card",
    "collate",
    "data",
    "database",
    "decision",
    "delay",
    "direct_data",
    "display",
    "document",
    "extract",
    "measurement",
    "internal_storage",
    "loop_limit",
    "manual_input",
    "manual_operation",
    "merge",
    "storage",
    "multi_document",
    "off_page_ref",
    "on_page_ref",
    "or",
    "tape",
    "parallel_mode",
    "predefined_process",
    "preparation",
    "process",
    "sequential_data",
    "sort",
    "start_1",
    "start_2",
    "stored_data",
    "summing_junction",
    "terminator",
    "transfer"
]

items = []
vert_space = 50
vert_pos = 0
for style in base_styles:
    item = drawpyo.diagram.object_from_library(
        library="flowchart", obj_name=style, page=page
    )
    item.value = style
    vert_pos = vert_pos + vert_space + item.geometry.height
    item.position = (0, vert_pos)
    items.append(item)

file.write()
