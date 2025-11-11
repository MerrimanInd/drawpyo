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
            label_mode (str): 'none', 'label' or 'inside'. Default: 'label'
            label_formatter (Callable[[str, float], str]): Custom label formatter. Default: "{label}\n{value}"
            title (str): Optional chart title. Default: None
            text_format (TextFormat): Text text_format object applied to labels and title.
            bar_fill_color (str): Fill color override for all bars. Default: None
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
        
        # Unified text_format object
        self._text_format: TextFormat = kwargs.get("text_format", TextFormat())

        # Label mode and formatter
        self._label_mode = kwargs.get("label_mode", "label")
        if self._label_mode not in ("label", "inside", "none"):
            raise ValueError("label_mode must be either 'label', 'inside', or 'none'")
        self._label_formatter = kwargs.get("label_formatter", self._default_label_formatter)

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

    def _default_label_formatter(self, label: str, value: float) -> str:
        return f"{label}\n{value}"

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
        
        if self._label_mode == "label":
            height += (self._text_format.fontSize or 12) + self.LABEL_TOP_MARGIN

        if self._title:
            height += (self._text_format.fontSize or 16) + self.TITLE_BOTTOM_MARGIN
        
        return width, height

    def _rebuild(self) -> None:
        self._group.objects.clear()
        self._build_chart()

    def _build_chart(self) -> None:
        x, y = self._position
        scale = self._calculate_scale()
        
        content_y = y
        if self._title:
            content_y += (self._text_format.fontSize or 16) + self.TITLE_BOTTOM_MARGIN
        
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
            height=(self._text_format.fontSize or 16) + 4,
            fillColor="none",
            strokeColor="none",
        )
        title_obj.text_format = deepcopy(self._text_format)
        title_obj.text_format.align = self._text_format.align or "center"
        title_obj.text_format.verticalAlign = self._text_format.verticalAlign or "top"
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

        # Use the template object if provided, otherwise default
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

        if self._label_mode == "none":
            return

        formatted_label = self._label_formatter(label, value)
        label_obj = Object(value=formatted_label, fillColor="none", strokeColor="none")
        label_obj.text_format = deepcopy(self._text_format)

        if self._label_mode == "inside":
            label_obj.position = (bar_x, bar_y)
            label_obj.width = bar_width
            label_obj.height = bar_height
            label_obj.text_format.align = self._text_format.align or "left"
            label_obj.text_format.verticalAlign = self._text_format.verticalAlign or "middle"

        elif self._label_mode == "label":
            label_obj.position = (
                bar_x,
                content_y + self._max_bar_height + self.LABEL_TOP_MARGIN,
            )
            label_obj.width = self._bar_width
            label_obj.height = (self._text_format.fontSize or 12) + 10
            label_obj.text_format.align = self._text_format.align or "center"

        self._group.add_object(label_obj)

    def __repr__(self) -> str:
        return f"BarChart(bars={len(self._data)}, position={self._position})"

    def __len__(self) -> int:
        return len(self._data)