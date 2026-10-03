import pytest
from xml.etree import ElementTree as ET
from unittest.mock import Mock
from drawpyo.page import Page
from drawpyo.diagram_types.bar_chart import BarChart
from drawpyo.diagram.text_format import TextFormat
from drawpyo.diagram.objects import Object, Group


class TestBarChartInitialization:
    """Test BarChart initialization and validation."""

    def test_initialization_empty_data_raises_error(self):
        """Test that empty data raises ValueError."""
        with pytest.raises(ValueError, match="Data cannot be empty"):
            BarChart({})

    def test_initialization_non_dict_data_raises_error(self):
        """Test that non-dict data raises TypeError."""
        with pytest.raises(TypeError, match="Data must be a dict"):
            BarChart([("A", 10), ("B", 20)])

    def test_initialization_non_numeric_value_raises_error(self):
        """Test that non-numeric values raise TypeError."""
        with pytest.raises(TypeError, match="must be numeric"):
            BarChart({"A": 10, "B": "20"})

    def test_initialization_with_single_color(self):
        """Test initialization with a single color string."""
        data = {"A": 10, "B": 20}
        chart = BarChart(data, bar_colors=["#ff0000"])

        assert chart._bar_colors == ["#ff0000", "#ff0000"]

    def test_initialization_with_insufficient_colors(self):
        """Test that colors are extended when list is too short."""
        data = {"A": 10, "B": 20, "C": 15}
        colors = ["#ff0000", "#00ff00"]
        chart = BarChart(data, bar_colors=colors)

        # Should repeat last color
        assert chart._bar_colors == ["#ff0000", "#00ff00", "#ff0000"]

    def test_initialization_with_empty_color_list(self):
        """Test that empty color list uses default."""
        data = {"A": 10}
        chart = BarChart(data, bar_colors=[])

        assert chart._bar_colors == ["#66ccff"]

    def test_initialization_with_custom_formatters(self):
        """Test custom label formatters."""
        data = {"A": 10}
        base_formatter = lambda l, v: f"{l} Label"
        inside_formatter = lambda l, v: f"${v}"

        chart = BarChart(
            data,
            base_label_formatter=base_formatter,
            inside_label_formatter=inside_formatter,
        )

        assert chart._base_label_formatter("A", 10) == "A Label"
        assert chart._inside_label_formatter("A", 10) == "$10"


class TestBarChartDataValidation:
    """Test data validation and edge cases."""

    def test_negative_values_raise_error(self):
        """Test that negative values raise ValueError during initialization."""
        data = {"A": 10, "B": -5}

        # Negative values should raise error during initialization (when _build_chart calls _calculate_scale)
        with pytest.raises(
            ValueError, match="Negative values are not currently supported"
        ):
            BarChart(data)

    def test_all_zero_values(self):
        """Test handling when all values are zero."""
        data = {"A": 0, "B": 0}
        chart = BarChart(data)

        scale = chart._calculate_scale()
        assert scale == 1  # Should return 1 to avoid division by zero

    def test_mixed_int_float_values(self):
        """Test mixed integer and float values."""
        data = {"A": 10, "B": 20.5, "C": 15}
        chart = BarChart(data)

        assert chart.data == data

    def test_very_large_values(self):
        """Test handling of very large values."""
        data = {"A": 1000000, "B": 2000000}
        chart = BarChart(data)

        scale = chart._calculate_scale()
        assert scale == chart._max_bar_height / 2000000

    def test_very_small_values(self):
        """Test handling of very small positive values."""
        data = {"A": 0.001, "B": 0.002}
        chart = BarChart(data)

        scale = chart._calculate_scale()
        assert scale == chart._max_bar_height / 0.002


class TestBarChartUpdateData:
    """Test data update functionality."""

    def test_update_data_basic(self):
        """Test basic data update."""
        data = {"A": 10, "B": 20}
        chart = BarChart(data)

        new_data = {"X": 15, "Y": 25, "Z": 30}
        chart.update_data(new_data)

        assert chart.data == new_data
        assert len(chart) == 3

    def test_update_data_empty_raises_error(self):
        """Test that updating with empty data raises ValueError."""
        chart = BarChart({"A": 10})

        with pytest.raises(ValueError, match="Data cannot be empty"):
            chart.update_data({})

    def test_update_data_non_dict_raises_error(self):
        """Test that non-dict update raises TypeError."""
        chart = BarChart({"A": 10})

        with pytest.raises(TypeError, match="Data must be a dict"):
            chart.update_data([("X", 20)])

    def test_update_data_non_numeric_raises_error(self):
        """Test that non-numeric values in update raise TypeError."""
        chart = BarChart({"A": 10})

        with pytest.raises(TypeError, match="must be numeric"):
            chart.update_data({"X": "invalid"})

    def test_update_data_adjusts_colors(self):
        """Test that colors are adjusted when data length changes."""
        chart = BarChart({"A": 10, "B": 20}, bar_colors=["#ff0000", "#00ff00"])

        # Update with more items
        chart.update_data({"X": 5, "Y": 10, "Z": 15})

        # Should extend colors
        assert len(chart._bar_colors) == 3


class TestBarChartUpdateColors:
    """Test color update functionality."""

    def test_update_colors_list(self):
        """Test updating with a color list."""
        chart = BarChart({"A": 10, "B": 20})
        chart.update_colors(["#ff0000", "#00ff00"])

        assert chart._bar_colors == ["#ff0000", "#00ff00"]

    def test_update_colors_preserves_original(self):
        """Test that original colors are preserved for future updates."""
        chart = BarChart({"A": 10, "B": 20}, bar_colors=["#ff0000"])

        # Add more data - should use original color
        chart.update_data({"A": 10, "B": 20, "C": 30})

        assert all(c == "#ff0000" for c in chart._bar_colors)


class TestBarChartMove:
    """Test chart repositioning."""

    def test_move_basic(self):
        """Test basic move operation."""
        chart = BarChart({"A": 10}, position=(0, 0))
        chart.move((100, 200))

        assert chart.position == (100, 200)

    def test_move_invalid_position_raises_error(self):
        """Test that invalid position raises ValueError."""
        chart = BarChart({"A": 10})

        with pytest.raises(ValueError, match="must be a tuple of"):
            chart.move((100,))  # Only one coordinate

        with pytest.raises(ValueError, match="must be a tuple of"):
            chart.move(100)  # Not a tuple

    def test_move_updates_all_objects(self):
        """Test that all objects in group are moved."""
        chart = BarChart({"A": 10, "B": 20}, position=(0, 0))

        initial_positions = [obj.position for obj in chart.group.objects]

        chart.move((50, 100))

        # All objects should be moved by the same delta
        for initial, obj in zip(initial_positions, chart.group.objects):
            new_pos = obj.position
            assert new_pos[0] == initial[0] + 50
            assert new_pos[1] == initial[1] + 100

    def test_move_negative_coordinates(self):
        """Test moving to negative coordinates."""
        chart = BarChart({"A": 10}, position=(100, 100))
        chart.move((-50, -50))

        assert chart.position == (-50, -50)


class TestBarChartAxisAndTicks:
    """Test axis and tick functionality."""

    def test_axis_disabled_by_default(self):
        """Test that axis is disabled by default."""
        chart = BarChart({"A": 10})
        assert chart._show_axis is False

    def test_axis_enabled(self):
        """Test enabling axis."""
        chart = BarChart({"A": 10}, show_axis=True)
        assert chart._show_axis is True

    def test_custom_tick_count(self):
        """Test custom tick count."""
        chart = BarChart({"A": 10}, show_axis=True, axis_tick_count=10)
        assert chart._axis_tick_count == 10

    def test_zero_tick_count(self):
        """Test zero tick count (no ticks)."""
        chart = BarChart({"A": 10}, show_axis=True, axis_tick_count=0)
        assert chart._axis_tick_count == 0


class TestBarChartDimensions:
    """Test dimension calculations."""

    def test_calculate_chart_dimensions_basic(self):
        """Test basic dimension calculation."""
        chart = BarChart(
            {"A": 10, "B": 20, "C": 15},
            bar_width=40,
            bar_spacing=20,
            max_bar_height=200,
        )

        width, _height = chart._calculate_chart_dimensions()

        # 3 bars * 40 width + 2 spaces * 20 spacing = 160
        expected_width = 3 * 40 + 2 * 20
        assert width == expected_width

    def test_calculate_chart_dimensions_with_title(self):
        """Test dimension calculation includes title space."""
        chart = BarChart(
            {"A": 10}, title="Test", title_text_format=TextFormat(fontSize=20)
        )

        _width, height = chart._calculate_chart_dimensions()

        # Should include title height + margin
        assert height > chart._max_bar_height

    def test_calculate_chart_dimensions_single_bar(self):
        """Test dimensions with single bar (no spacing)."""
        chart = BarChart({"A": 10}, bar_width=50)

        width, height = chart._calculate_chart_dimensions()

        # Only one bar, no spacing
        assert width == 50


class TestBarChartScaleCalculation:
    """Test scale calculation for bar heights."""

    def test_calculate_scale_basic(self):
        """Test basic scale calculation."""
        chart = BarChart({"A": 50, "B": 100}, max_bar_height=200)

        scale = chart._calculate_scale()

        # max_bar_height / max_value = 200 / 100 = 2
        assert scale == 2.0

    def test_calculate_scale_equal_values(self):
        """Test scale with all equal values."""
        chart = BarChart({"A": 50, "B": 50, "C": 50}, max_bar_height=200)

        scale = chart._calculate_scale()

        # 200 / 50 = 4
        assert scale == 4.0

    def test_calculate_scale_single_value(self):
        """Test scale with single value."""
        chart = BarChart({"A": 25}, max_bar_height=100)

        scale = chart._calculate_scale()

        # 100 / 25 = 4
        assert scale == 4.0


class TestBarChartTextFormatting:
    """Test text formatting and label formatters."""

    def test_custom_text_formats(self):
        """Test custom text formats are applied."""
        title_fmt = TextFormat(fontSize=24, align="left")
        base_fmt = TextFormat(fontSize=10, color="#ff0000")

        chart = BarChart(
            {"A": 10},
            title="Test",
            title_text_format=title_fmt,
            base_text_format=base_fmt,
        )

        assert chart._title_text_format.fontSize == 24
        assert chart._base_text_format.fontSize == 10

    def test_label_formatter_called(self):
        """Test that label formatters are used."""

        def custom_base(label, _value):
            return f"[{label}]"

        def custom_inside(_label, value):
            return f"${value:.2f}"

        assert custom_base("A", 10.5) == "[A]"
        assert custom_inside("A", 10.5) == "$10.50"


class TestBarChartBackgroundAndStyling:
    """Test background and styling options."""

    def test_background_color(self):
        """Test background color is applied."""
        chart = BarChart({"A": 10}, background_color="#f0f0f0")
        assert chart._background_color == "#f0f0f0"


class TestBarChartGroupIntegration:
    """Test integration with Group object."""

    def test_group_contains_objects(self):
        """Test that group contains chart objects."""
        chart = BarChart({"A": 10, "B": 20})

        assert len(chart.group.objects) > 0

    def test_add_to_page(self):
        """Test adding chart to a page."""
        chart = BarChart({"A": 10})
        mock_page = Mock()

        chart.add_to_page(mock_page)

        # Should call add_object for each object in the group
        assert mock_page.add_object.call_count == len(chart.group.objects)


class TestBarChartRepr:
    """Test string representation."""

    def test_repr(self):
        """Test __repr__ method."""
        chart = BarChart({"A": 10, "B": 20}, position=(50, 100))

        repr_str = repr(chart)

        assert "BarChart" in repr_str
        assert "bars=2" in repr_str
        assert "(50, 100)" in repr_str

    def test_len(self):
        """Test __len__ method."""
        chart = BarChart({"A": 10, "B": 20, "C": 15})

        assert len(chart) == 3


class TestBarChartEdgeCases:
    """Test various edge cases and boundary conditions."""

    def test_single_bar_chart(self):
        """Test chart with only one bar."""
        chart = BarChart({"A": 100})

        assert len(chart) == 1
        assert chart.data == {"A": 100}

    def test_many_bars(self):
        """Test chart with many bars."""
        data = {f"Bar{i}": i * 10 for i in range(50)}
        chart = BarChart(data)

        assert len(chart) == 50

    def test_special_characters_in_labels(self):
        """Test labels with special characters."""
        data = {"A & B": 10, "C/D": 20, "E-F": 15}
        chart = BarChart(data)

        assert chart.data == data

    def test_unicode_labels(self):
        """Test unicode characters in labels."""
        data = {"café": 10, "naïve": 20, "日本": 15}
        chart = BarChart(data)

        assert chart.data == data

    def test_empty_string_label(self):
        """Test empty string as label."""
        data = {"": 10, "B": 20}
        chart = BarChart(data)

        assert "" in chart.data

    def test_multiple_updates(self):
        """Test multiple sequential updates."""
        chart = BarChart({"A": 10})

        chart.update_data({"B": 20, "C": 30})
        assert len(chart) == 2

        chart.update_colors(["#ff0000", "#00ff00"])
        assert chart._bar_colors == ["#ff0000", "#00ff00"]

        chart.move((100, 100))
        assert chart.position == (100, 100)

    def test_data_property_returns_copy(self):
        """Test that data property returns a copy, not reference."""
        chart = BarChart({"A": 10})

        data = chart.data
        data["B"] = 20

        # Original chart data should be unchanged
        assert "B" not in chart.data
        assert chart.data == {"A": 10}


class TestBarChartAttachedUpdates:
    """Regression coverage for stale page content after rebuilding (#138)."""

    @pytest.mark.parametrize("page_count", [1, 2])
    def test_repeated_updates_replace_page_content(self, page_count):
        data = {"old-a": 11, "old-b": 12, "old-c": 13}
        component = BarChart(
            data, title="Persistent title", background_color="#eeeeee", show_axis=True
        )
        pages = [Page() for _ in range(page_count)]
        unrelated = [Object(page=page, value="Unrelated") for page in pages]
        unrelated_xml = [obj.xml for obj in unrelated]
        for page in pages:
            component.add_to_page(page)
            component.add_to_page(page)
            assert len(page.objects) == 3 + len(component.group.objects)

        for replacement in [{"middle": 21}, {"new-a": 31, "new-b": 32, "new-c": 33}]:
            old_objects = list(component.group.objects)
            old_labels = set(data) | {str(value) for value in data.values()}
            component.update_data(replacement)
            data = replacement
            expected_labels = set(data) | {str(value) for value in data.values()}

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
        component = BarChart({"old-a": 11, "old-b": 12, "old-c": 13})
        component.update_data({"middle": 21})
        page = Page()
        component.add_to_page(page)

        data = {"middle": 21}
        values = {cell.get("value") for cell in ET.fromstring(page.xml).iter("mxCell")}
        assert set(data) | {str(value) for value in data.values()} <= values
        assert len(page.objects) == 2 + len(component.group.objects)
        assert all(obj in page.objects for obj in component.group.objects)

    @pytest.mark.parametrize("move_first", [False, True])
    def test_move_and_update_change_exported_positions(self, move_first):
        component = BarChart({"old-a": 11, "old-b": 12, "old-c": 13}, position=(10, 20))
        reference = BarChart({"middle": 21}, position=(10, 20))
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
        component = BarChart({"old-a": 11, "old-b": 12, "old-c": 13})
        page = Page()
        component.add_to_page(page)
        page.remove_object(component.group.objects[0])

        component.update_data({"middle": 21})

        assert len(page.objects) == 2 + len(component.group.objects)
        assert all(obj in page.objects for obj in component.group.objects)

    def test_color_update_changes_exported_styles(self):
        component = BarChart({"A": 1}, bar_colors=["#aa0000"])
        page = Page()
        component.add_to_page(page)
        assert "fillColor=#aa0000;" in page.xml

        component.update_colors(["#00aa00"])

        assert "fillColor=#00aa00;" in page.xml
        assert "fillColor=#aa0000;" not in page.xml
        assert len(page.objects) == 2 + len(component.group.objects)
        assert all(obj in page.objects for obj in component.group.objects)
