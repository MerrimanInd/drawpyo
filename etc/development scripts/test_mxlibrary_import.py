import drawpyo

# Create a diagram
file = drawpyo.File()
file.file_name = "mxlibrary_demo.drawio"
file.file_path = "./tests/output"

page = drawpyo.Page(file=file)
page.name = "Shape Library Demo"

# Create some standard shapes to demonstrate the library is working
shape1 = drawpyo.diagram.object_from_library(
    library="general",
    obj_name="rectangle",
    page=page,
    position=(50, 50),
    value="Standard Shape",
)

shape2 = drawpyo.diagram.object_from_library(
    library="flowchart",
    obj_name="process",
    page=page,
    position=(250, 50),
    value="Flowchart Shape",
)

# Connect them
edge = drawpyo.diagram.Edge(page=page, source=shape1, target=shape2)

# Save the diagram
file.write()

# To use external mxlibrary files:
# 1. Register a library: drawpyo.register_mxlibrary('name', 'url_or_path')
# 2. Use shapes: drawpyo.diagram.object_from_library(library='name', obj_name='shape')
