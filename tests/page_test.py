"""
Tests for the Page class.

A Page represents a single diagram page in a Draw.io file.
Each page contains its own objects, grid settings, and other parameters.
"""

import drawpyo
import pytest


class TestPageInit:
    """Page object initialization tests"""

    def test_default_values(self, empty_page: drawpyo.Page) -> None:
        """Checks default values when creating a page"""
        assert empty_page.id == id(empty_page)
        assert len(empty_page.objects) == 2  # Two basic mxCell objects

    def test_viewport_settings(self, empty_page: drawpyo.Page) -> None:
        """Checks the default viewport settings"""
        assert empty_page.dx == 2037
        assert empty_page.dy == 830

    def test_grid_settings(self, empty_page: drawpyo.Page) -> None:
        """Checks the default grid settings"""
        assert empty_page.grid == 1
        assert empty_page.grid_size == 10

    def test_ui_settings(self, empty_page: drawpyo.Page) -> None:
        """Checks the default interface settings"""
        assert empty_page.guides == 1
        assert empty_page.tooltips == 1
        assert empty_page.connect == 1
        assert empty_page.arrows == 1
        assert empty_page.fold == 1

    def test_page_dimensions(self, empty_page: drawpyo.Page) -> None:
        """Checks the default page dimensions"""
        assert empty_page.scale == 1
        assert empty_page.width == 850
        assert empty_page.height == 1100

    def test_page_size_presets(self) -> None:
        """Checks page dimensions when using a size preset"""
        page = drawpyo.Page(
            size_preset=drawpyo.PageSize.A4LANDSCAPE,
            width=99,
        )

        assert page.scale == 1
        assert page.width == 1169
        assert page.height == 827

    def test_special_features(self, empty_page: drawpyo.Page) -> None:
        """Checks special default functions"""
        assert empty_page.math == 0
        assert empty_page.shadow == 0

    def test_xml_structure_objects(self, empty_page: drawpyo.Page) -> None:
        """Validates XML structural objects"""
        assert empty_page.diagram.xml_class == "diagram"
        assert empty_page.mxGraph.xml_class == "mxGraphModel"
        assert empty_page.root.xml_class == "root"

    def test_with_custom_name(self) -> None:
        """Checks if a page with a custom name is created"""
        page = drawpyo.Page(name="Custom Page")
        assert page.name == "Custom Page"

    def test_with_file_reference(self, empty_file: drawpyo.File) -> None:
        """Checks if a page is created with a file link"""
        page = drawpyo.Page(file=empty_file)
        assert page.file == empty_file
        assert page in empty_file.pages


class TestPageXML:
    """Tests XML generation for the page"""

    def test_xml_open_tag_structure(self, empty_page: drawpyo.Page) -> None:
        """Checks the structure of the opening tag"""
        open_tag_1 = f'<diagram name="Page-1" id="{empty_page.diagram.id}">'
        open_tag_2 = f'    <mxGraphModel dx="{empty_page.dx}" dy="{empty_page.dy}" grid="{empty_page.grid}" gridSize="{empty_page.grid_size}" guides="{empty_page.guides}" toolTips="{empty_page.tooltips}" connect="{empty_page.connect}" arrows="{empty_page.arrows}" fold="{empty_page.fold}" page="1" pageScale="{empty_page.scale}" pageWidth="{empty_page.width}" pageHeight="{empty_page.height}" math="{empty_page.math}" shadow="{empty_page.shadow}">'
        open_tag_3 = f"      <root>"

        assert empty_page.xml_open_tag.split("\n")[0] == open_tag_1
        assert empty_page.xml_open_tag.split("\n")[1] == open_tag_2
        assert empty_page.xml_open_tag.split("\n")[2] == open_tag_3

    def test_xml_close_tag_structure(self, empty_page: drawpyo.Page) -> None:
        """Checks the structure of the closing tag"""
        close_tag_1 = "      </root>"
        close_tag_2 = "    </mxGraphModel>"
        close_tag_3 = "  </diagram>"

        assert empty_page.xml_close_tag.split("\n")[0] == close_tag_1
        assert empty_page.xml_close_tag.split("\n")[1] == close_tag_2
        assert empty_page.xml_close_tag.split("\n")[2] == close_tag_3

    def test_full_xml_output(self, empty_page: drawpyo.Page) -> None:
        """Checks the full XML output of a page"""
        open_tag_1 = f'<diagram name="Page-1" id="{empty_page.diagram.id}">'
        open_tag_2 = f'    <mxGraphModel dx="{empty_page.dx}" dy="{empty_page.dy}" grid="{empty_page.grid}" gridSize="{empty_page.grid_size}" guides="{empty_page.guides}" toolTips="{empty_page.tooltips}" connect="{empty_page.connect}" arrows="{empty_page.arrows}" fold="{empty_page.fold}" page="1" pageScale="{empty_page.scale}" pageWidth="{empty_page.width}" pageHeight="{empty_page.height}" math="{empty_page.math}" shadow="{empty_page.shadow}">'
        open_tag_3 = f"      <root>"

        close_tag_1 = "      </root>"
        close_tag_2 = "    </mxGraphModel>"
        close_tag_3 = "  </diagram>"

        obj_tag_1 = '        <mxCell id="0" />'
        obj_tag_2 = '        <mxCell id="1" parent="0" />'

        expected_xml = "\n".join(
            [
                open_tag_1,
                open_tag_2,
                open_tag_3,
                obj_tag_1,
                obj_tag_2,
                close_tag_1,
                close_tag_2,
                close_tag_3,
            ]
        )

        assert empty_page.xml == expected_xml


class TestPageObjects:
    """Tests for working with objects on the page"""

    def test_initial_objects_count(self, empty_page: drawpyo.Page) -> None:
        """Checks the initial number of objects (two service mxCells)"""
        assert len(empty_page.objects) == 2

    def test_add_object(self, empty_page: drawpyo.Page) -> None:
        """Checks if an object has been added to the page"""
        obj = drawpyo.diagram.Object(page=empty_page, value="Test")
        assert len(empty_page.objects) == 3
        assert obj in empty_page.objects

    def test_add_multiple_objects(self, empty_page: drawpyo.Page) -> None:
        """Checks if multiple objects have been added"""
        obj1 = drawpyo.diagram.Object(page=empty_page, value="Object 1")
        obj2 = drawpyo.diagram.Object(page=empty_page, value="Object 2")
        obj3 = drawpyo.diagram.Object(page=empty_page, value="Object 3")

        assert len(empty_page.objects) == 5  # 2 basic + 3 new
        assert obj1 in empty_page.objects
        assert obj2 in empty_page.objects
        assert obj3 in empty_page.objects


class TestPageCustomization:
    """Page parameter customization tests"""

    def test_custom_dimensions(self) -> None:
        """Checks if a page is created with custom dimensions"""
        page = drawpyo.Page(width=1200, height=1600)
        assert page.width == 1200
        assert page.height == 1600

    def test_custom_grid_size(self) -> None:
        """Checks the grid size setting"""
        page = drawpyo.Page(grid_size=20)
        assert page.grid_size == 20

    def test_custom_scale(self) -> None:
        """Checks the scale setting"""
        page = drawpyo.Page(scale=2)
        assert page.scale == 2
