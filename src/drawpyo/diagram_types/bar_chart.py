from ..diagram.objects import Object, Group


class BarChart:
    """A configurable bar chart built entirely from Object and Group."""

    def __init__(self, data: dict[str, float], **kwargs):
        """
        Args:
            data (dict[str, float]): Mapping of labels to numeric values.
        Keyword Args:
            position (tuple[int, int]): Chart top-left position.
            bar_width (int): Width of each bar.
            bar_spacing (int): Space between bars.
            max_bar_height (int): Height of the largest bar.
            bar_colors (str | list[str]): Single color or list of colors.
            direction (str): 'up' or 'right'.
            label_font_size (int): Font size for bar labels.
            title (str): Optional chart title.
            title_font_size (int): Font size for the title.
            fillColor (str): Optional fill color override.
            strokeColor (str): Stroke color for bars.
            background_color (str): Optional chart background fill.
        """
        self.data = data
        self.kwargs = kwargs

        # Default values
        self.position = kwargs.get("position", (0, 0))
        self.bar_width = kwargs.get("bar_width", 40)
        self.bar_spacing = kwargs.get("bar_spacing", 20)
        self.max_bar_height = kwargs.get("max_bar_height", 200)
        self.direction = kwargs.get("direction", "up")
        self.label_font_size = kwargs.get("label_font_size", 12)
        self.title = kwargs.get("title")
        self.title_font_size = kwargs.get("title_font_size", 16)
        self.fillColor = kwargs.get("fillColor")
        self.strokeColor = kwargs.get("strokeColor", "#000000")
        self.background_color = kwargs.get("background_color")

        # Normalize bar colors
        bar_colors = kwargs.get("bar_colors", "#66ccff")
        if isinstance(bar_colors, str):
            self.bar_colors = [bar_colors] * len(data)
        else:
            self.bar_colors = bar_colors + [bar_colors[-1]] * (
                len(data) - len(bar_colors)
            )

        self.group = Group()
        self._build_chart()

    # ------------------------------------------------------------------

    def _build_chart(self):
        data = self.data
        position = self.position
        max_value = max(data.values()) if data else 1
        scale = self.max_bar_height / max_value if max_value > 0 else 1
        x, y = position

        # Background (optional)
        if self.background_color:
            bg = Object(
                value="",
                position=position,
                width=len(data) * (self.bar_width + self.bar_spacing),
                height=self.max_bar_height + 40,
                fillColor=self.background_color,
                strokeColor=None,
            )
            self.group.add_object(bg)

        # Title (optional)
        if self.title:
            title_obj = Object(
                value=self.title,
                position=(x, y - self.title_font_size - 10),
                width=len(data) * (self.bar_width + self.bar_spacing),
                height=self.title_font_size + 4,
                fillColor="none",
                strokeColor="none",
            )
            title_obj.text_format.font_size = self.title_font_size
            title_obj.text_format.align = "center"
            self.group.add_object(title_obj)

        # Bars and labels
        for i, (label, value) in enumerate(data.items()):
            bar_height = value * scale
            color = self.bar_colors[i]

            if self.direction == "up":
                bar_x = x + i * (self.bar_width + self.bar_spacing)
                bar_y = y + (self.max_bar_height - bar_height)
            else:  # right
                bar_x = x
                bar_y = y + i * (self.bar_width + self.bar_spacing)

            bar = Object(
                value="",
                position=(bar_x, bar_y),
                width=self.bar_width if self.direction == "up" else bar_height,
                height=bar_height if self.direction == "up" else self.bar_width,
                fillColor=self.fillColor or color,
                strokeColor=self.strokeColor,
            )
            self.group.add_object(bar)

            # Label
            if self.direction == "up":
                label_pos = (bar_x, y + self.max_bar_height + 5)
            else:
                label_pos = (x + bar.height + 10, bar_y)

            label_obj = Object(
                value=f"{label}\n{value}",
                position=label_pos,
                width=self.bar_width if self.direction == "up" else 80,
                height=self.label_font_size + 10,
                fillColor="none",
                strokeColor="none",
            )
            label_obj.text_format.font_size = self.label_font_size
            label_obj.text_format.align = (
                "center" if self.direction == "up" else "left"
            )
            self.group.add_object(label_obj)

        self.group.update_geometry()

    # ------------------------------------------------------------------

    def add_to_page(self, page):
        """Add all objects in this chart to a Drawpyo Page."""
        for obj in self.group.objects:
            page.add_object(obj)

    def to_group(self) -> Group:
        """Return the Group containing all bar objects."""
        return self.group

    def move(self, new_position):
        """Move the entire chart group to a new top-left position."""
        self.group.position = new_position
