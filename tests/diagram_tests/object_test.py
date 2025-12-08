"""
Tests for the Object class.

Object is the base class for all shapes and objects in Draw.io diagrams.
"""

import pytest
import drawpyo
from drawpyo.utils.color_scheme import ColorScheme
from drawpyo.utils.standard_colors import StandardColor


def parse_style(style: str) -> dict[str, str]:
    """Convert a style string into a dict for order-independent comparison."""
    if not style:
        return {}

    parts = style.split(";")
    parsed = {}

    for part in parts:
        if "=" in part:
            key, value = part.split("=", 1)
            parsed[key] = value

    return parsed


class TestObjectInit:
    """Object initialization tests"""

    def test_default_values(self, empty_page: drawpyo.Page) -> None:
        """Checks default values when creating an object"""
        obj = drawpyo.diagram.Object(page=empty_page)
        assert obj.page == empty_page
        assert obj.value == ""
        assert obj.position == (0, 0)

    def test_with_value(self, empty_page: drawpyo.Page) -> None:
        """Checks if an object with text is created"""
        obj = drawpyo.diagram.Object(page=empty_page, value="Test Object")
        assert obj.value == "Test Object"

    def test_with_position(self, empty_page: drawpyo.Page) -> None:
        """Checks if an object with a position is created"""
        obj = drawpyo.diagram.Object(page=empty_page, position=(100, 200))
        assert obj.position == (100, 200)

    def test_with_dimensions(self, empty_page: drawpyo.Page) -> None:
        """Checks if an object with dimensions is created"""
        obj = drawpyo.diagram.Object(
            page=empty_page,
            width=150,
            height=100,
        )
        assert obj.width == 150
        assert obj.height == 100

    def test_added_to_page_objects(self, empty_page: drawpyo.Page) -> None:
        """Checks that the object is added to the page's list of objects"""
        initial_count = len(empty_page.objects)
        obj = drawpyo.diagram.Object(page=empty_page)
        assert len(empty_page.objects) == initial_count + 1
        assert obj in empty_page.objects


class TestObjectStyleString:
    """Tests for applying styles through a line"""

    def test_apply_style_string(self, empty_page: drawpyo.Page) -> None:
        """Checks whether a style string is applied to an object"""
        test_style_str = (
            "whiteSpace=wrap;rounded=1;fillColor=#6a00ff;strokeColor=#000000;"
            "dashed=0;html=1;fontColor=#ffffff;gradientColor=#FF33FF;strokeWidth=4;"
        )

        expected_style = parse_style(test_style_str)

        obj = drawpyo.diagram.Object(page=empty_page)
        obj.apply_style_string(test_style_str)

        assert parse_style(obj.style) == expected_style

    def test_style_string_overwrites_existing(self, empty_page: drawpyo.Page) -> None:
        """Checks that the style string overwrites existing settings"""
        obj = drawpyo.diagram.Object(page=empty_page)
        obj.fill_color = "#FF0000"

        obj.apply_style_string("fillColor=#00FF00;strokeColor=#000000;")

        style_dict = parse_style(obj.style)
        assert style_dict["fillColor"] == "#00FF00"


class TestObjectTemplate:
    """Tests for creating objects from templates"""

    def test_create_from_template_object(self, empty_page: drawpyo.Page) -> None:
        """Checks whether an object is created from a template"""
        test_style_str = (
            "whiteSpace=wrap;rounded=1;fillColor=#6a00ff;strokeColor=#000000;"
            "dashed=0;html=1;fontColor=#ffffff;gradientColor=#FF33FF;strokeWidth=4;"
        )

        expected_style = parse_style(test_style_str)

        # Create a template object
        template = drawpyo.diagram.Object(page=empty_page)
        template.apply_style_string(test_style_str)

        # Create an object from a template using a constructor
        obj1 = drawpyo.diagram.Object(page=empty_page, template_object=template)
        assert parse_style(obj1.style) == expected_style

        # Create an object from a template through a class method
        obj2 = drawpyo.diagram.Object.create_from_template_object(
            page=empty_page,
            template_object=template,
        )
        assert parse_style(obj2.style) == expected_style

    def test_template_chain(self, empty_page: drawpyo.Page) -> None:
        """Checks the template chain"""
        style_str = "fillColor=#FF0000;strokeColor=#000000;"

        # Creating the initial template
        template1 = drawpyo.diagram.Object(page=empty_page)
        template1.apply_style_string(style_str)

        # Create a second object from the first template
        template2 = drawpyo.diagram.Object(page=empty_page, template_object=template1)

        # Create a third object from the second template
        obj = drawpyo.diagram.Object(page=empty_page, template_object=template2)

        # Check that the main styles have been copied
        obj_style = parse_style(obj.style)
        assert "fillColor" in obj_style
        assert "strokeColor" in obj_style
        assert obj_style["fillColor"] == "#FF0000"
        assert obj_style["strokeColor"] == "#000000"


class TestObjectColors:
    """Tests of working with object colors"""

    def test_fill_color(self, empty_page: drawpyo.Page) -> None:
        """Checks the fill color setting"""
        obj = drawpyo.diagram.Object(page=empty_page, fillColor="#FF6B6B")
        assert obj.fillColor == "#FF6B6B"

    def test_stroke_color(self, empty_page: drawpyo.Page) -> None:
        """Checks the stroke color setting"""
        obj = drawpyo.diagram.Object(page=empty_page, strokeColor="#000000")
        assert obj.strokeColor == "#000000"

    def test_font_color_via_text_format(self, empty_page: drawpyo.Page) -> None:
        """Checks the font color setting via text_format"""
        obj = drawpyo.diagram.Object(page=empty_page)
        obj.text_format.font_color = "#FFFFFF"
        assert obj.text_format.font_color == "#FFFFFF"

    def test_standard_color_enum(self, empty_page: drawpyo.Page) -> None:
        """Checks the use of standard colors"""
        obj = drawpyo.diagram.Object(
            page=empty_page,
            fillColor=StandardColor.RED5,
        )

        assert obj.fillColor is not None

    def test_color_scheme(
        self, empty_page: drawpyo.Page, basic_color_scheme: ColorScheme
    ) -> None:
        """Checks the application of the color scheme"""
        obj = drawpyo.diagram.Object(
            page=empty_page,
            color_scheme=basic_color_scheme,
        )
        assert obj.color_scheme == basic_color_scheme


class TestObjectGeometry:
    """Tests of geometry and positioning of objects"""

    def test_position_update(self, basic_object: drawpyo.diagram.Object) -> None:
        """Checks if the object's position is updated"""
        basic_object.position = (200, 300)
        assert basic_object.position == (200, 300)

    def test_width_update(self, basic_object: drawpyo.diagram.Object) -> None:
        """Checks whether the width of an object is updated"""
        basic_object.width = 200
        assert basic_object.width == 200

    def test_height_update(self, basic_object: drawpyo.diagram.Object) -> None:
        """Checks whether the object's height is updated"""
        basic_object.height = 150
        assert basic_object.height == 150


class TestObjectStrokeStyles:
    """Testing object outline styles"""

    def test_stroke_width(self, empty_page: drawpyo.Page) -> None:
        """Checks the stroke width setting via line_pattern"""
        obj = drawpyo.diagram.Object(page=empty_page)
        assert obj.line_pattern == "solid"

    def test_line_pattern_solid(self, empty_page: drawpyo.Page) -> None:
        """Checks the solid line setting"""
        obj = drawpyo.diagram.Object(page=empty_page, line_pattern="solid")
        assert obj.line_pattern == "solid"

    def test_line_pattern_dashed(self, empty_page: drawpyo.Page) -> None:
        """Checks the installation of the dotted line"""
        obj = drawpyo.diagram.Object(page=empty_page, line_pattern="small_dash")
        assert obj.line_pattern == "small_dash"


class TestObjectSpecialProperties:
    """Tests of special properties of objects"""

    def test_opacity(self, empty_page: drawpyo.Page) -> None:
        """Checks the transparency setting"""
        obj = drawpyo.diagram.Object(page=empty_page, opacity=50)
        assert obj.opacity == 50

    def test_rounded_corners(self, empty_page: drawpyo.Page) -> None:
        """Checks the setting of rounded corners"""
        obj = drawpyo.diagram.Object(page=empty_page, rounded=True)
        assert obj.rounded is True


class TestObjectHierarchy:
    """Parent-child hierarchy tests"""

    def test_parent_child_relationship(self, empty_page: drawpyo.Page) -> None:
        """Checks the parent-child relationship"""
        parent = drawpyo.diagram.Object(page=empty_page, value="Parent")
        child = drawpyo.diagram.Object(
            page=empty_page,
            value="Child",
            parent=parent,
        )

        assert child.parent == parent

    def test_add_child(self, empty_page: drawpyo.Page) -> None:
        """Checks whether a child has been added"""
        parent = drawpyo.diagram.Object(page=empty_page, value="Parent")
        child = drawpyo.diagram.Object(page=empty_page, value="Child")

        # Setting up the parent
        child.parent = parent

        assert child.parent == parent
