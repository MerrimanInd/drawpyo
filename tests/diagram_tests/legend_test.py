"""
Tests for the Legend class.

A Legend is a diagram component that displays
label/color mappings with optional titles and backgrounds.
"""

import pytest
from xml.etree import ElementTree as ET

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


class TestLegendAttachedUpdates:
    """Regression coverage for stale page content after rebuilding (#138)."""

    @pytest.mark.parametrize("page_count", [1, 2])
    def test_repeated_updates_replace_page_content(self, page_count):
        data = {"old-a": "#aa0000", "old-b": "#bb0000", "old-c": "#cc0000"}
        component = Legend(data, title="Persistent title", background_color="#eeeeee")
        pages = [Page() for _ in range(page_count)]
        unrelated = [Object(page=page, value="Unrelated") for page in pages]
        unrelated_xml = [obj.xml for obj in unrelated]
        for page in pages:
            component.add_to_page(page)
            component.add_to_page(page)
            assert len(page.objects) == 3 + len(component.group.objects)

        for replacement in [
            {"middle": "#00aa00"},
            {"new-a": "#0000aa", "new-b": "#0000bb", "new-c": "#0000cc"},
        ]:
            old_objects = list(component.group.objects)
            old_labels = set(data)
            component.update_mapping(replacement)
            data = replacement
            expected_labels = set(data)

            for page, other, original_xml in zip(pages, unrelated, unrelated_xml):
                cells = ET.fromstring(page.xml).findall(".//mxCell")
                values = {cell.get("value") for cell in cells}
                assert expected_labels <= values
                assert old_labels.isdisjoint(values)
                assert values >= {"Persistent title", "Unrelated"}
                assert all(obj not in page.objects for obj in old_objects)
                assert all(obj in page.objects for obj in component.group.objects)
                assert len(page.objects) == 3 + len(component.group.objects)
                assert other in page.objects
                assert other.xml == original_xml
                ids = [cell.get("id") for cell in cells]
                assert len(ids) == len(set(ids))
                assert set(ids) == {str(obj.id) for obj in page.objects}
                assert {str(obj.id) for obj in old_objects}.isdisjoint(ids)

                component.add_to_page(page)
                assert len(page.objects) == 3 + len(component.group.objects)

    def test_update_before_attachment(self):
        component = Legend({"old-a": "#aa0000", "old-b": "#bb0000", "old-c": "#cc0000"})
        component.update_mapping({"middle": "#00aa00"})
        page = Page()
        component.add_to_page(page)

        data = {"middle": "#00aa00"}
        values = {cell.get("value") for cell in ET.fromstring(page.xml).iter("mxCell")}
        assert set(data) <= values
        assert len(page.objects) == 2 + len(component.group.objects)
        assert all(obj in page.objects for obj in component.group.objects)

    @pytest.mark.parametrize("move_first", [False, True])
    def test_move_and_update_change_exported_positions(self, move_first):
        component = Legend(
            {"old-a": "#aa0000", "old-b": "#bb0000", "old-c": "#cc0000"},
            position=(10, 20),
        )
        reference = Legend({"middle": "#00aa00"}, position=(10, 20))
        expected_positions = [
            (obj.position[0] + 100, obj.position[1] + 200)
            for obj in reference.group.objects
        ]
        page = Page()
        component.add_to_page(page)

        if move_first:
            component.move((110, 220))
        component.update_mapping({"middle": "#00aa00"})
        if not move_first:
            component.move((110, 220))

        cells = {
            cell.get("id"): cell for cell in ET.fromstring(page.xml).iter("mxCell")
        }
        for obj, position in zip(component.group.objects, expected_positions):
            assert obj in page.objects
            assert obj.position == pytest.approx(position)
            geometry = cells[str(obj.id)].find("mxGeometry")
            assert (
                float(geometry.get("x")),
                float(geometry.get("y")),
            ) == pytest.approx(position)

    def test_update_after_page_object_removed(self):
        component = Legend({"old-a": "#aa0000", "old-b": "#bb0000", "old-c": "#cc0000"})
        page = Page()
        component.add_to_page(page)
        page.remove_object(component.group.objects[0])

        component.update_mapping({"middle": "#00aa00"})

        assert len(page.objects) == 2 + len(component.group.objects)
        assert all(obj in page.objects for obj in component.group.objects)

    def test_color_update_changes_exported_styles(self):
        component = Legend({"A": "#aa0000"})
        page = Page()
        component.add_to_page(page)
        assert "fillColor=#aa0000;" in page.xml

        component.update_mapping({"A": "#00aa00"})

        assert "fillColor=#00aa00;" in page.xml
        assert "fillColor=#aa0000;" not in page.xml
        assert len(page.objects) == 2 + len(component.group.objects)
        assert all(obj in page.objects for obj in component.group.objects)
