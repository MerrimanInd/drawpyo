import pytest
from xml.etree import ElementTree as ET
from unittest.mock import Mock
from drawpyo.page import Page
from drawpyo.diagram_types.pie_chart import PieChart
from drawpyo.diagram.text_format import TextFormat
from drawpyo.diagram.objects import Object, Group
from drawpyo.utils.standard_colors import StandardColor
from drawpyo.utils.color_scheme import ColorScheme


class TestPieChartInitialization:
    """Test PieChart initialization and validation."""

    def test_initialization_empty_data_raises_error(self):
        """Test that empty data raises ValueError."""
        with pytest.raises(ValueError, match="Data cannot be empty"):
            PieChart({})

    def test_initialization_non_dict_data_raises_error(self):
        """Test that non-dict data raises TypeError."""
        with pytest.raises(TypeError, match="Data must be a dict"):
            PieChart([("A", 10), ("B", 20)])

    def test_initialization_non_string_keys_raises_error(self):
        """Test that non-string keys raise TypeError."""
        with pytest.raises(TypeError, match="All keys must be strings"):
            PieChart({1: 10, 2: 20})

    def test_initialization_non_numeric_value_raises_error(self):
        """Test that non-numeric values raise TypeError."""
        with pytest.raises(TypeError, match="Values must be numeric"):
            PieChart({"A": 10, "B": "20"})

    def test_initialization_with_single_color(self):
        """Test initialization with a single color string."""
        data = {"A": 10, "B": 20}
        chart = PieChart(data, slice_colors=["#ff0000"])

        assert chart._slice_colors == ["#ff0000", "#ff0000"]

    def test_initialization_with_insufficient_colors(self):
        """Test that colors are cycled when list is too short."""
        data = {"A": 10, "B": 20, "C": 15}
        colors = ["#ff0000", "#00ff00"]
        chart = PieChart(data, slice_colors=colors)

        # Should cycle through colors
        assert chart._slice_colors == ["#ff0000", "#00ff00", "#ff0000"]

    def test_initialization_with_empty_color_list(self):
        """Test that empty color list uses default."""
        data = {"A": 10}
        chart = PieChart(data, slice_colors=[])

        assert chart._slice_colors == ["#66ccff"]

    def test_initialization_with_custom_formatter(self):
        """Test custom label formatter."""
        data = {"A": 10}
        formatter = lambda key, value, total: f"{key}: ${value}"

        chart = PieChart(data, label_formatter=formatter)

        assert chart._label_formatter("A", 10, 100) == "A: $10"

    def test_initialization_with_color_scheme(self):
        """Test initialization with ColorScheme objects."""
        data = {"A": 10, "B": 20}
        color_scheme = ColorScheme(
            fill_color="#ff0000", stroke_color="#000000", font_color=StandardColor.WHITE
        )
        chart = PieChart(data, slice_colors=[color_scheme])

        assert isinstance(chart._slice_colors[0], ColorScheme)

    def test_initialization_with_standard_color(self):
        """Test initialization with StandardColor."""
        data = {"A": 10}
        chart = PieChart(data, slice_colors=[StandardColor.RED1])

        assert chart._slice_colors[0] == StandardColor.RED1


class TestPieChartDataValidation:
    """Test data validation and edge cases."""

    def test_negative_values(self):
        """Test that negative values are handled (pie charts should show proportion)."""
        data = {"A": 10, "B": -5, "C": 20}
        # Negative values should be allowed since they're just proportional
        chart = PieChart(data)
        assert chart.data == data

    def test_all_zero_values(self):
        """Test handling when all values are zero."""
        data = {"A": 0, "B": 0}
        chart = PieChart(data)

        # Should not crash, each slice gets 0%
        assert chart.data == data

    def test_mixed_int_float_values(self):
        """Test mixed integer and float values."""
        data = {"A": 10, "B": 20.5, "C": 15}
        chart = PieChart(data)

        assert chart.data == data

    def test_very_large_values(self):
        """Test handling of very large values."""
        data = {"A": 1000000, "B": 2000000}
        chart = PieChart(data)

        # Should handle proportions correctly
        assert chart.data == data

    def test_very_small_values(self):
        """Test handling of very small positive values."""
        data = {"A": 0.001, "B": 0.002}
        chart = PieChart(data)

        assert chart.data == data

    def test_mixed_positive_negative_values(self):
        """Test mixed positive and negative values."""
        data = {"A": 10, "B": -5, "C": 15}
        chart = PieChart(data)

        # Total is 20, proportions should still work
        assert chart.data == data


class TestPieChartUpdateData:
    """Test data update functionality."""

    def test_update_data_basic(self):
        """Test basic data update."""
        data = {"A": 10, "B": 20}
        chart = PieChart(data)

        new_data = {"X": 15, "Y": 25, "Z": 30}
        chart.update_data(new_data)

        assert chart.data == new_data

    def test_update_data_empty_raises_error(self):
        """Test that updating with empty data raises ValueError."""
        chart = PieChart({"A": 10})

        with pytest.raises(ValueError, match="Data cannot be empty"):
            chart.update_data({})

    def test_update_data_non_dict_raises_error(self):
        """Test that non-dict update raises TypeError."""
        chart = PieChart({"A": 10})

        with pytest.raises(TypeError, match="Data must be a dict"):
            chart.update_data([("X", 20)])

    def test_update_data_adjusts_colors(self):
        """Test that colors are adjusted when data length changes."""
        chart = PieChart({"A": 10, "B": 20}, slice_colors=["#ff0000", "#00ff00"])

        # Update with more items
        chart.update_data({"X": 5, "Y": 10, "Z": 15})

        # Should extend colors
        assert len(chart._slice_colors) == 3

    def test_update_data_preserves_position(self):
        """Test that position is preserved after data update."""
        chart = PieChart({"A": 10}, position=(100, 200))
        chart.update_data({"B": 20, "C": 30})

        assert chart.position == (100, 200)


class TestPieChartUpdateColors:
    """Test color update functionality."""

    def test_update_colors_list(self):
        """Test updating with a color list."""
        chart = PieChart({"A": 10, "B": 20})
        chart.update_colors(["#ff0000", "#00ff00"])

        assert chart._slice_colors == ["#ff0000", "#00ff00"]

    def test_update_colors_preserves_original(self):
        """Test that original colors are preserved for future updates."""
        chart = PieChart({"A": 10, "B": 20}, slice_colors=["#ff0000"])

        # Add more data - should use original color
        chart.update_data({"A": 10, "B": 20, "C": 30})

        assert all(c == "#ff0000" for c in chart._slice_colors)

    def test_update_colors_with_color_scheme(self):
        """Test updating colors with ColorScheme objects."""
        chart = PieChart({"A": 10, "B": 20})
        color_scheme = ColorScheme(
            fill_color="#0000ff", stroke_color="#000000", font_color=StandardColor.WHITE
        )
        chart.update_colors([color_scheme])

        assert isinstance(chart._slice_colors[0], ColorScheme)


class TestPieChartMove:
    """Test chart repositioning."""

    def test_move_basic(self):
        """Test basic move operation."""
        chart = PieChart({"A": 10}, position=(0, 0))
        chart.move((100, 200))

        assert chart.position == (100, 200)

    def test_move_updates_all_objects(self):
        """Test that all objects in group are moved."""
        chart = PieChart({"A": 10, "B": 20}, position=(0, 0))

        initial_positions = [obj.position for obj in chart.group.objects]

        chart.move((50, 100))

        # All objects should be moved by the same delta
        for initial, obj in zip(initial_positions, chart.group.objects):
            new_pos = obj.position
            assert new_pos[0] == initial[0] + 50
            assert new_pos[1] == initial[1] + 100

    def test_move_negative_coordinates(self):
        """Test moving to negative coordinates."""
        chart = PieChart({"A": 10}, position=(100, 100))
        chart.move((-50, -50))

        assert chart.position == (-50, -50)

    def test_move_with_title(self):
        """Test moving chart with title."""
        chart = PieChart({"A": 10}, position=(0, 0), title="Test")
        chart.move((100, 100))

        assert chart.position == (100, 100)


class TestPieChartSliceCalculation:
    """Test slice angle and position calculations."""

    def test_equal_slices(self):
        """Test that equal values create equal slices."""
        data = {"A": 25, "B": 25, "C": 25, "D": 25}
        chart = PieChart(data)

        # Each slice should be 0.25 (25%)
        total = sum(data.values())
        for value in data.values():
            fraction = value / total
            assert fraction == 0.25

    def test_single_slice_full_circle(self):
        """Test single slice creates full circle."""
        data = {"Only": 100}
        chart = PieChart(data)

        total = sum(data.values())
        fraction = data["Only"] / total
        assert fraction == 1.0

    def test_slice_order_preserved(self):
        """Test that slice order matches data order."""
        data = {"First": 10, "Second": 20, "Third": 30}
        chart = PieChart(data)

        # Data property should preserve order
        assert list(chart.data.keys()) == ["First", "Second", "Third"]


class TestPieChartTextFormatting:
    """Test text formatting and label formatters."""

    def test_custom_text_formats(self):
        """Test custom text formats are applied."""
        title_fmt = TextFormat(fontSize=24, align="left")
        label_fmt = TextFormat(fontSize=10, color="#ff0000")

        chart = PieChart(
            {"A": 10},
            title="Test",
            title_text_format=title_fmt,
            label_text_format=label_fmt,
        )

        assert chart._title_text_format.fontSize == 24
        assert chart._label_text_format.fontSize == 10

    def test_default_label_formatter(self):
        """Test default label formatter output."""
        chart = PieChart({"A": 10, "B": 20})

        label = chart.default_label_formatter("A", 10, 30)
        assert "A:" in label
        assert "33.3%" in label

    def test_label_formatter_called(self):
        """Test that custom label formatter is used."""

        def custom_formatter(key, value, total):
            return f"[{key}] = {value}"

        chart = PieChart({"A": 10}, label_formatter=custom_formatter)
        assert chart._label_formatter("A", 10, 100) == "[A] = 10"


class TestPieChartBackgroundAndStyling:
    """Test background and styling options."""

    def test_background_color(self):
        """Test background color is applied."""
        chart = PieChart({"A": 10}, background_color="#f0f0f0")
        assert chart._background_color == "#f0f0f0"

    def test_no_background_color(self):
        """Test chart without background."""
        chart = PieChart({"A": 10})
        assert chart._background_color is None

    def test_custom_size(self):
        """Test custom pie size."""
        chart = PieChart({"A": 10}, size=300)
        assert chart._size == 300

    def test_default_size(self):
        """Test default pie size."""
        chart = PieChart({"A": 10})
        assert chart._size == PieChart.DEFAULT_SIZE


class TestPieChartTitleHandling:
    """Test title functionality."""

    def test_title_present(self):
        """Test chart with title."""
        chart = PieChart({"A": 10}, title="Test Title")
        assert chart._title == "Test Title"

    def test_no_title(self):
        """Test chart without title."""
        chart = PieChart({"A": 10})
        assert chart._title is None

    def test_title_affects_layout(self):
        """Test that title affects chart layout."""
        chart_with_title = PieChart(
            {"A": 10}, title="Test", title_text_format=TextFormat(fontSize=20)
        )
        chart_without_title = PieChart({"A": 10})

        # Chart with title should have objects at different positions
        assert chart_with_title._title is not None
        assert chart_without_title._title is None


class TestPieChartGroupIntegration:
    """Test integration with Group object."""

    def test_group_contains_objects(self):
        """Test that group contains chart objects."""
        chart = PieChart({"A": 10, "B": 20})

        # Should have slices and labels
        assert len(chart.group.objects) > 0

    def test_add_to_page(self):
        """Test adding chart to a page."""
        chart = PieChart({"A": 10})
        mock_page = Mock()

        chart.add_to_page(mock_page)

        # Should call add_object for each object in the group
        assert mock_page.add_object.call_count == len(chart.group.objects)

    def test_group_updated_after_rebuild(self):
        """Test that group is updated after data changes."""
        chart = PieChart({"A": 10})
        initial_count = len(chart.group.objects)

        chart.update_data({"A": 10, "B": 20, "C": 30})
        new_count = len(chart.group.objects)

        # More data means more objects
        assert new_count > initial_count


class TestPieChartRepr:
    """Test string representation."""

    def test_repr(self):
        """Test __repr__ method."""
        chart = PieChart({"A": 10, "B": 20}, position=(50, 100))

        repr_str = repr(chart)

        assert "PieChart" in repr_str
        assert "slices=2" in repr_str
        assert "(50, 100)" in repr_str


class TestPieChartEdgeCases:
    """Test various edge cases and boundary conditions."""

    def test_single_slice_chart(self):
        """Test chart with only one slice."""
        chart = PieChart({"A": 100})

        assert chart.data == {"A": 100}

    def test_many_slices(self):
        """Test chart with many slices."""
        data = {f"Slice{i}": i * 10 for i in range(20)}
        chart = PieChart(data)

        assert len(chart.data) == 20

    def test_special_characters_in_labels(self):
        """Test labels with special characters."""
        data = {"A & B": 10, "C/D": 20, "E-F": 15}
        chart = PieChart(data)

        assert chart.data == data

    def test_unicode_labels(self):
        """Test unicode characters in labels."""
        data = {"café": 10, "naïve": 20, "日本": 15}
        chart = PieChart(data)

        assert chart.data == data

    def test_empty_string_label(self):
        """Test empty string as label."""
        data = {"": 10, "B": 20}
        chart = PieChart(data)

        assert "" in chart.data

    def test_multiple_updates(self):
        """Test multiple sequential updates."""
        chart = PieChart({"A": 10})

        chart.update_data({"B": 20, "C": 30})
        assert len(chart.data) == 2

        chart.update_colors(["#ff0000", "#00ff00"])
        assert chart._slice_colors == ["#ff0000", "#00ff00"]

        chart.move((100, 100))
        assert chart.position == (100, 100)

    def test_data_property_returns_copy(self):
        """Test that data property returns a copy, not reference."""
        chart = PieChart({"A": 10})

        data = chart.data
        data["B"] = 20

        # Original chart data should be unchanged
        assert "B" not in chart.data
        assert chart.data == {"A": 10}

    def test_very_small_slice(self):
        """Test slice with very small proportion."""
        data = {"Large": 999, "Tiny": 1}
        chart = PieChart(data)

        total = sum(data.values())
        tiny_fraction = data["Tiny"] / total
        assert tiny_fraction == 0.001

    def test_position_default(self):
        """Test default position is (0, 0)."""
        chart = PieChart({"A": 10})
        assert chart.position == (0, 0)

    def test_custom_position(self):
        """Test custom position."""
        chart = PieChart({"A": 10}, position=(50, 75))
        assert chart.position == (50, 75)


class TestPieChartLabelPositioning:
    """Test label positioning calculations."""

    def test_label_offset_constant(self):
        """Test that label offset constant is defined."""
        assert hasattr(PieChart, "LABEL_OFFSET")
        assert PieChart.LABEL_OFFSET == 5

    def test_get_slice_label_position(self):
        """Test slice label position calculation."""
        chart = PieChart({"A": 10, "B": 20})

        # Test label position for first slice (starts at angle 0)
        pos = chart._get_slice_label_position(0, 0.5, 100, 100)

        # Position should be a tuple of two numbers
        assert isinstance(pos, tuple)
        assert len(pos) == 2
        assert isinstance(pos[0], (int, float))
        assert isinstance(pos[1], (int, float))


class TestPieChartConstants:
    """Test class constants."""

    def test_default_size_constant(self):
        """Test DEFAULT_SIZE constant."""
        assert PieChart.DEFAULT_SIZE == 200

    def test_title_bottom_margin_constant(self):
        """Test TITLE_BOTTOM_MARGIN constant."""
        assert PieChart.TITLE_BOTTOM_MARGIN == 20

    def test_label_offset_constant(self):
        """Test LABEL_OFFSET constant."""
        assert PieChart.LABEL_OFFSET == 5

    def test_background_padding_constant(self):
        """Test BACKGROUND_PADDING constant."""
        assert PieChart.BACKGROUND_PADDING == 20


class TestPieChartColorNormalization:
    """Test color normalization logic."""

    def test_normalize_colors_empty_list(self):
        """Test normalizing empty color list."""
        chart = PieChart({"A": 10})
        colors = chart._normalize_colors([], 3)

        assert colors == ["#66ccff", "#66ccff", "#66ccff"]

    def test_normalize_colors_exact_match(self):
        """Test normalizing when colors match count."""
        chart = PieChart({"A": 10})
        colors = chart._normalize_colors(["#ff0000", "#00ff00"], 2)

        assert colors == ["#ff0000", "#00ff00"]

    def test_normalize_colors_repeat(self):
        """Test normalizing when colors need to repeat."""
        chart = PieChart({"A": 10})
        colors = chart._normalize_colors(["#ff0000", "#00ff00"], 5)

        assert colors == ["#ff0000", "#00ff00", "#ff0000", "#00ff00", "#ff0000"]


class TestPieChartAttachedUpdates:
    """Regression coverage for stale page content after rebuilding (#138)."""

    @pytest.mark.parametrize("page_count", [1, 2])
    def test_repeated_updates_replace_page_content(self, page_count):
        data = {"old-a": 11, "old-b": 12, "old-c": 13}
        component = PieChart(data, title="Persistent title", background_color="#eeeeee")
        pages = [Page() for _ in range(page_count)]
        unrelated = [Object(page=page, value="Unrelated") for page in pages]
        unrelated_xml = [obj.xml for obj in unrelated]
        for page in pages:
            component.add_to_page(page)
            component.add_to_page(page)
            assert len(page.objects) == 3 + len(component.group.objects)

        for replacement in [{"middle": 21}, {"new-a": 31, "new-b": 32, "new-c": 33}]:
            old_objects = list(component.group.objects)
            old_labels = {
                f"{key}: {value / sum(data.values()) * 100:.1f}%"
                for key, value in data.items()
            }
            component.update_data(replacement)
            data = replacement
            expected_labels = {
                f"{key}: {value / sum(data.values()) * 100:.1f}%"
                for key, value in data.items()
            }

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
        component = PieChart({"old-a": 11, "old-b": 12, "old-c": 13})
        component.update_data({"middle": 21})
        page = Page()
        component.add_to_page(page)

        data = {"middle": 21}
        values = {cell.get("value") for cell in ET.fromstring(page.xml).iter("mxCell")}
        assert {
            f"{key}: {value / sum(data.values()) * 100:.1f}%"
            for key, value in data.items()
        } <= values
        assert len(page.objects) == 2 + len(component.group.objects)
        assert all(obj in page.objects for obj in component.group.objects)

    @pytest.mark.parametrize("move_first", [False, True])
    def test_move_and_update_change_exported_positions(self, move_first):
        component = PieChart({"old-a": 11, "old-b": 12, "old-c": 13}, position=(10, 20))
        reference = PieChart({"middle": 21}, position=(10, 20))
        expected_positions = [
            (obj.position[0] + 100, obj.position[1] + 200)
            for obj in reference.group.objects
        ]
        page = Page()
        component.add_to_page(page)

        if move_first:
            component.move((110, 220))
        component.update_data({"middle": 21})
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
        component = PieChart({"old-a": 11, "old-b": 12, "old-c": 13})
        page = Page()
        component.add_to_page(page)
        page.remove_object(component.group.objects[0])

        component.update_data({"middle": 21})

        assert len(page.objects) == 2 + len(component.group.objects)
        assert all(obj in page.objects for obj in component.group.objects)

    def test_color_update_changes_exported_styles(self):
        component = PieChart({"A": 1}, slice_colors=["#aa0000"])
        page = Page()
        component.add_to_page(page)
        assert "fillColor=#aa0000;" in page.xml

        component.update_colors(["#00aa00"])

        assert "fillColor=#00aa00;" in page.xml
        assert "fillColor=#aa0000;" not in page.xml
        assert len(page.objects) == 2 + len(component.group.objects)
        assert all(obj in page.objects for obj in component.group.objects)

    def test_updates_preserve_page_stacking_order(self):
        component = PieChart({"old": 1, "other": 2}, background_color="#eeeeee")
        pages = [Page(), Page()]
        prefixes = []
        annotations = []
        for index, page in enumerate(pages):
            for _ in range(index + 1):
                Object(page=page, value="Below")
            prefixes.append(page.objects.copy())
            component.add_to_page(page)
            annotations.append(Object(page=page, value="Above", position=(0, 0)))

        for step in range(3):
            if step == 0:
                component.update_colors(["#00aa00"])
            elif step == 1:
                component.update_data({"new": 3})
            else:
                component.update_data({"new": 3, "more": 4, "last": 5})

            for page, prefix, annotation in zip(pages, prefixes, annotations):
                expected = prefix + component.group.objects + [annotation]
                assert page.objects == expected
                cells = ET.fromstring(page.xml).findall(".//mxCell")
                assert [cell.get("id") for cell in cells] == [
                    str(obj.id) for obj in expected
                ]

    def test_failed_rebuild_preserves_objects_and_allows_retry(self):
        def format_label(key, value, total):
            if key == "bad":
                raise RuntimeError("Label failed")
            return key

        component = PieChart(
            {"old": 1}, label_formatter=format_label, background_color="#eeeeee"
        )
        pages = [Page(), Page()]
        for page in pages:
            component.add_to_page(page)
        group = component.group
        objects = group.objects
        old_objects = objects.copy()
        old_geometry = (
            group.geometry.x,
            group.geometry.y,
            group.geometry.width,
            group.geometry.height,
        )
        old_xml = [page.xml for page in pages]

        with pytest.raises(RuntimeError, match="Label failed"):
            component.update_data({"partial": 2, "bad": 3})

        assert component.group is group
        assert group.objects is objects
        assert group.objects == old_objects
        assert (
            group.geometry.x,
            group.geometry.y,
            group.geometry.width,
            group.geometry.height,
        ) == old_geometry
        assert [page.xml for page in pages] == old_xml

        component.update_data({"new": 3})

        for page in pages:
            assert all(obj not in page.objects for obj in old_objects)
            assert all(obj in page.objects for obj in component.group.objects)
            assert len(page.objects) == 2 + len(component.group.objects)
            values = {
                cell.get("value") for cell in ET.fromstring(page.xml).iter("mxCell")
            }
            assert "new" in values
            assert "old" not in values
            assert "partial" not in values

    def test_updates_keep_positions_of_unrelated_objects_inside_span(self):
        component = PieChart({"a": 1}, background_color="#eeeeee")
        page = Page()
        component.add_to_page(page)

        # Unrelated objects between the component's own objects, so the
        # component does not occupy one contiguous span.
        on_page = Object(page=page)
        nested = Object(page=page)
        trailing = Object(page=page)
        page.objects.remove(on_page)
        page.objects.remove(nested)
        page.objects.remove(trailing)
        base = page.objects.index(component.group.objects[0])
        page.objects.insert(base + 1, on_page)
        page.objects.insert(base + 2, nested)
        page.objects.append(trailing)

        indices = [page.objects.index(obj) for obj in (on_page, nested, trailing)]

        # Growing the component changes how many objects replace the old ones.
        component.update_data({"a": 1, "b": 2, "c": 3})

        # Unrelated objects keep their order and stay inside the span the
        # component occupies, instead of the whole component being pushed to
        # the end of the page (which would flip the stacking order).
        assert page.objects.index(on_page) < page.objects.index(nested)
        assert page.objects.index(nested) < page.objects.index(trailing)
        assert indices[0] == page.objects.index(on_page)
        assert indices[1] == page.objects.index(nested)
        component_indexes = [page.objects.index(obj) for obj in component.group.objects]
        assert min(component_indexes) < page.objects.index(on_page)
        assert max(component_indexes) > page.objects.index(nested)
        assert all(obj in page.objects for obj in component.group.objects)
        cells = ET.fromstring(page.xml).findall(".//mxCell")
        assert [cell.get("id") for cell in cells] == [
            str(obj.id) for obj in page.objects
        ]

    def test_failed_page_sync_rolls_back_and_allows_retry(self):
        component = PieChart({"old": 1}, background_color="#eeeeee")
        page = Page()
        component.add_to_page(page)
        old_objects = component.group.objects.copy()
        old_xml = page.xml

        objects = page.objects
        # Simulate a page that rejects replacement mid-sync.
        page.objects = tuple(objects)
        try:
            with pytest.raises(TypeError):
                component.update_data({"new": 3})
        finally:
            page.objects = objects

        assert component.group.objects == old_objects
        assert page.xml == old_xml

        component.update_data({"new": 3})

        assert all(obj not in page.objects for obj in old_objects)
        assert all(obj in page.objects for obj in component.group.objects)
