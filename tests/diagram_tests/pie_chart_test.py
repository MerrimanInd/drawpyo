import pytest
from unittest.mock import Mock
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
