from typing import Union, Optional
from copy import deepcopy
from ..diagram.objects import Object, Group
from ..diagram.text_format import TextFormat
from ..utils.standard_colors import StandardColor
from ..utils.color_scheme import ColorScheme
from ..page import Page


class Legend:
    """A simple color/label legend diagram."""

    # Layout constants
    COLOR_BOX_SIZE = 20
    COLOR_TEXT_GAP = 10
    ROW_GAP = 8
    TITLE_BOTTOM_MARGIN = 20
    BACKGROUND_PADDING = 15

    def __init__(
        self, mapping: dict[str, Union[str, StandardColor, ColorScheme]], **kwargs
    ):
        """
        Args:
            mapping (dict[str, StandardColor, ColorScheme]): Mapping of labels to colors.

        Keyword Args:
            position (tuple[int, int]): Top-left diagram position. Default: (0, 0)
            title (str): Optional title.
            title_text_format (TextFormat): Formatting for the title.
            label_text_format (TextFormat): Formatting for labels.
            glass (bool): Whether color boxes have a glass effect. Default: False
            rounded (bool): Whether color boxes have rounded corners. Default: False
            background_color (str | StandardColor): Optional background fill color.
        """

        if not isinstance(mapping, dict) or not mapping:
            raise ValueError("Mapping must be a non-empty dict.")

        self._mapping: dict[str, Union[str, StandardColor, ColorScheme]] = (
            mapping.copy()
        )

        # Position
        self._position: tuple[int, int] = kwargs.get("position", (0, 0))

        # Title
        self._title: Optional[str] = kwargs.get("title")

        # Text formats
        self._title_text_format: TextFormat = deepcopy(
            kwargs.get("title_text_format", TextFormat())
        )
        self._label_text_format: TextFormat = deepcopy(
            kwargs.get("label_text_format", TextFormat())
        )

        # Color box styles
        self._glass: Optional[bool] = kwargs.get("glass", False)
        self._rounded: Optional[bool] = kwargs.get("rounded", False)

        # Background
        self._background_color: Optional[Union[str, StandardColor]] = kwargs.get(
            "background_color"
        )

        self._group = Group()
        self._build()

    # -----------------------------------------------------
    # Public methods
    # -----------------------------------------------------

    @property
    def group(self) -> Group:
        return self._group

    @property
    def position(self) -> tuple[int, int]:
        return self._position

    def update_mapping(
        self, mapping: dict[str, Union[str, StandardColor, ColorScheme]]
    ):
        self._mapping = mapping.copy()
        self._rebuild()

    def move(self, new_position: tuple[int, int]):
        new_x, new_y = new_position
        old_x, old_y = self._position
        dx = new_x - old_x
        dy = new_y - old_y

        for obj in self._group.objects:
            x, y = obj.position
            obj.position = (x + dx, y + dy)

        self._position = new_position
        self._group.update_geometry()

    def add_to_page(self, page: Page):
        for obj in self._group.objects:
            page.add_object(obj)

    # -----------------------------------------------------
    # Private methods
    # -----------------------------------------------------

    def _rebuild(self):
        self._group.objects.clear()
        self._build()

    def _build(self):
        x, y = self._position

        title_offset = (
            (self._title_text_format.fontSize or 16) + self.TITLE_BOTTOM_MARGIN
            if self._title
            else 0
        )

        bg_width, bg_height = self._compute_background_dimensions(title_offset)

        if self._background_color:
            self._add_background(bg_width, bg_height, title_offset)

        if self._title:
            self._add_title()

        current_y = y + title_offset

        # Create rows
        for label, color in self._mapping.items():
            self._add_row(label, color, current_y)
            current_y += self.COLOR_BOX_SIZE + self.ROW_GAP

        self._group.update_geometry()

    def _compute_background_dimensions(self, title_offset: int) -> tuple[int, int]:
        """Compute background size dynamically based on label lengths."""

        # Estimate text width
        max_text_len = max(len(label) for label in self._mapping)
        approx_text_width = max_text_len * 8

        width = (
            self.COLOR_BOX_SIZE
            + self.COLOR_TEXT_GAP
            + approx_text_width
            + (2 * self.BACKGROUND_PADDING)
        )
        height = (
            title_offset
            + len(self._mapping) * (self.COLOR_BOX_SIZE + self.ROW_GAP)
            - self.ROW_GAP
            + (2 * self.BACKGROUND_PADDING)
        )

        return width, height

    def _add_background(self, w: int, h: int, title_offset: int):
        x, y = self._position
        bg = Object(
            value="",
            position=(x - self.BACKGROUND_PADDING, y - self.BACKGROUND_PADDING),
            width=w,
            height=h,
            fillColor=self._background_color,
            strokeColor=None,
        )
        self._group.add_object(bg)

    def _add_title(self):
        x, y = self._position
        text_h = (self._title_text_format.fontSize or 16) + 4

        title_obj = Object(
            value=self._title,
            position=(x, y),
            width=200,
            height=text_h,
            fillColor="none",
            strokeColor="none",
        )

        title_obj.text_format = deepcopy(self._title_text_format)
        title_obj.text_format.align = "left"
        title_obj.text_format.verticalAlign = "top"

        self._group.add_object(title_obj)

    def _add_row(
        self, label: str, color: Union[str, StandardColor, ColorScheme], y: int
    ):
        x, _ = self._position

        # Color square
        color_box = Object(
            value="",
            position=(x, y),
            width=self.COLOR_BOX_SIZE,
            height=self.COLOR_BOX_SIZE,
            fillColor=None if isinstance(color, ColorScheme) else color,
            color_scheme=(color if isinstance(color, ColorScheme) else None),
            rounded=self._rounded,
            glass=self._glass,
        )
        self._group.add_object(color_box)

        # Text label
        label_obj = Object(
            value=label,
            position=(x + self.COLOR_BOX_SIZE + self.COLOR_TEXT_GAP, y),
            width=200,
            height=self.COLOR_BOX_SIZE,
            fillColor="none",
            strokeColor="none",
        )
        label_obj.text_format = deepcopy(self._label_text_format)
        label_obj.text_format.align = "left"
        label_obj.text_format.verticalAlign = "middle"

        self._group.add_object(label_obj)

    def __repr__(self):
        return f"Legend(items={len(self._mapping)}, position={self._position})"
