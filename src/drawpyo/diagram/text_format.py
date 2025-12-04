from typing import Optional, Dict, Any, Union
from ..utils.logger import logger
from .base_diagram import DiagramBase

__all__ = ["TextFormat"]

directions: Dict[Optional[str], Optional[int]] = {
    None: None,
    "horizontal": 1,
    "vertical": 0,
}
directions_inv: Dict[Optional[int], Optional[str]] = {
    v: k for k, v in directions.items()
}


class TextFormat(DiagramBase):
    """The TextFormat class handles all of the formatting specifically around a text box or label."""

    def __init__(self, **kwargs: Any) -> None:
        """TextFormat objects can be initialized with no properties or any of what's listed below:

        Keyword Args:
            fontColor (int, optional): The color of the text in the object (#ffffff)
            fontFamily (str, optional): The typeface of the text in the object (see Draw.io for available fonts)
            fontSize (int, optional): The size of the text in the object in points
            align (str, optional): The horizontal alignment of the text in the object ('left', 'center', or 'right')
            verticalAlign (str, optional): The vertical alignment of the text in the object ('top', 'middle', 'bottom')
            textOpacity (int, optional): The opacity of the text in the object
            direction (str, optional): The direction to print the text ('vertical', 'horizontal')
            bold (bool, optional): Whether the text in the object should be bold
            italic (bool, optional): Whether the text in the object should be italic
            underline (bool, optional): Whether the text in the object should be underlined
            labelPosition (str, optional): The position of the object label ('left', 'center', or 'right')
            labelBackgroundColor (str, optional): The background color of the object label (#ffffff)
            labelBorderColor (str, optional): The border color of the object label (#ffffff)
            formattedText (bool, optional): Whether to render the text as HTML formatted or not

        """
        super().__init__(**kwargs)
        self.fontFamily: Optional[str] = kwargs.get("fontFamily", None)
        self.fontSize: Optional[int] = kwargs.get("fontSize", None)
        self.fontColor: Optional[str] = kwargs.get("fontColor", None)
        self.labelBorderColor: Optional[str] = kwargs.get("labelBorderColor", None)
        self.labelBackgroundColor: Optional[str] = kwargs.get(
            "labelBackgroundColor", None
        )
        self.labelPosition: Optional[str] = kwargs.get("labelPosition", None)
        self.textShadow: Optional[Union[int, str]] = kwargs.get("textShadow", None)
        self.textOpacity: Optional[int] = kwargs.get("textOpacity", None)
        self.spacingTop: Optional[int] = kwargs.get("spacingTop", None)
        self.spacingLeft: Optional[int] = kwargs.get("spacingLeft", None)
        self.spacingBottom: Optional[int] = kwargs.get("spacingBottom", None)
        self.spacingRight: Optional[int] = kwargs.get("spacingRight", None)
        self.spacing: Optional[int] = kwargs.get("spacing", None)
        self.align: Optional[str] = kwargs.get("align", None)
        self.verticalAlign: Optional[str] = kwargs.get("verticalAlign", None)
        # These need to be enumerated
        self._direction: Optional[str] = kwargs.get("direction", None)
        # This is actually horizontal. 0 means vertical text, 1 or not present
        # means horizontal
        self.html: Optional[bool] = kwargs.get(
            "formattedText", None
        )  # prints in the style string as html
        self.bold: bool = kwargs.get("bold", False)
        self.italic: bool = kwargs.get("italic", False)
        self.underline: bool = kwargs.get("underline", False)

        self._style_attributes: list[str] = [
            "html",
            "fontFamily",
            "fontStyle",
            "fontSize",
            "fontColor",
            "labelBorderColor",
            "labelBackgroundColor",
            "labelPosition",
            "textShadow",
            "textOpacity",
            "spacingTop",
            "spacingLeft",
            "spacingBottom",
            "spacingRight",
            "spacing",
            "align",
            "verticalAlign",
            "horizontal",
        ]

    def __repr__(self) -> str:
        """
        A concise, informative representation for TextFormat.
        """
        cls = self.__class__.__name__
        parts = []

        # Font properties
        if self.fontFamily:
            parts.append(f"fontFamily={self.fontFamily!r}")
        if self.fontSize:
            parts.append(f"fontSize={self.fontSize}")
        if self.fontColor:
            parts.append(f"fontColor={self.fontColor!r}")

        # Style flags
        flags = []
        if self.bold:
            flags.append("bold")
        if self.italic:
            flags.append("italic")
        if self.underline:
            flags.append("underline")
        if flags:
            parts.append("fontStyle=" + "|".join(flags))

        # Alignment
        if self.align:
            parts.append(f"align={self.align!r}")
        if self.verticalAlign:
            parts.append(f"verticalAlign={self.verticalAlign!r}")
        if self._direction:
            parts.append(f"direction={self._direction!r}")
        if self.html:
            parts.append("formattedText=True")

        # Label styling
        if self.labelPosition:
            parts.append(f"labelPosition={self.labelPosition!r}")

        return f"{cls}(" + ", ".join(parts) + ")"

    @property
    def formattedText(self) -> Optional[bool]:
        """formattedText wraps the Draw.io style attribute 'html'. This controls whether the text is rendered with HTML attributes or as plain text."""
        return self.html

    @formattedText.setter
    def formattedText(self, value: Optional[bool]) -> None:
        self.html = value

    @formattedText.deleter
    def formattedText(self) -> None:
        self.html = None

    # The direction of the text is encoded as 'horizontal' in Draw.io. This is
    # unintuitive so I provided a direction alternate syntax.
    @property
    def horizontal(self) -> Optional[int]:
        return directions[self._direction]

    @horizontal.setter
    def horizontal(self, value: Optional[int]) -> None:
        if value in directions_inv.keys():
            self._direction = directions_inv[value]
        else:
            raise ValueError("{0} is not an allowed value of horizontal".format(value))

    @property
    def directions(self) -> Dict[Optional[str], Optional[int]]:
        """The direction controls the direction of the text and can be either horizontal or vertical."""
        return directions

    @property
    def direction(self) -> Optional[str]:
        return self._direction

    @direction.setter
    def direction(self, value: Optional[str]) -> None:
        if value in directions.keys():
            self._direction = value
        else:
            raise ValueError("{0} is not an allowed value of direction".format(value))

    @property
    def font_style(self) -> int:
        """The font_style is a numeric format that corresponds to a combination of three other attributes: bold, italic, and underline. Any combination of them can be true."""
        bld = self.bold
        ita = self.italic
        unl = self.underline

        # 0 = normal
        # 1 = bold
        # 2 = italic
        # 3 = bold and italic
        # 4 = underline
        # 5 = bold and underlined
        # 6 = italic and underlined
        # 7 = bold, italic, and underlined

        if not bld and not ita and not unl:
            return 0
        elif bld and not ita and not unl:
            return 1
        elif not bld and ita and not unl:
            return 2
        elif bld and ita and not unl:
            return 3
        elif not bld and not ita and unl:
            return 4
        elif bld and not ita and unl:
            return 5
        elif not bld and ita and unl:
            return 6
        elif bld and ita and unl:
            return 7
        return 0  # fallback (shouldn't be reached)

    @property
    def fontStyle(self) -> Optional[int]:
        if self.font_style != 0:
            return self.font_style
        return None
