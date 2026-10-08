from dataclasses import dataclass
from typing import Callable, Union, Optional
from enum import Enum
from copy import deepcopy
from ..diagram.objects import Object, Group
from ..diagram.text_format import TextFormat
from ..utils.standard_colors import StandardColor
from ..utils.color_scheme import ColorScheme
from ..page import Page
from ..diagram.extended_objects import DonutArc


class AnnotationPosition(Enum):
    INSIDE = 0.6
    MIDDLE = 1.0
    OUTSIDE = 1.4


@dataclass(frozen=True)
class ArcAnnotation:
    name: str = "Annotation"
    formatter: Callable[[str, float, float], str] = (
        lambda label, value, total: f"{value/total:.1%}"
    )
    position: Union[AnnotationPosition, float] = AnnotationPosition.MIDDLE
    text_format: Optional[TextFormat] = None


class DonutChart:
    """A configurable donut chart built entirely from Object, Group, and DonutArc.

    This chart is mutable - you can update data, styling, and position after creation.
    """

    # Layout constants
    DEFAULT_SIZE = 200
    DEFAULT_INNER_RATIO = 0.65

    # Spacing constants
    TITLE_BOTTOM_MARGIN = 10
    MAX_TITLE_DISTANCE = 50
    BACKGROUND_PADDING = 20

    def __init__(self, data: dict[str, float], **kwargs):
        """
        Args:
            data (dict[str, float]): Mapping of labels to numeric values.

        Keyword Args:
            position (tuple[int, int]): Top-left chart position. Default: (0, 0)
            size (int): Outer diameter of the donut. Default: 200
            inner_radius_ratio (float): The inner radius as a fraction of the outer radius (0.0-1.0). Default: 0.65
            arc_colors (list[str | StandardColor | ColorScheme]): Colors for arcs.
            title (str): Optional title.
            title_text_format (TextFormat): Formatting for the title.
            background_color (str | StandardColor): Optional chart background.
            annotations (list[ArcAnnotation]): A list of radial annotations rendered for each arc.
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

        # Inner radius ratio
        self._inner_radius_ratio: float = kwargs.get(
            "inner_radius_ratio", self.DEFAULT_INNER_RATIO
        )
        if not (0.0 <= self._inner_radius_ratio <= 1.0):
            raise ValueError("inner_radius_ratio must be between 0.0 and 1.0")

        # Text formats
        self._title_text_format: TextFormat = deepcopy(
            kwargs.get("title_text_format", TextFormat())
        )

        # Title
        self._title: Optional[str] = kwargs.get("title")

        # Background
        self._background_color: Optional[Union[str, StandardColor]] = kwargs.get(
            "background_color"
        )

        # Colors
        arc_colors: list[Union[str, StandardColor, ColorScheme]] = kwargs.get(
            "arc_colors", ["#66ccff"]
        )
        self._arc_colors: list = self._normalize_colors(arc_colors, len(data))
        self._original_arc_colors = arc_colors

        # Annotations
        self._annotations: list[ArcAnnotation] = kwargs.get(
            "annotations", self._default_annotations()
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
        self._arc_colors = self._normalize_colors(self._original_arc_colors, len(data))
        self._rebuild()

    def update_colors(self, arc_colors: list[Union[str, StandardColor, ColorScheme]]):
        self._original_arc_colors = arc_colors
        self._arc_colors = self._normalize_colors(arc_colors, len(self._data))
        self._rebuild()

    def move(self, new_position: tuple[int, int]):
        dx = new_position[0] - self._position[0]
        dy = new_position[1] - self._position[1]
        for obj in self._group.objects:
            ox, oy = obj.position
            obj.position = (ox + dx, oy + dy)
        self._position = new_position
        self._group.update_geometry()

    def add_to_page(self, page: Page):
        for obj in self._group.objects:
            page.add_object(obj)

    # ------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------

    def _default_annotations(self) -> list[ArcAnnotation]:
        return [
            ArcAnnotation(
                name="Label",
                formatter=lambda label, value, total: label,
                position=AnnotationPosition.INSIDE,
                text_format=None,
            ),
            ArcAnnotation(
                name="Value",
                formatter=lambda label, value, total: f"{value/total:.1%}",
                position=AnnotationPosition.MIDDLE,
                text_format=None,
            ),
        ]

    def _outer_radius(self) -> float:
        return self._size / 2

    def _inner_radius(self) -> float:
        return self._outer_radius() * self._inner_radius_ratio

    def _max_annotation_radius(self) -> float:
        return max(
            self._annotation_radius(annotation.position)
            for annotation in self._annotations
        )

    def _max_chart_radius(self) -> float:
        return max(self._outer_radius(), self._max_annotation_radius())

    def _annotation_radius(self, position: Union[AnnotationPosition, float]) -> float:
        outer = self._outer_radius()
        inner = self._inner_radius()
        base = (inner + outer) / 2

        if isinstance(position, AnnotationPosition):
            return base * position.value
        return base * position

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
            max(
                self._title_text_format.fontSize or 16,
                (self._max_chart_radius() - self._outer_radius()),
            )
            + self.TITLE_BOTTOM_MARGIN
            if self._title
            else 0
        )
        arc_y = y + title_h

        if self._background_color:
            self._add_background(title_h)
        if self._title:
            self._add_title()

        total = sum(self._data.values())
        if total == 0:
            total = 1.0  # Avoid division by zero

        start_angle = 0.0
        arc_width = 1.0 - self._inner_radius_ratio

        annotations = self._annotations

        for i, (label, value) in enumerate(self._data.items()):
            fraction = value / total if total else 0
            arc_color = self._arc_colors[i]

            arc_obj = DonutArc(
                value="",
                arc_value=fraction,
                position=(x, arc_y),
                size=self._size,
                startAngle=start_angle,
                arcWidth=arc_width,
                fillColor=None if isinstance(arc_color, ColorScheme) else arc_color,
                color_scheme=(
                    arc_color if isinstance(arc_color, ColorScheme) else None
                ),
            )

            self._group.add_object(arc_obj)

            for annotation in annotations:
                radius = self._annotation_radius(annotation.position)
                pos = self._polar_to_xy(start_angle, fraction, x, arc_y, radius)
                text = annotation.formatter(label, value, total)

                obj = Object(
                    value=text,
                    position=pos,
                    width=self._size,
                    height=self._size,
                    color_scheme=(
                        arc_color if isinstance(arc_color, ColorScheme) else None
                    ),
                    fillColor="none",
                    strokeColor="none",
                )

                if annotation.text_format:
                    obj.text_format = deepcopy(annotation.text_format)
                else:
                    obj.text_format = deepcopy(TextFormat())

                self._group.add_object(obj)

            start_angle += fraction

        self._group.update_geometry()

    def _polar_to_xy(
        self, start_angle: float, fraction: float, x: int, y: int, radius: float
    ) -> tuple[float, float]:
        import math

        mid_angle = start_angle + fraction / 2
        theta = (mid_angle * 2 * math.pi) - (math.pi / 2)

        return (
            x + math.cos(theta) * radius,
            y + math.sin(theta) * radius,
        )

    def _add_background(self, title_h: int):
        r = self._max_chart_radius()
        x, y = self._position

        annotation_overflow = self._max_chart_radius() - self._outer_radius()
        bg = Object(
            value="",
            position=(
                (
                    x - 2 * annotation_overflow - self.BACKGROUND_PADDING,
                    y - 2 * annotation_overflow - self.BACKGROUND_PADDING,
                )
            ),
            width=2 * r + 2 * self.BACKGROUND_PADDING + 2 * annotation_overflow,
            height=2 * r
            + 2 * self.BACKGROUND_PADDING
            + 2 * annotation_overflow
            + title_h,
            fillColor=self._background_color,
            strokeColor=None,
        )
        self._group.add_object(bg)

    def _add_title(self):
        x, y = self._position
        title_height = (self._title_text_format.fontSize or 16) + 4
        annotation_overflow = self._max_chart_radius() - self._outer_radius()

        title_obj = Object(
            value=self._title,
            position=(
                x,
                y
                - min(self.MAX_TITLE_DISTANCE, annotation_overflow)
                - self.TITLE_BOTTOM_MARGIN,
            ),
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
        return f"DonutChart(arcs={len(self._data)}, position={self._position})"
