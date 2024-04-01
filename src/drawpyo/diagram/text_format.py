from .base_diagram import DiagramBase

__all__ = ["TextFormat"]

directions = {None: None, "horizontal": 1, "vertical": 0}
directions_inv = {v: k for k, v in directions.items()}


class TextFormat(DiagramBase):
    """The TextFormat class handles all of the formatting specifically around a text box or label."""

    def __init__(self, **kwargs):
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
            fomrattedText (bool, optional): Whether to render the text as HTML formatted or not

        """
        super().__init__(**kwargs)
        self.fontFamily = kwargs.get("fontFamily", None)
        self.fontSize = kwargs.get("fontSize", None)
        self.fontColor = kwargs.get("fontColor", None)
        self.labelBorderColor = kwargs.get("labelBorderColor", None)
        self.labelBackgroundColor = kwargs.get("labelBackgroundColor", None)
        self.labelPosition = kwargs.get("labelPosition", None)
        self.textShadow = kwargs.get("textShadow", None)
        self.textOpacity = kwargs.get("textOpacity", None)
        self.spacingTop = kwargs.get("spacingTop", None)
        self.spacingLeft = kwargs.get("spacingLeft", None)
        self.spacingBottom = kwargs.get("spacingBottom", None)
        self.spacingRight = kwargs.get("spacingRight", None)
        self.spacing = kwargs.get("spacing", None)
        self.align = kwargs.get("align", None)
        self.verticalAlign = kwargs.get("verticalAlign", None)
        # These need to be enumerated
        self.direction = kwargs.get("direction", None)
        # This is actually horizontal. 0 means vertical text, 1 or not present
        # means horizontal
        self.formattedText = kwargs.get(
            "formattedText", None
        )  # prints in the style string as html
        self.bold = kwargs.get("bold", False)
        self.italic = kwargs.get("italic", False)
        self.underline = kwargs.get("underline", False)

        self._style_attributes = [
            "html",
            "fontFamily",
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

    @property
    def formattedText(self):
        """formattedText wraps the Draw.io style attribute 'html'. This controls whether the text is rendered with HTML attributes or as plain text."""
        return self.html

    @formattedText.setter
    def formattedText(self, value):
        self.html = value

    @formattedText.deleter
    def formattedText(self, value):
        self.html = None

    # The direction of the text is encoded as 'horizontal' in Draw.io. This is
    # unintuitive so I provided a direction alternate syntax.
    @property
    def horizontal(self):
        return directions[self._direction]

    @horizontal.setter
    def horizontal(self, value):
        if value in directions_inv.keys():
            self._direction = directions_inv[value]
        else:
            raise ValueError("{0} is not an allowed value of horizontal".format(value))

    @property
    def directions(self):
        """The direction controls the direction of the text and can be either horizontal or vertical."""
        return directions

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        if value in directions.keys():
            self._direction = value
        else:
            raise ValueError("{0} is not an allowed value of direction".format(value))

    @property
    def font_style(self):
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
        # 7 = bolt, italic, and underlined

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
