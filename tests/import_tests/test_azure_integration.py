import drawpyo
from drawpyo.utils.logger import logger


def test_azure_integration():
    """Test registering Azure library and creating a diagram with Azure icons"""
    azure_url = "https://raw.githubusercontent.com/dwarfered/azure-architecture-icons-for-drawio/refs/heads/main/azure-public-service-icons/004%20azure%20ecosystem.xml"

    logger.info("Registering Azure library...")
    drawpyo.register_mxlibrary("azure", azure_url)

    from drawpyo.diagram.objects import base_libraries

    assert "azure" in base_libraries
    azure_shapes = base_libraries["azure"]
    logger.info(f"Found {len(azure_shapes)} shapes in library")

    file = drawpyo.File()
    file.file_name = "azure_diagram_test.drawio"
    file.file_path = "./etc/reference drawio charts"

    page = drawpyo.Page(file=file)
    page.name = "Azure Test"

    shape_names = list(azure_shapes.keys())[:2]

    obj1 = drawpyo.diagram.object_from_library(
        library="azure",
        obj_name=shape_names[0],
        page=page,
        position=(100, 100),
    )
    logger.info(f"Created: {shape_names[0]}")

    if len(shape_names) > 1:
        obj2 = drawpyo.diagram.object_from_library(
            library="azure",
            obj_name=shape_names[1],
            page=page,
            position=(300, 100),
        )
        logger.info(f"Created: {shape_names[1]}")

        edge = drawpyo.diagram.Edge(page=page, source=obj1, target=obj2)
        edge.label = "connects to"

    file.write()

    import os

    file_path = os.path.join(file.file_path, f"{file.file_name}")
    assert os.path.exists(file_path)

    with open(file_path, "r") as f:
        content = f.read()
        assert "mxGraphModel" in content
        assert "mxCell" in content

    logger.info("Test completed successfully")
