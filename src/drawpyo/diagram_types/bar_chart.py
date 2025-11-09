from typing import Callable, Optional, Union
from ..diagram.objects import Object, Group


class BarChart:
    """A configurable bar chart built entirely from Object and Group.
    
    This chart is mutable - you can update data, styling, and position after creation.
    """

    # Layout constants
    DEFAULT_BAR_WIDTH = 40
    DEFAULT_BAR_SPACING = 20
    DEFAULT_MAX_BAR_HEIGHT = 200
    DEFAULT_LABEL_FONT_SIZE = 12
    DEFAULT_TITLE_FONT_SIZE = 16
    
    # Spacing constants
    TITLE_BOTTOM_MARGIN = 10
    LABEL_TOP_MARGIN = 5
    LABEL_SIDE_MARGIN = 10
    LABEL_WIDTH_HORIZONTAL = 80
    BACKGROUND_PADDING = 20

    def __init__(self, data: dict[str, float], **kwargs):
        """
        Args:
            data (dict[str, float]): Mapping of labels to numeric values.
            
        Keyword Args:
            position (tuple[int, int]): Chart top-left position. Default: (0, 0)
            bar_width (int): Width of each bar. Default: 40
            bar_spacing (int): Space between bars. Default: 20
            max_bar_height (int): Height of the largest bar. Default: 200
            bar_colors (str | list[str]): Single color or list of colors. Default: "#66ccff"
            direction (str): 'up' or 'right'. Default: 'up'
            label_font_size (int): Font size for bar labels. Default: 12
            label_formatter (Callable[[str, float], str]): Custom label formatter. Default: "{label}\n{value}"
            title (str): Optional chart title. Default: None
            title_font_size (int): Font size for the title. Default: 16
            bar_fill_color (str): Fill color override for all bars. Default: None
            bar_stroke_color (str): Stroke color for bars. Default: "#000000"
            background_color (str): Optional chart background fill. Default: None
        """
        # Validate data
        if not isinstance(data, dict):
            raise TypeError(f"data must be a dict, got {type(data).__name__}")
        if not data:
            raise ValueError("data cannot be empty")
        
        # Validate all values are numeric
        for label, value in data.items():
            if not isinstance(value, (int, float)):
                raise TypeError(f"Value for '{label}' must be numeric, got {type(value).__name__}")
        
        self._data = data.copy()  # Store a copy to prevent external mutation
        
        # Position and dimensions
        self._position = kwargs.get("position", (0, 0))
        self._bar_width = kwargs.get("bar_width", self.DEFAULT_BAR_WIDTH)
        self._bar_spacing = kwargs.get("bar_spacing", self.DEFAULT_BAR_SPACING)
        self._max_bar_height = kwargs.get("max_bar_height", self.DEFAULT_MAX_BAR_HEIGHT)
        
        # Direction
        direction = kwargs.get("direction", "up")
        if direction not in ("up", "right"):
            raise ValueError(f"direction must be 'up' or 'right', got '{direction}'")
        self._direction = direction
        
        # Text formatting
        self._label_font_size = kwargs.get("label_font_size", self.DEFAULT_LABEL_FONT_SIZE)
        self._label_formatter = kwargs.get("label_formatter", self._default_label_formatter)
        self._title = kwargs.get("title")
        self._title_font_size = kwargs.get("title_font_size", self.DEFAULT_TITLE_FONT_SIZE)
        
        # Colors
        self._bar_fill_color = kwargs.get("bar_fill_color")
        self._bar_stroke_color = kwargs.get("bar_stroke_color", "#000000")
        self._background_color = kwargs.get("background_color")
        
        # Normalize bar colors
        bar_colors = kwargs.get("bar_colors", "#66ccff")
        self._bar_colors = self._normalize_colors(bar_colors, len(data))
        
        # Build the chart
        self._group = Group()
        self._build_chart()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def data(self) -> dict[str, float]:
        """Get a copy of the current data."""
        return self._data.copy()
    
    @property
    def position(self) -> tuple[int, int]:
        """Get the current position."""
        return self._position
    
    @property
    def group(self) -> Group:
        """Get the underlying Group object."""
        return self._group

    # ------------------------------------------------------------------
    # Public methods
    # ------------------------------------------------------------------

    def update_data(self, data: dict[str, float]) -> None:
        """Update the chart data and rebuild.
        
        Args:
            data: New data mapping labels to values.
        """
        if not isinstance(data, dict):
            raise TypeError(f"data must be a dict, got {type(data).__name__}")
        if not data:
            raise ValueError("data cannot be empty")
        
        for label, value in data.items():
            if not isinstance(value, (int, float)):
                raise TypeError(f"Value for '{label}' must be numeric, got {type(value).__name__}")
        
        self._data = data.copy()
        self._bar_colors = self._normalize_colors(
            self._bar_colors[0] if len(set(self._bar_colors)) == 1 else self._bar_colors,
            len(data)
        )
        self._rebuild()

    def update_colors(self, bar_colors: Union[str, list[str]]) -> None:
        """Update bar colors and rebuild.
        
        Args:
            bar_colors: Single color string or list of colors.
        """
        self._bar_colors = self._normalize_colors(bar_colors, len(self._data))
        self._rebuild()

    def move(self, new_position: tuple[int, int]) -> None:
        """Move the entire chart to a new position.
        
        Args:
            new_position: New (x, y) position for the top-left corner.
        """
        if not isinstance(new_position, (tuple, list)) or len(new_position) != 2:
            raise ValueError("new_position must be a tuple of (x, y)")
        
        dx = new_position[0] - self._position[0]
        dy = new_position[1] - self._position[1]
        
        # Move all objects in the group
        for obj in self._group.objects:
            old_x, old_y = obj.position
            obj.position = (old_x + dx, old_y + dy)
        
        self._position = new_position
        self._group.update_geometry()

    def add_to_page(self, page) -> None:
        """Add all chart objects to a Drawpyo Page.
        
        Args:
            page: The Page object to add objects to.
        """
        for obj in self._group.objects:
            page.add_object(obj)

    # ------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------

    def _normalize_colors(self, colors: Union[str, list[str]], count: int) -> list[str]:
        """Normalize color input to a list of the correct length.
        
        Args:
            colors: Single color or list of colors.
            count: Number of colors needed.
            
        Returns:
            List of colors with length equal to count.
        """
        if isinstance(colors, str):
            return [colors] * count
        
        if not colors:
            return ["#66ccff"] * count
        
        # Extend list if too short
        if len(colors) < count:
            return colors + [colors[-1]] * (count - len(colors))
        
        return colors[:count]

    def _default_label_formatter(self, label: str, value: float) -> str:
        """Default formatter for bar labels.
        
        Args:
            label: The bar's label.
            value: The bar's value.
            
        Returns:
            Formatted label string.
        """
        return f"{label}\n{value}"

    def _calculate_scale(self) -> float:
        """Calculate the scale factor for bar heights.
        
        Returns:
            Scale factor to apply to values.
        """
        values = list(self._data.values())
        max_value = max(values)
        min_value = min(values)
        
        # Handle negative values
        if min_value < 0:
            raise ValueError("Negative values are not currently supported")
        
        if max_value == 0:
            return 1
        
        return self._max_bar_height / max_value

    def _calculate_chart_dimensions(self) -> tuple[int, int]:
        """Calculate the total width and height of the chart content area.
        
        Returns:
            (width, height) tuple.
        """
        num_bars = len(self._data)
        
        if self._direction == "up":
            width = num_bars * self._bar_width + (num_bars - 1) * self._bar_spacing
            height = self._max_bar_height
        else:  # right
            width = self._max_bar_height
            height = num_bars * self._bar_width + (num_bars - 1) * self._bar_spacing
        
        # Add space for labels
        if self._direction == "up":
            height += self._label_font_size + self.LABEL_TOP_MARGIN
        else:
            width += self.LABEL_WIDTH_HORIZONTAL + self.LABEL_SIDE_MARGIN
        
        # Add space for title
        if self._title:
            height += self._title_font_size + self.TITLE_BOTTOM_MARGIN
        
        return width, height

    def _rebuild(self) -> None:
        """Clear and rebuild the entire chart."""
        self._group.objects.clear()
        self._build_chart()

    def _build_chart(self) -> None:
        """Build all chart components."""
        x, y = self._position
        scale = self._calculate_scale()
        
        # Adjust starting position if title exists
        content_y = y
        if self._title:
            content_y += self._title_font_size + self.TITLE_BOTTOM_MARGIN
        
        # Background (optional)
        if self._background_color:
            self._add_background()
        
        # Title (optional)
        if self._title:
            self._add_title()
        
        # Bars and labels
        for i, (label, value) in enumerate(self._data.items()):
            self._add_bar_and_label(i, label, value, content_y, scale)
        
        self._group.update_geometry()

    def _add_background(self) -> None:
        """Add background rectangle with equal padding on all sides."""
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
        """Add chart title."""
        x, y = self._position
        chart_width, _ = self._calculate_chart_dimensions()
        
        title_obj = Object(
            value=self._title,
            position=(x, y),
            width=chart_width,
            height=self._title_font_size + 4,
            fillColor="none",
            strokeColor="none",
        )
        title_obj.text_format.fontSize = self._title_font_size
        title_obj.text_format.align = "center"
        self._group.add_object(title_obj)

    def _add_bar_and_label(
        self, index: int, label: str, value: float, content_y: int, scale: float
    ) -> None:
        """Add a single bar and its label.
        
        Args:
            index: Bar index.
            label: Bar label.
            value: Bar value.
            content_y: Y-coordinate for content area.
            scale: Scale factor for bar height.
        """
        x, _ = self._position
        bar_height = value * scale
        color = self._bar_fill_color or self._bar_colors[index]
        
        # Calculate bar position
        if self._direction == "up":
            bar_x = x + index * (self._bar_width + self._bar_spacing)
            bar_y = content_y + (self._max_bar_height - bar_height)
            bar_width = self._bar_width
            bar_display_height = bar_height
        else:  # right
            bar_x = x
            bar_y = content_y + index * (self._bar_width + self._bar_spacing)
            bar_width = bar_height
            bar_display_height = self._bar_width
        
        # Create bar
        bar = Object(
            value="",
            position=(bar_x, bar_y),
            width=bar_width,
            height=bar_display_height,
            fillColor=color,
            strokeColor=self._bar_stroke_color,
        )
        self._group.add_object(bar)
        
        # Create label
        formatted_label = self._label_formatter(label, value)
        
        if self._direction == "up":
            label_x = bar_x
            label_y = content_y + self._max_bar_height + self.LABEL_TOP_MARGIN
            label_width = self._bar_width
            label_align = "center"
        else:  # right
            label_x = x + self._max_bar_height + self.LABEL_SIDE_MARGIN
            label_y = bar_y
            label_width = self.LABEL_WIDTH_HORIZONTAL
            label_align = "left"
        
        label_obj = Object(
            value=formatted_label,
            position=(label_x, label_y),
            width=label_width,
            height=self._label_font_size + 10,
            fillColor="none",
            strokeColor="none",
        )
        label_obj.text_format.fontSize = self._label_font_size
        label_obj.text_format.align = label_align
        self._group.add_object(label_obj)

    # ------------------------------------------------------------------
    # Dunder methods
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """Return string representation of the chart."""
        return (
            f"BarChart(bars={len(self._data)}, "
            f"position={self._position}, "
            f"direction='{self._direction}')"
        )

    def __len__(self) -> int:
        """Return number of bars in the chart."""
        return len(self._data)