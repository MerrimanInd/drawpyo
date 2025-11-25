from __future__ import annotations
from typing import Union
import re
from .default_colors import DefaultColors


ColorType = Union[str, DefaultColors, None]


class ColorScheme:
    """
    Represents a set of colors used for an object's fill, stroke, and gradient.

    A color can be:
        • None
        • A hex string
        • A DefaultColor
    """

    HEX_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")

    ###########################################################
    # Initialization
    ###########################################################

    def __init__(
        self,
        fill_color: ColorType = None,
        stroke_color: ColorType = None,
        gradient: ColorType = None,
        font_color: ColorType = None,
    ) -> None:
        self.fill_color: ColorType = self._validated(fill_color)
        self.stroke_color: ColorType = self._validated(stroke_color)
        self.gradient: ColorType = self._validated(gradient)
        self.font_color: ColorType = self._validated(font_color)

    ###########################################################
    # Public Setters
    ###########################################################

    def set_fill_color(self, color: ColorType) -> None:
        self.fill_color = self._validated(color)

    def set_stroke_color(self, color: ColorType) -> None:
        self.stroke_color = self._validated(color)

    def set_gradient(self, color: ColorType) -> None:
        self.gradient = self._validated(color)

    def set_font_color(self, color: ColorType) -> None:
        self.font_color = self._validated(color)

    ###########################################################
    # Validation
    ###########################################################

    def _validated(self, color: ColorType) -> ColorType:
        """Validate hex strings or DefaultColor enums."""
        if color is None:
            return None

        if isinstance(color, DefaultColors):
            return color.value

        if isinstance(color, str):
            if not self.is_valid_hex(color):
                raise ValueError(
                    f"Invalid color '{color}'. "
                    f"Expected '#RRGGBB' (example: #A1B2C3)."
                )
            return color.upper()

        raise TypeError(
            f"Color must be a hex string like '#AABBCC', None, or a DefaultColor enum. "
            f"Received: {type(color)}"
        )

    @classmethod
    def is_valid_hex(cls, value: str) -> bool:
        """Return True if string is a valid #RRGGBB hex color."""
        return bool(cls.HEX_PATTERN.match(value))

    ###########################################################
    # Utility
    ###########################################################

    def __repr__(self) -> str:
        return (
            f"ColorScheme(fill={self.fill_color}, "
            f"stroke={self.stroke_color}, "
            f"gradient={self.gradient})"
            f"font_color={self.font_color})"
        )
