import drawpyo

# Register Azure icons
azure_url = "https://raw.githubusercontent.com/dwarfered/azure-architecture-icons-for-drawio/refs/heads/main/azure-public-service-icons/004%20azure%20ecosystem.xml"
drawpyo.register_mxlibrary("azure", azure_url)

# Get available shapes
from drawpyo.diagram.objects import base_libraries

azure_shapes = base_libraries["azure"]
shape_names = list(azure_shapes.keys())

# Create diagram
file = drawpyo.File()
file.file_name = "azure_architecture.drawio"
file.file_path = "./etc/reference drawio charts"

page = drawpyo.Page(file=file)
page.name = "Azure Architecture Diagram"

# Add a title
title = drawpyo.diagram.Object(
    page=page,
    value="Azure Cloud Services",
    position=(200, 50),
    width=300,
    height=40,
)
title.text_format.size = 20
title.text_format.bold = True
title.text_format.align = "center"
title.fillColor = "#0078D4"
title.fontColor = "#FFFFFF"
title.rounded = True

# Create shapes in a row
icons = []
y_position = 150
spacing = 150

for i, shape_name in enumerate(shape_names[:3]):
    x_position = 100 + (i * spacing)

    icon = drawpyo.diagram.object_from_library(
        library="azure",
        obj_name=shape_name,
        page=page,
        position=(x_position, y_position),
    )

    label = drawpyo.diagram.Object(
        page=page,
        value=shape_name.replace("-", " "),
        position=(x_position - 25, y_position + 80),
        width=100,
        height=30,
    )
    label.text_format.size = 10
    label.text_format.align = "center"
    label.fillColor = "none"
    label.strokeColor = "none"

    icons.append(icon)

# Connect the icons with arrows
if len(icons) > 1:
    for i in range(len(icons) - 1):
        edge = drawpyo.diagram.Edge(page=page, source=icons[i], target=icons[i + 1])
        edge.strokeColor = "#0078D4"
        edge.strokeWidth = 2

# Save
file.write()
print(
    "Azure diagram created successfully! You can now open the file in Draw.io to see the Azure icons!"
)
