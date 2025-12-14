from typing import Callable, Union, Optional
from copy import deepcopy
from ..diagram.objects import Object, Group
from ..diagram.text_format import TextFormat
from ..utils.standard_colors import StandardColor
from ..utils.color_scheme import ColorScheme
from ..page import Page


class BarChart:
    """A configurable bar chart built entirely from Object and Group.

    This chart is mutable - you can update data, styling, and position after creation.
    """

    # Layout constants
    DEFAULT_BAR_WIDTH = 40
    DEFAULT_BAR_SPACING = 20
    DEFAULT_MAX_BAR_HEIGHT = 200

    # Spacing constants
    TITLE_BOTTOM_MARGIN = 10
    LABEL_TOP_MARGIN = 5
    BACKGROUND_PADDING = 20

    # Axis constants
    AXIS_OFFSET = 10
    TICK_COUNT = 5
    TICK_LENGTH = 4
    TICK_LABEL_MARGIN = 4
    TICK_COLOR = "#000000"

    def __init__(self, data: dict[str, float], **kwargs):
        """
        Args:
            data (dict[str, float]): Mapping of labels to numeric values.

        Keyword Args:
            position (tuple[int, int]): Chart top-left position. Default: (0, 0)
            bar_width (int): Width of each bar. Default: 40
            bar_spacing (int): Space between bars. Default: 20
            max_bar_height (int): Height of the largest bar. Default: 200
            bar_colors (list[Union[str, StandardColor, ColorScheme]]): List of colors. Default: ["#66ccff"]
            base_label_formatter (Callable[[str, float], str]): Custom label formatter for base (below) labels. Default: lambda l,v: l
            inside_label_formatter (Callable[[str, float], str]): Custom label formatter for inside-bar labels. Default: lambda l,v: str(v)
            title (str): Optional chart title. Default: None
            title_text_format (TextFormat): TextFormat for the title. Default: TextFormat()
            base_text_format (TextFormat): TextFormat for base labels. Default: TextFormat()
            inside_text_format (TextFormat): TextFormat for inside labels. Default: TextFormat()
            background_color (str | StandardColor): Optional chart background fill. Default: None
            show_axis (bool): Whether to show the axis and ticks. Default: False
            axis_tick_count (int): Number of tick intervals on the axis. Default: 5
            axis_text_format (TextFormat): TextFormat for axis tick labels. Default: TextFormat()
            glass (bool): Whether bars have a glass effect. Default: False
            rounded (bool): Whether bars have rounded corners. Default: False
        """
        # Validate data
        if not isinstance(data, dict):
            raise TypeError("Data must be a dict.")
        if not data:
            raise ValueError("Data cannot be empty.")

        invalid_keys = [key for key in data if not isinstance(key, str)]
        if invalid_keys:
            raise TypeError(f"All keys must be strings. Invalid: {invalid_keys}")

        invalid_values = [
            key for key, value in data.items() if not isinstance(value, (int, float))
        ]
        if invalid_values:
            raise TypeError(f"Values must be numeric. Invalid: {invalid_values}")

        self._data: dict[str, Union[int, float]] = data.copy()

        # Position and dimensions
        self._position: Optional[tuple[int, int]] = kwargs.get("position", (0, 0))
        self._bar_width: Optional[int] = kwargs.get("bar_width", self.DEFAULT_BAR_WIDTH)
        self._bar_spacing: Optional[int] = kwargs.get(
            "bar_spacing", self.DEFAULT_BAR_SPACING
        )
        self._max_bar_height: Optional[int] = kwargs.get(
            "max_bar_height", self.DEFAULT_MAX_BAR_HEIGHT
        )

        # Text formats
        self._title_text_format: Optional[TextFormat] = deepcopy(
            kwargs.get("title_text_format", TextFormat())
        )
        self._base_text_format: Optional[TextFormat] = deepcopy(
            kwargs.get("base_text_format", TextFormat())
        )
        self._inside_text_format: Optional[TextFormat] = deepcopy(
            kwargs.get("inside_text_format", TextFormat())
        )
        self._axis_text_format: Optional[TextFormat] = deepcopy(
            kwargs.get("axis_text_format", TextFormat())
        )

        # Label formatters
        self._base_label_formatter: Optional[Callable[[str, float], str]] = kwargs.get(
            "base_label_formatter", lambda label, value: label
        )
        self._inside_label_formatter: Optional[Callable[[str, float], str]] = (
            kwargs.get("inside_label_formatter", lambda label, value: str(value))
        )

        # Title
        self._title: Optional[str] = kwargs.get("title")

        # Background color
        self._background_color: Optional[Union[str, StandardColor]] = kwargs.get(
            "background_color"
        )

        # Axis settings
        self._show_axis: Optional[bool] = kwargs.get("show_axis", False)
        self._axis_tick_count: Optional[int] = kwargs.get(
            "axis_tick_count", self.TICK_COUNT
        )

        # Bar appearance
        bar_colors: Optional[list[Union[str, StandardColor, ColorScheme]]] = kwargs.get(
            "bar_colors", ["#66ccff"]
        )
        self._bar_colors: list[Union[str, StandardColor, ColorScheme]] = (
            self._normalize_colors(bar_colors, len(data))
        )
        self._original_bar_colors: Optional[
            list[Union[str, StandardColor, ColorScheme]]
        ] = bar_colors
        self._glass: Optional[bool] = kwargs.get("glass", False)
        self._rounded: Optional[bool] = kwargs.get("rounded", False)

        # Build the chart
        self._group: Group = Group()
        self._build_chart()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def data(self) -> dict[str, float]:
        return self._data.copy()

    @property
    def position(self) -> tuple[int, int]:
        return self._position

    @property
    def group(self) -> Group:
        return self._group

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def update_data(self, data: dict[str, Union[float, int]]) -> None:
        # Validate data
        if not isinstance(data, dict):
            raise TypeError("Data must be a dict.")
        if not data:
            raise ValueError("Data cannot be empty.")

        invalid_keys = [key for key in data if not isinstance(key, str)]
        if invalid_keys:
            raise TypeError(f"All keys must be strings. Invalid: {invalid_keys}")

        invalid_values = [
            key for key, value in data.items() if not isinstance(value, (int, float))
        ]
        if invalid_values:
            raise TypeError(f"Values must be numeric. Invalid: {invalid_values}")

        self._data = data.copy()
        self._bar_colors = self._normalize_colors(self._original_bar_colors, len(data))
        self._rebuild()

    def update_colors(
        self, bar_colors: list[Union[str, StandardColor, ColorScheme]]
    ) -> None:
        self._original_bar_colors = bar_colors
        self._bar_colors = self._normalize_colors(bar_colors, len(self._data))
        self._rebuild()

    def move(self, new_position: tuple[int, int]) -> None:
        if not isinstance(new_position, (tuple, list)) or len(new_position) != 2:
            raise ValueError("new_position must be a tuple of (x, y)")

        dx = new_position[0] - self._position[0]
        dy = new_position[1] - self._position[1]

        for obj in self._group.objects:
            old_x, old_y = obj.position
            obj.position = (old_x + dx, old_y + dy)

        self._position = new_position
        self._group.update_geometry()

    def add_to_page(self, page: Page) -> None:
        for obj in self._group.objects:
            page.add_object(obj)

    # ------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------

    def _normalize_colors(
        self,
        colors: list[Union[str, StandardColor, ColorScheme]],
        count: int,
    ) -> list[Union[str, StandardColor, ColorScheme]]:
        if not colors:
            return ["#66ccff"] * count

        # Cycle through the list until we have the right amount of colors
        result = []
        for i in range(count):
            result.append(colors[i % len(colors)])
        return result

    def _calculate_scale(self) -> float:
        values = list(self._data.values())
        max_value = max(values)
        min_value = min(values)

        if min_value < 0:
            raise ValueError("Negative values are not currently supported")
        if max_value == 0:
            return 1
        return self._max_bar_height / max_value

    def _calculate_chart_dimensions(self) -> tuple[int, int]:
        num_bars = len(self._data)
        width = num_bars * self._bar_width + (num_bars - 1) * self._bar_spacing
        height = self._max_bar_height

        # add space for base labels
        height += (self._base_text_format.fontSize or 12) + self.LABEL_TOP_MARGIN

        # add space for title
        if self._title:
            height += (
                self._title_text_format.fontSize or 16
            ) + self.TITLE_BOTTOM_MARGIN

        return width, height

    def _rebuild(self) -> None:
        self._group.objects.clear()
        self._build_chart()

    def _build_chart(self) -> None:
        x, y = self._position
        scale = self._calculate_scale()

        content_y = y
        if self._title:
            content_y += (
                self._title_text_format.fontSize or 16
            ) + self.TITLE_BOTTOM_MARGIN

        if self._background_color:
            self._add_background()
        if self._title:
            self._add_title()

        # Add ticks and axis if enabled
        if self._show_axis:
            self._add_axis_and_ticks(content_y, scale)

        for i, (key, value) in enumerate(self._data.items()):
            self._add_bar_and_label(i, key, value, content_y, scale)

        self._group.update_geometry()

    def _add_background(self) -> None:
        width, height = self._calculate_chart_dimensions()
        x, y = self._position

        bg = Object(
            value="",
            position=(x - self.BACKGROUND_PADDING, y - self.BACKGROUND_PADDING),
            width=width + 2 * self.BACKGROUND_PADDING,
            height=height + 2 * self.BACKGROUND_PADDING,
            fillColor=self._background_color,
            strokeColor=None,
        )
        self._group.add_object(bg)

    def _add_title(self) -> None:
        x, y = self._position
        chart_width, _ = self._calculate_chart_dimensions()

        title_obj = Object(
            value=self._title,
            position=(x, y),
            width=chart_width,
            height=(self._title_text_format.fontSize or 16) + 4,
            fillColor="none",
            strokeColor="none",
        )
        title_obj.text_format = deepcopy(self._title_text_format)
        title_obj.text_format.align = title_obj.text_format.align or "center"
        title_obj.text_format.verticalAlign = (
            title_obj.text_format.verticalAlign or "top"
        )
        self._group.add_object(title_obj)

    # Draw axis and tick marks
    def _add_axis_and_ticks(self, content_y: int, scale: float) -> None:
        x, _ = self._position

        axis_x = x - self._bar_spacing
        axis_y_top = content_y
        axis_y_bottom = content_y + self._max_bar_height

        axis_line = Object(
            value="",
            position=(axis_x, axis_y_top),
            width=1,
            height=self._max_bar_height,
            fillColor=None,
            strokeColor=self.TICK_COLOR,
        )
        self._group.add_object(axis_line)

        self._add_ticks(axis_x, content_y, scale)

    def _add_ticks(self, axis_x: int, content_y: int, scale: float) -> None:
        if self._axis_tick_count < 1:
            return

        max_value = max(self._data.values())
        font_size = self._axis_text_format.fontSize or 12

        for i in range(self._axis_tick_count + 1):
            t = i / self._axis_tick_count

            tick_value = max_value * (1 - t)
            tick_y = content_y + (self._max_bar_height * t)

            tick = Object(
                value="",
                position=(axis_x - self.TICK_LENGTH, tick_y),
                width=self.TICK_LENGTH,
                height=1,
                fillColor=None,
                strokeColor=self.TICK_COLOR,
            )
            self._group.add_object(tick)

            label_obj = Object(
                value=str(round(tick_value, 2)),
                position=(
                    axis_x - self.TICK_LENGTH - self.TICK_LABEL_MARGIN - 40,
                    tick_y - font_size / 2,
                ),
                width=40,
                height=font_size + 4,
                fillColor="none",
                strokeColor="none",
            )
            label_obj.text_format = deepcopy(self._axis_text_format)
            label_obj.text_format.align = "right"
            self._group.add_object(label_obj)

    def _add_bar_and_label(
        self, index: int, key: str, value: float, content_y: int, scale: float
    ) -> None:
        x, _ = self._position
        bar_height = value * scale
        if isinstance(self._bar_colors[index], ColorScheme):
            color_scheme = self._bar_colors[index]
        elif isinstance(self._bar_colors[index], (StandardColor, str)):
            fill_color = self._bar_colors[index]

        # Calculate geometry
        bar_x = x + index * (self._bar_width + self._bar_spacing)
        bar_y = content_y + (self._max_bar_height - bar_height)
        bar_width = self._bar_width

        # Resolve color
        color_value = self._bar_colors[index]
        color_scheme = color_value if isinstance(color_value, ColorScheme) else None
        fill_color = None if color_scheme else color_value

        # INSIDE LABEL
        inside_label = self._inside_label_formatter(key, value)
        inside_text_format = deepcopy(self._inside_text_format)
        inside_text_format.align = inside_text_format.align or "center"
        inside_text_format.verticalAlign = inside_text_format.verticalAlign or "middle"

        bar = Object(
            value=inside_label,
            position=(bar_x, bar_y),
            width=bar_width,
            height=bar_height,
            color_scheme=color_scheme,
            fillColor=fill_color,
            rounded=self._rounded,
            glass=self._glass,
            text_format=inside_text_format,
        )

        self._group.add_object(bar)

        # BASE LABEL
        base_label = self._base_label_formatter(key, value)
        base_obj = Object(
            value=base_label,
            position=(bar_x, content_y + self._max_bar_height + self.LABEL_TOP_MARGIN),
            width=bar_width,
            height=(self._base_text_format.fontSize or 12) + 10,
            fillColor="none",
            strokeColor="none",
        )
        base_obj.text_format = deepcopy(self._base_text_format)
        base_obj.text_format.align = base_obj.text_format.align or "center"
        self._group.add_object(base_obj)

    def __repr__(self) -> str:
        return f"BarChart(bars={len(self._data)}, position={self._position})"

    def __len__(self) -> int:
        return len(self._data)
