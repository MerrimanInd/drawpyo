from typing import Callable
from copy import deepcopy
from ..diagram.objects import Object, Group
from ..diagram.text_format import TextFormat


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

    def __init__(self, data: dict[str, float], **kwargs):
        """
        Args:
            data (dict[str, float]): Mapping of labels to numeric values.

        Keyword Args:
            position (tuple[int, int]): Chart top-left position. Default: (0, 0)
            bar_object (Object): Optional template Object for bar styling. Default: None
            bar_width (int): Width of each bar. Default: 40
            bar_spacing (int): Space between bars. Default: 20
            max_bar_height (int): Height of the largest bar. Default: 200
            bar_colors (str | list[str]): Single color or list of colors. Default: "#66ccff"
            base_label_formatter (Callable[[str, float], str]): Custom label formatter for base (below) labels. Default: lambda l,v: l
            inside_label_formatter (Callable[[str, float], str]): Custom label formatter for inside-bar labels. Default: lambda l,v: str(v)
            title (str): Optional chart title. Default: None
            title_text_format (TextFormat): TextFormat for the title. Default: TextFormat()
            base_text_format (TextFormat): TextFormat for base labels. Default: TextFormat()
            inside_text_format (TextFormat): TextFormat for inside labels. Default: TextFormat()
            bar_fill_color (str): Optional fill color override for all bars. Default: None
            bar_stroke_color (str): Stroke color for bars. Default: "#000000"
            background_color (str): Optional chart background fill. Default: None
        """
        # Validate data
        if not isinstance(data, dict):
            raise TypeError(f"data must be a dict, got {type(data).__name__}")
        if not data:
            raise ValueError("data cannot be empty")

        for label, value in data.items():
            if not isinstance(value, (int, float)):
                raise TypeError(f"Value for '{label}' must be numeric, got {type(value).__name__}")

        self._data = data.copy()

        # Position and dimensions
        self._position = kwargs.get("position", (0, 0))
        self._bar_width = kwargs.get("bar_width", self.DEFAULT_BAR_WIDTH)
        self._bar_spacing = kwargs.get("bar_spacing", self.DEFAULT_BAR_SPACING)
        self._max_bar_height = kwargs.get("max_bar_height", self.DEFAULT_MAX_BAR_HEIGHT)

        # Text formats
        self._title_text_format: TextFormat = deepcopy(kwargs.get("title_text_format", TextFormat()))
        self._base_text_format: TextFormat = deepcopy(kwargs.get("base_text_format", TextFormat()))
        self._inside_text_format: TextFormat = deepcopy(kwargs.get("inside_text_format", TextFormat()))

        # Label formatters
        self._base_label_formatter: Callable[[str, float], str] = kwargs.get(
            "base_label_formatter", lambda label, value: label
        )
        self._inside_label_formatter: Callable[[str, float], str] = kwargs.get(
            "inside_label_formatter", lambda label, value: str(value)
        )

        # Title
        self._title = kwargs.get("title")

        # Colors
        self._bar_fill_color = kwargs.get("bar_fill_color")
        self._bar_stroke_color = kwargs.get("bar_stroke_color", "#000000")
        self._background_color = kwargs.get("background_color")

        # Optional bar object template
        self._bar_object_template: Object | None = kwargs.get("bar_object")

        # Normalize bar colors
        bar_colors = kwargs.get("bar_colors", "#66ccff")
        self._bar_colors = self._normalize_colors(bar_colors, len(data))
        self._original_bar_colors = bar_colors

        # Build the chart
        self._group = Group()
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

    def update_data(self, data: dict[str, float]) -> None:
        if not isinstance(data, dict):
            raise TypeError(f"data must be a dict, got {type(data).__name__}")
        if not data:
            raise ValueError("data cannot be empty")

        for label, value in data.items():
            if not isinstance(value, (int, float)):
                raise TypeError(f"Value for '{label}' must be numeric, got {type(value).__name__}")

        self._data = data.copy()
        self._bar_colors = self._normalize_colors(self._original_bar_colors, len(data))
        self._rebuild()

    def update_colors(self, bar_colors: str | list[str]) -> None:
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

    def add_to_page(self, page) -> None:
        for obj in self._group.objects:
            page.add_object(obj)

    # ------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------

    def _normalize_colors(self, colors: str | list[str], count: int) -> list[str]:
        if isinstance(colors, str):
            return [colors] * count
        if not colors:
            return ["#66ccff"] * count
        if len(colors) < count:
            return colors + [colors[-1]] * (count - len(colors))
        return colors[:count]

    def _calculate_scale(self) -> float:
        values = list(self._data.values())
        max_value = max(values)
        min_value = min(values)

        if min_value < 0:
            raise ValueError("Negative values are not currently supported")
        if max_value == 0:
            return 0
        return self._max_bar_height / max_value

    def _calculate_chart_dimensions(self) -> tuple[int, int]:
        num_bars = len(self._data)
        width = num_bars * self._bar_width + (num_bars - 1) * self._bar_spacing
        height = self._max_bar_height

        # add space for base labels
        height += (self._base_text_format.fontSize or 12) + self.LABEL_TOP_MARGIN

        # add space for title
        if self._title:
            height += (self._title_text_format.fontSize or 16) + self.TITLE_BOTTOM_MARGIN

        return width, height

    def _rebuild(self) -> None:
        self._group.objects.clear()
        self._build_chart()

    def _build_chart(self) -> None:
        x, y = self._position
        scale = self._calculate_scale()

        content_y = y
        if self._title:
            content_y += (self._title_text_format.fontSize or 16) + self.TITLE_BOTTOM_MARGIN

        if self._background_color:
            self._add_background()
        if self._title:
            self._add_title()

        for i, (label, value) in enumerate(self._data.items()):
            self._add_bar_and_label(i, label, value, content_y, scale)

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
        title_obj.text_format.verticalAlign = title_obj.text_format.verticalAlign or "top"
        self._group.add_object(title_obj)

    def _add_bar_and_label(
        self, index: int, label: str, value: float, content_y: int, scale: float
    ) -> None:
        x, _ = self._position
        bar_height = value * scale
        color = self._bar_fill_color or self._bar_colors[index]

        bar_x = x + index * (self._bar_width + self._bar_spacing)
        bar_y = content_y + (self._max_bar_height - bar_height)
        bar_width = self._bar_width

        # Uses the template object if provided, otherwise defaults
        if self._bar_object_template:
            bar = Object.create_from_template_object(
                self._bar_object_template,
                value="",
                position=(bar_x, bar_y),
            )
            bar.width = bar_width
            bar.height = bar_height
            bar.fillColor = color
            bar.strokeColor = self._bar_stroke_color
        else:
            bar = Object(
                value="",
                position=(bar_x, bar_y),
                width=bar_width,
                height=bar_height,
                fillColor=color,
                strokeColor=self._bar_stroke_color,
            )

        self._group.add_object(bar)

        # BASE LABEL
        base_label = self._base_label_formatter(label, value)
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

        # INSIDE LABEL
        inside_label = self._inside_label_formatter(label, value)
        inside_obj = Object(
            value=inside_label,
            position=(bar_x, bar_y),
            width=bar_width,
            height=bar_height,
            fillColor="none",
            strokeColor="none",
        )
        inside_obj.text_format = deepcopy(self._inside_text_format)
        inside_obj.text_format.align = inside_obj.text_format.align or "center"
        inside_obj.text_format.verticalAlign = inside_obj.text_format.verticalAlign or "middle"
        self._group.add_object(inside_obj)

    def __repr__(self) -> str:
        return f"BarChart(bars={len(self._data)}, position={self._position})"

    def __len__(self) -> int:
        return len(self._data)
