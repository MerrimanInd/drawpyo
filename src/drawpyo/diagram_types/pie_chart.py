from typing import Callable, Union, Optional
from copy import deepcopy
from ..diagram.objects import Object, Group
from ..diagram.text_format import TextFormat
from ..utils.standard_colors import StandardColor
from ..utils.color_scheme import ColorScheme
from ..page import Page
from ..diagram.extended_objects import PieSlice


class PieChart:
    """A configurable pie chart built entirely from Object, Group, and PieSlice.

    This chart is mutable - you can update data, styling, and position after creation.
    """

    # Layout constants
    DEFAULT_SIZE = 200
    TITLE_BOTTOM_MARGIN = 20
    LABEL_OFFSET = 5
    BACKGROUND_PADDING = 20

    def __init__(self, data: dict[str, float], **kwargs):
        """
        Args:
            data (dict[str, float]): Mapping of labels to numeric values.

        Keyword Args:
            position (tuple[int, int]): Top-left chart position. Default: (0, 0)
            size (int): Diameter of the pie. Default: 200
            slice_colors (list[str | StandardColor | ColorScheme]): Colors for slices.
            title (str): Optional title.
            title_text_format (TextFormat): Formatting for the title.
            label_text_format (TextFormat): Formatting for labels.
            background_color (str | StandardColor): Optional chart background.
            label_formatter (Callable[[str, float], str]): Custom formatter for slice labels.
        """

        # Validate data
        if not isinstance(data, dict):
            raise TypeError("Data must be a dict.")
        if not data:
            raise ValueError("Data cannot be empty.")

        invalid_keys = [k for k in data if not isinstance(k, str)]
        if invalid_keys:
            raise TypeError(f"All keys must be strings: {invalid_keys}")

        invalid_values = [k for k, v in data.items() if not isinstance(v, (int, float))]
        if invalid_values:
            raise TypeError(f"Values must be numeric: {invalid_values}")

        self._data: dict[str, float] = data.copy()

        # Position and size
        self._position: tuple[int, int] = kwargs.get("position", (0, 0))
        self._size: int = kwargs.get("size", self.DEFAULT_SIZE)

        # Text formats
        self._title_text_format: TextFormat = deepcopy(
            kwargs.get("title_text_format", TextFormat())
        )
        self._label_text_format: TextFormat = deepcopy(
            kwargs.get("label_text_format", TextFormat())
        )

        # Title
        self._title: Optional[str] = kwargs.get("title")

        # Background
        self._background_color = kwargs.get("background_color")

        # Colors
        slice_colors: list[Union[str, StandardColor, ColorScheme]] = kwargs.get(
            "slice_colors", ["#66ccff"]
        )
        self._slice_colors: list = self._normalize_colors(slice_colors, len(data))
        self._original_slice_colors = slice_colors

        # Label formatting
        self._label_formatter: Callable[[str, float, float], str] = kwargs.get(
            "label_formatter", self.default_label_formatter
        )

        # Build
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

    def update_data(self, data: dict[str, float]) -> None:
        if not isinstance(data, dict):
            raise TypeError("Data must be a dict.")
        if not data:
            raise ValueError("Data cannot be empty.")

        self._data = data.copy()
        self._slice_colors = self._normalize_colors(
            self._original_slice_colors, len(data)
        )
        self._rebuild()

    def update_colors(self, slice_colors: list[Union[str, StandardColor, ColorScheme]]):
        self._original_slice_colors = slice_colors
        self._slice_colors = self._normalize_colors(slice_colors, len(self._data))
        self._rebuild()

    def move(self, new_position: tuple[int, int]):
        new_x, new_y = new_position
        old_x, old_y = self._position
        dx = new_x - old_x
        dy = new_y - old_y

        for obj in self._group.objects:
            ox, oy = obj.position
            obj.position = (ox + dx, oy + dy)

        self._position = new_position
        self._group.update_geometry()

    def add_to_page(self, page: Page):
        for obj in self._group.objects:
            page.add_object(obj)

    def default_label_formatter(self, key, value, total):
        return f"{key}: {value/total*100:.1f}%"

    # ------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------

    def _normalize_colors(self, colors, count):
        if not colors:
            return ["#66ccff"] * count
        return [colors[i % len(colors)] for i in range(count)]

    def _rebuild(self):
        self._group.objects.clear()
        self._build_chart()

    def _build_chart(self):
        x, y = self._position

        # Compute vertical offsets if title is present
        title_h = (
            (self._title_text_format.fontSize or 16) + self.TITLE_BOTTOM_MARGIN
            if self._title
            else 0
        )
        pie_y = y + title_h

        if self._background_color:
            self._add_background(title_h)
        if self._title:
            self._add_title()

        total = sum(self._data.values())
        if total == 0:
            total = 1.0  # Avoid division by zero

        start_angle = 0.0

        for i, (label, value) in enumerate(self._data.items()):
            fraction = value / total if total else 0
            slice_color = self._slice_colors[i]

            slice_obj = PieSlice(
                value="",
                slice_value=fraction,
                position=(x, pie_y),
                size=self._size,
                startAngle=start_angle,
                fillColor=None if isinstance(slice_color, ColorScheme) else slice_color,
                color_scheme=(
                    slice_color if isinstance(slice_color, ColorScheme) else None
                ),
            )

            self._group.add_object(slice_obj)

            # SLICE LABEL
            slice_label_pos = self._get_slice_label_position(
                start_angle, fraction, x, pie_y
            )
            slice_text = self._label_formatter(label, value, total)
            slice_label = Object(
                value=slice_text,
                position=slice_label_pos,
                width=self._size,
                height=self._size,
                color_scheme=(
                    slice_color if isinstance(slice_color, ColorScheme) else None
                ),
                fillColor="none",
                strokeColor="none",
            )
            self._group.add_object(slice_label)

            start_angle += fraction

        self._group.update_geometry()

    def _get_slice_label_position(
        self, start_angle: float, fraction: float, x: int, y: int
    ) -> tuple[int, int]:
        import math

        # Mittelpunktwinkel der Scheibe (normalisiert 0–1)
        mid_angle = start_angle + (fraction / 2)

        # In Radiant umrechnen (Uhrzeigersinn)
        theta = (mid_angle * 2 * math.pi) - (math.pi / 2)

        # Radius + Offset
        offset = (self._size / 4) + self.LABEL_OFFSET

        # Kreisposition berechnen
        label_x = x + math.cos(theta) * offset
        label_y = y + math.sin(theta) * offset

        return (label_x, label_y)

    def _add_background(self, title_h: int):
        x, y = self._position
        size = self._size
        bg = Object(
            value="",
            position=(x - self.BACKGROUND_PADDING, y - self.BACKGROUND_PADDING),
            width=size + 2 * self.BACKGROUND_PADDING,
            height=size + 2 * self.BACKGROUND_PADDING + title_h,
            fillColor=self._background_color,
            strokeColor=None,
        )
        self._group.add_object(bg)

    def _add_title(self):
        x, y = self._position
        title_height = (self._title_text_format.fontSize or 16) + 4

        title_obj = Object(
            value=self._title,
            position=(x, y),
            width=self._size,
            height=title_height,
            fillColor="none",
            strokeColor="none",
        )

        title_obj.text_format = deepcopy(self._title_text_format)
        title_obj.text_format.align = "center"
        title_obj.text_format.verticalAlign = "top"

        self._group.add_object(title_obj)

    def __repr__(self):
        return f"PieChart(slices={len(self._data)}, position={self._position})"
