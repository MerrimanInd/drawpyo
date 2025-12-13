"""
Tests for the Legend class.

A Legend is a diagram component that displays
label/color mappings with optional titles and backgrounds.
"""

import pytest

from drawpyo.diagram_types.legend import Legend
from drawpyo.diagram.text_format import TextFormat
from drawpyo.utils.standard_colors import StandardColor
from drawpyo.utils.color_scheme import ColorScheme
from drawpyo.page import Page
from drawpyo.diagram.objects import Object, Group


# -------------------------------------------------
# Fixtures
# -------------------------------------------------


@pytest.fixture
def simple_mapping():
    return {
        "Alpha": "#ff0000",
        "Beta": "#00ff00",
    }


@pytest.fixture
def scheme_mapping():
    return {
        "Gamma": ColorScheme(
            fill_color="#111111",
            stroke_color="#222222",
            font_color=StandardColor.WHITE,
        )
    }


@pytest.fixture
def title_format():
    return TextFormat(fontSize=16, bold=True)


@pytest.fixture
def label_format():
    return TextFormat(fontSize=12)


# -------------------------------------------------
# Initialization
# -------------------------------------------------


class TestLegendInit:
    """Legend object initialization tests"""

    def test_requires_non_empty_mapping(self):
        """Legend must be created with a non-empty dict"""
        with pytest.raises(ValueError):
            Legend(mapping={})

        with pytest.raises(ValueError):
            Legend(mapping="invalid")  # type: ignore

    def test_default_values(self, simple_mapping):
        """Checks default Legend values"""
        legend = Legend(mapping=simple_mapping)

        assert isinstance(legend.group, Group)
        assert legend.position == (0, 0)
        assert len(legend.group.objects) == 4  # 2 rows × (box + label)

    def test_repr(self, simple_mapping):
        """Checks __repr__ output"""
        legend = Legend(mapping=simple_mapping, position=(10, 20))
        assert repr(legend) == "Legend(items=2, position=(10, 20))"


# -------------------------------------------------
# Title handling
# -------------------------------------------------


class TestLegendTitle:
    """Legend title tests"""

    def test_title_object_created(self, simple_mapping, title_format):
        """Legend with title adds a title object"""
        legend = Legend(
            mapping=simple_mapping,
            title="My Legend",
            title_text_format=title_format,
        )

        # title + 2 rows × 2 objects
        assert len(legend.group.objects) == 5

        title_obj = legend.group.objects[0]
        assert title_obj.value == "My Legend"
        assert title_obj.text_format.fontSize == 16
        assert title_obj.text_format.bold is True


# -------------------------------------------------
# Background handling
# -------------------------------------------------


class TestLegendBackground:
    """Legend background tests"""

    def test_background_is_added(self, simple_mapping):
        """Background object is added when background_color is set"""
        legend = Legend(
            mapping=simple_mapping,
            background_color=StandardColor.GRAY1,
        )

        bg = legend.group.objects[0]
        assert isinstance(bg, Object)
        assert bg.fillColor == StandardColor.GRAY1
        assert bg.strokeColor is None


# -------------------------------------------------
# Color handling
# -------------------------------------------------


class TestLegendColors:
    """Legend color rendering tests"""

    def test_standard_color_box(self, simple_mapping):
        """Standard color fills color box"""
        legend = Legend(mapping=simple_mapping)

        color_box = legend.group.objects[0]
        assert color_box.fillColor == "#ff0000"
        assert color_box.color_scheme is None

    def test_color_scheme_box(self, scheme_mapping):
        """ColorScheme is assigned correctly"""
        legend = Legend(mapping=scheme_mapping)

        color_box = legend.group.objects[0]

        assert isinstance(color_box.color_scheme, ColorScheme)

    def test_rounded_and_glass_flags(self, simple_mapping):
        """Rounded and glass flags propagate to color boxes"""
        legend = Legend(mapping=simple_mapping, rounded=True, glass=True)

        color_box = legend.group.objects[0]
        assert color_box.rounded is True
        assert color_box.glass is True


# -------------------------------------------------
# Mapping updates
# -------------------------------------------------


class TestLegendUpdateMapping:
    """Legend mapping update tests"""

    def test_update_mapping_rebuilds(self, simple_mapping):
        """Updating mapping rebuilds legend objects"""
        legend = Legend(mapping=simple_mapping)

        legend.update_mapping({"New": "#000000"})

        assert len(legend.group.objects) == 2
        assert legend.group.objects[0].value == ""


# -------------------------------------------------
# Movement
# -------------------------------------------------


class TestLegendMove:
    """Legend movement tests"""

    def test_move_updates_positions(self, simple_mapping):
        """Moving legend shifts all objects"""
        legend = Legend(mapping=simple_mapping, position=(10, 10))
        original_positions = [obj.position for obj in legend.group.objects]

        legend.move((30, 40))

        for (ox, oy), obj in zip(original_positions, legend.group.objects):
            nx, ny = obj.position
            assert nx == ox + 20
            assert ny == oy + 30

        assert legend.position == (30, 40)
