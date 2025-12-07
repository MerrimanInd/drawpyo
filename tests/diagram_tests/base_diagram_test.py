"""
Tests for the DiagramBase base class.

DiagramBase is the base class for all diagram objects,
providing common functionality for working with styles and positioning.
"""

import pytest
import drawpyo
from drawpyo.diagram.base_diagram import (
    color_input_check,
    width_input_check,
    style_str_from_dict,
    import_shape_database,
)


class TestDiagramBaseInit:
    """Tests initialization of DiagramBase objects"""

    def test_default_values(self, empty_page: drawpyo.Page) -> None:
        """Checks default values when creating DiagramBase"""
        dbase = drawpyo.diagram.DiagramBase(page=empty_page)

        assert dbase.xml_class == "xml_tag"
        assert dbase.page == empty_page
        assert dbase.style_attributes == ["html"]

    def test_without_page(self) -> None:
        """Checks if DiagramBase is created without a page"""
        dbase = drawpyo.diagram.DiagramBase()
        assert dbase.page is None

    def test_with_xml_parent(self, empty_page: drawpyo.Page) -> None:
        """Checks if a DiagramBase is created with an XML parent"""
        parent = drawpyo.diagram.DiagramBase(page=empty_page)
        child = drawpyo.diagram.DiagramBase(page=empty_page, xml_parent=parent)
        assert child.xml_parent == parent


class TestColorInputCheck:
    """Tests of the color correctness checking function"""

    def test_valid_hex_color(self) -> None:
        """Checks for correct hex color"""
        assert color_input_check("#FF0000") == "#FF0000"
        assert color_input_check("#00FF00") == "#00FF00"
        assert color_input_check("#0000FF") == "#0000FF"

    def test_none_value(self) -> None:
        """Checks if None is handled"""
        assert color_input_check(None) is None

    def test_special_values(self) -> None:
        """Checks for the special values 'none' and 'default'"""
        assert color_input_check("none") == "none"
        assert color_input_check("default") == "default"

    def test_invalid_hex_format(self) -> None:
        """
        Checks for invalid hex color formats
        The function does not validate hex characters, only length and '#'
        """
        assert color_input_check("FF0000") is None
        assert color_input_check("#FF00") is None
        assert color_input_check("#FF00000") is None

    def test_uppercase_and_lowercase(self) -> None:
        """Checks work with upper and lower case"""
        assert color_input_check("#ffffff") == "#ffffff"
        assert color_input_check("#FFFFFF") == "#FFFFFF"
        assert color_input_check("#FfFfFf") == "#FfFfFf"


class TestWidthInputCheck:
    """Tests the width validation function"""

    def test_valid_width(self) -> None:
        """Checks for valid width values"""
        assert width_input_check(1) == 1
        assert width_input_check(50) == 50
        assert width_input_check(999) == 999

    def test_string_width(self) -> None:
        """Checks string width values"""
        assert width_input_check("1") == 1
        assert width_input_check("50") == 50
        assert width_input_check("999") == 999

    def test_none_and_empty(self) -> None:
        """Checks handling of None and empty values"""
        assert width_input_check(None) is None
        assert width_input_check("") is None

    def test_invalid_string(self) -> None:
        """Checks for invalid string values"""
        assert width_input_check("abc") is None
        assert width_input_check("12.5") is None

    def test_boundary_values(self) -> None:
        """Checks boundary values"""
        assert width_input_check(1) == 1
        assert width_input_check(-5) == 1
        assert width_input_check(1000) == 999
        assert width_input_check(5000) == 999

    @pytest.mark.parametrize(
        "value,expected",
        [
            (1, 1),
            (10, 10),
            (100, 100),
            (999, 999),
            (-10, 1),
            (1000, 999),
            (10000, 999),
        ],
    )
    def test_width_range(self, value: int, expected: int) -> None:
        """Parameterized width range test"""
        assert width_input_check(value) == expected


class TestStyleStrFromDict:
    """Tests the function for generating a style string from a dictionary"""

    def test_basic_style_dict(self) -> None:
        """Checks basic dictionary to style string conversion"""
        style_dict = {
            "fillColor": "#FF0000",
            "strokeColor": "#000000",
        }
        result = style_str_from_dict(style_dict)
        assert "fillColor=#FF0000" in result
        assert "strokeColor=#000000" in result

    def test_with_base_style(self) -> None:
        """Checks baseStyle processing"""
        style_dict = {
            "baseStyle": "rounded",
            "fillColor": "#FF0000",
        }
        result = style_str_from_dict(style_dict)
        assert result.startswith("rounded;")
        assert "fillColor=#FF0000" in result

    def test_empty_dict(self) -> None:
        """Checks for an empty dictionary"""
        result = style_str_from_dict({})
        assert result == ""

    def test_ignores_none_values(self) -> None:
        """Checks that None values are ignored"""
        style_dict = {
            "fillColor": "#FF0000",
            "strokeColor": None,
            "fontColor": "",
        }
        result = style_str_from_dict(style_dict)
        assert "fillColor=#FF0000" in result
        assert "strokeColor" not in result
        assert "fontColor" not in result

    def test_complex_style_dict(self) -> None:
        """Checks a complex style dictionary"""
        style_dict = {
            "baseStyle": "rounded",
            "fillColor": "#FF0000",
            "strokeColor": "#000000",
            "strokeWidth": "2",
            "opacity": "80",
        }
        result = style_str_from_dict(style_dict)
        assert result.startswith("rounded;")
        parts = result.split(";")
        assert len(parts) == 5


class TestImportShapeDatabase:
    """Tests the shape database import function"""

    def test_import_general_library(self) -> None:
        """Checks the import of the shared shape library"""
        from os import path

        data = import_shape_database(
            file_name=path.join("shape_libraries", "general.toml"),
            relative=True,
        )
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_import_flowchart_library(self) -> None:
        """Checks the flowchart library import"""
        from os import path

        data = import_shape_database(
            file_name=path.join("shape_libraries", "flowchart.toml"),
            relative=True,
        )
        assert isinstance(data, dict)
        assert len(data) > 0


class TestGeometry:
    """Geometry class tests"""

    def test_geometry_init_default(self) -> None:
        """Checks the default initialization of Geometry"""
        geom = drawpyo.diagram.Geometry()
        assert geom.x == 0
        assert geom.y == 0
        assert geom.width == 120
        assert geom.height == 60

    def test_geometry_init_custom(self) -> None:
        """Checks whether a Geometry is initialized with user-defined values"""
        geom = drawpyo.diagram.Geometry(x=100, y=200, width=150, height=100)
        assert geom.x == 100
        assert geom.y == 200
        assert geom.width == 150
        assert geom.height == 100

    def test_geometry_xml(self) -> None:
        """Validates the Geometry XML output"""
        geom = drawpyo.diagram.Geometry(x=50, y=75, width=200, height=150)
        xml = geom.xml
        assert 'x="50"' in xml
        assert 'y="75"' in xml
        assert 'width="200"' in xml
        assert 'height="150"' in xml


class TestDiagramBaseStyleAttributes:
    """DiagramBase style attribute tests"""

    def test_default_style_attributes(self, empty_page: drawpyo.Page) -> None:
        """Checks default style attributes"""
        dbase = drawpyo.diagram.DiagramBase(page=empty_page)
        assert "html" in dbase.style_attributes

    def test_style_attributes_mutable(self, empty_page: drawpyo.Page) -> None:
        """Checks whether style attributes are mutable"""
        dbase = drawpyo.diagram.DiagramBase(page=empty_page)
        dbase.style_attributes.append("custom")
        assert "custom" in dbase.style_attributes
