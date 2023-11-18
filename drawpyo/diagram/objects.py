from .base_diagram import DiagramBase, import_shape_databases


__all__ = ["BasicObject", "Group"]

general = import_shape_databases(filename='shape_libraries\\general_w_inherit.toml')
line_styles = import_shape_databases(filename='formatting_database\\line_styles.toml')

text_directions = {None: None, "horizontal": 1, "vertical": 0}

container = {None: None, "vertical_container": None}

"""
TODO: Delete once rework is complete

# Dash pattern property
line_styles = {
    None: None,
    "solid": "0",
    "small_dash": "1",
    "medium_dash": "1;dashPattern=8 8",
    "large_dash": "1;dashPattern=12 12",
    "small_dot": "1;dashPattern=1 1",
    "medium_dot": "1;dashPattern=1 2",
    "large_dot": "1;dashPattern=1 4",
}


base_styles = {
    None: "",
    "rectanle": "",
    "rounded rectangle": "rounded=1;",
    "text": "text;",
    "ellipse": "ellipse;",
    "square": "aspect=fixed;",
    "circle": "ellipse;aspect=fixed;",
    "process": "shape=process;backgroundOutline=1;",
    "diamond": "rhombus;",
    "parallelogram": "shape=parallelogram;perimeter=parallelogramPerimeter;fixedSize=1;",
    "hexagon": "shape=hexagon;perimeter=hexagonPerimeter2;fixedSize=1;",
    "triangle": "triangle;",
    "cylinder": "shape=cylinder3;boundedLbl=1;backgroundOutline=1;",
    "cloud": "ellipse;shape=cloud;",
    "document": "shape=document;boundedLbl=1;",
    "internal storage": "shape=internalStorage;backgroundOutline=1;",
    "cube": "shape=cube;boundedLbl=1;backgroundOutline=1;darkOpacity=0.05;darkOpacity2=0.1;",
    "step": "shape=step;perimeter=stepPerimeter;",
    "trapezoid": "shape=trapezoid;perimeter=trapezoidPerimeter;",
    "tape": "shape=tape;",
    "note": "shape=note;backgroundOutline=1;darkOpacity=0.05;",
    "card": "shape=card;",
    "callout": "shape=callout;perimeter=calloutPerimeter;",
    "actor": "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;outlineConnect=0;",
    "or": "shape=xor;",
    "and": "shape=or;",
    "data storage": "shape=dataStorage;fixedSize=1;",
    "container": "swimlane;startSize=0;",
    "labeled container": "swimlane;",
    "labeled horizontal container": "swimlane;horizontal=0;",
}


default_sizes = {
    None: (120, 60),
    "rectangle": (120, 60),
    "rounded rectangle": (120, 60),
    "text": (60, 20),
    "ellipse": (120, 80),
    "square": (80, 80),
    "circle": (80, 80),
    "process": (120, 60),
    "diamond": (80, 80),
    "parallelogram": (120, 60),
    "hexagon": (120, 80),
    "triangle": (60, 80),
    "cylinder": (60, 80),
    "cloud": (120, 80),
    "document": (120, 80),
    "internal storage": (80, 80),
    "cube": (120, 80),
    "step": (120, 80),
    "trapezoid": (120, 60),
    "tape": (120, 100),
    "note": (80, 100),
    "card": (80, 100),
    "callout": (120, 80),
    "actor": (30, 60),
    "or": (60, 80),
    "and": (60, 80),
    "data storage": (100, 80),
    "container": (200, 200),
    "labeled container": (200, 200),
    "labeled horizontal container": (200, 200),
}
"""

###########################################################
# Objects
###########################################################


class BasicObject(DiagramBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # TODO: Delete once rework is complete
        # self.base_style = kwargs.get("base_style", None)

        # Geometry
        self.geometry = ObjGeometry(parent_object=self)
        self.position = kwargs.get("position", (0, 0))
        self.size = kwargs.get("size", [120, 80])
        self.vertex = kwargs.get("vertex", 1)

        # TODO enumerate to fixed
        self.aspect = kwargs.get("aspect", None)

        # Content
        self.value = kwargs.get("value", "")

        # Style

        # self.default_style = "rounded=0;whiteSpace=wrap;html=1;"
        # self.style = kwargs.get("style", self.default_style)

        self.html = kwargs.get("html", 1)
        self.rounded = kwargs.get("rounded", 0)
        self.white_space = kwargs.get("white_space", "wrap")
        self.fill_color = kwargs.get("fill_color", None)
        self.font_color = kwargs.get("font_color", None)
        self.opacity = kwargs.get("opacity", None)
        self.stroke_color = kwargs.get("stroke_color", None)
        self.glass = kwargs.get("glass", None)
        self.shadow = kwargs.get("shadow", None)
        self.comic = kwargs.get("comic", None)
        self.line_pattern = kwargs.get("line_pattern", None)

        self.font_family = kwargs.get("font_family", None)
        self.font_size = kwargs.get("font_size", None)
        self.align = kwargs.get("align", None)
        self.vertical_align = kwargs.get("vertical_align", None)
        self.label_position = kwargs.get("label_position", None)
        self.label_bg_color = kwargs.get("label_bg_color", None)
        self.label_border_color = kwargs.get("label_border_color", None)

        # These need to be enumerated
        self.text_direction = kwargs.get("font_direction", None)
        # This is actually horizontal. 0 means vertical text, 1 or not present
        # means horizontal

        self.text_opacity = kwargs.get("text_opacity", None)
        self.bold_font = kwargs.get("bold_font", False)
        self.italic_font = kwargs.get("italic_font", False)
        self.underline_font = kwargs.get("underline_font", False)

        # Base style declaration comes last since it overwrites the defaults
        # set by all kwargs.get lines above
        #self.parse_style_string(base_styles[self.base_style])

        self.out_edges = kwargs.get("out_edges", [])
        self.in_edges = kwargs.get("in_edges", [])

        self.xml_class = "mxCell"


    def __repr__(self):
        if self.value is not None:
            name_str = "{0} object with value {1}".format(
                self.__class__.__name__, self.value
            )
        else:
            name_str = "{0} object".format(self.__class__.__name__)
        return name_str

    def __str_(self):
        return self.__repr__()

    @property
    def attributes(self):
        return {
            "id": self.id,
            "value": self.value,
            "style": self.style,
            "vertex": self.vertex,
            "parent": self.parent_id,
        }


    ###########################################################
    # Style templates
    ###########################################################

    @property
    def line_styles(self):
        return line_styles

    @property
    def text_directions(self):
        return text_directions

    @property
    def container(self):
        return container

    """
    TODO: Delete once rework is complete
    @property
    def base_styles(self):
        return base_styles

    @property
    def default_sizes(self):
        return default_sizes
    """

    ###########################################################
    # Style properties
    ###########################################################

    @property
    def style_attributes(self):
        return {
            "html": self.html,
            "whiteSpace": self.white_space,
            "rounded": self.rounded,
            "fillColor": self.fill_color,
            "fontColor": self.font_color,
            "strokeColor": self.stroke_color,
            "glass": self.glass,
            "shadow": self.shadow,
            "comic": self.comic,
            "fontFamily": self.font_family,
            "align": self.align,
            "verticalAlign": self.vertical_align,
            "labelPosition": self.label_position,
            "labelBackgroundColor": self.label_bg_color,
            "labelBorderColor": self.label_border_color,
            "fontSize": self.font_size,
            "horizontal": self.horizontal,
            "textOpacity": self.text_opacity,
            "opacity": self.opacity,
            "dashed": self.dashed,
        }

    @property
    def base_style(self):
        return self._base_style

    @base_style.setter
    def base_style(self, value):
        if value in base_styles.keys():
            self._base_style = value
        else:
            raise ValueError(
                "{0} is not an allowed value of base_style".format(value)
            )

    @property
    def horizontal(self):
        return text_directions[self._text_direction]

    @property
    def text_direction(self):
        return self._text_direction

    @text_direction.setter
    def text_direction(self, value):
        if value in text_directions.keys():
            self._text_direction = value
        else:
            raise ValueError(
                "{0} is not an allowed value of text_direction".format(value)
            )

    @property
    def font_style(self):
        # TODO there HAS to be a better way to do this
        # it's basically an enumerated truth table
        bld = self.bold_font
        ita = self.italic_font
        unl = self.underline_font

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

    @property
    def dashed(self):
        return line_styles[self._line_pattern]

    @property
    def line_pattern(self):
        return self._line_pattern

    @line_pattern.setter
    def line_pattern(self, value):
        if value in line_styles.keys():
            self._line_pattern = value
        else:
            raise ValueError(
                "{0} is not an allowed value of line_pattern".format(value)
            )

    ###########################################################
    # Geometry properties
    ###########################################################

    # Position property
    @property
    def position(self):
        return (self.geometry.x, self.geometry.y)

    @position.setter
    def position(self, value):
        self.geometry.x = value[0]
        self.geometry.y = value[1]

    @property
    def center_position(self):
        x = self.geometry.x + self.geometry.width / 2
        y = self.geometry.y + self.geometry.height / 2
        return (x, y)

    @center_position.setter
    def center_position(self, position):
        self.geometry.x = position[0] - self.geometry.width / 2
        self.geometry.y = position[1] - self.geometry.height / 2

    # Size property
    @property
    def size(self):
        return (self.geometry.width, self.geometry.height)

    @size.setter
    def size(self, value):
        self.geometry.width = value[0]
        self.geometry.height = value[1]

    ###########################################################
    # Edge Tracking
    ###########################################################

    def add_out_edge(self, edge):
        self.out_edges.append(edge)

    def remove_out_edge(self, edge):
        self.out_edges.remove(edge)

    def add_in_edge(self, edge):
        self.in_edges.append(edge)

    def remove_in_edge(self, edge):
        self.in_edges.remove(edge)

    ###########################################################
    # XML Generation
    ###########################################################

    @property
    def xml(self):
        tag = (
            self.xml_open_tag
            + "\n  "
            + self.geometry.xml
            + "\n"
            + self.xml_close_tag
        )
        return tag


class ObjGeometry(DiagramBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.xml_class = "mxGeometry"

        self.parent_object = kwargs.get("parent_object", None)
        self.x = kwargs.get("x", 0)
        self.y = kwargs.get("y", 0)
        self.width = kwargs.get("width", 120)
        self.height = kwargs.get("height", 60)
        self.as_attribute = kwargs.get("as_attribute", "geometry")

    @property
    def attributes(self):
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "as": self.as_attribute,
        }


class Group:
    def __init__(self, **kwargs):
        self.objects = kwargs.get("objects", [])
        self.geometry = ObjGeometry()

    def add_object(self, obj):
        if not isinstance(obj, list):
            obj = [obj]
        for o in obj:
            if o not in self.objects:
                self.objects.append(o)
        self.update_geometry()

    def update_geometry(self):
        self.geometry.x = self.left
        self.geometry.y = self.top
        self.geometry.width = self.width
        self.geometry.height = self.height

    ###########################################################
    # Passive properties
    ###########################################################

    @property
    def left(self):
        return min([obj.geometry.x for obj in self.objects])

    @property
    def right(self):
        return max(
            [obj.geometry.x + obj.geometry.width for obj in self.objects]
        )

    @property
    def top(self):
        return min([obj.geometry.y for obj in self.objects])

    @property
    def bottom(self):
        return max(
            [obj.geometry.y + obj.geometry.height for obj in self.objects]
        )

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.bottom - self.top

    @property
    def size(self):
        return (self.width, self.height)

    ###########################################################
    # Position properties
    ###########################################################

    @property
    def center_position(self):
        return (self.left + self.width / 2, self.top + self.height / 2)

    @center_position.setter
    def center_position(self, new_center):
        current_center = (
            self.left + self.width / 2,
            self.top + self.height / 2,
        )
        delta_x = new_center[0] - current_center[0]
        delta_y = new_center[1] - current_center[1]
        for obj in self.objects:
            obj.position = (obj.geometry.x + delta_x, obj.geometry.y + delta_y)
            # obj.geometry.x = obj.geometry.x + delta_x
            # obj.geometry.y = obj.geometry.y + delta_y
        # self.geometry.x = new_center[0] + self.width / 2
        # self.geometry.y = new_center[1] + self.height / 2
        self.update_geometry()

    @property
    def position(self):
        return (self.left, self.top)

    @position.setter
    def position(self, new_position):
        current_position = (self.left, self.top)
        delta_x = new_position[0] - current_position[0]
        delta_y = new_position[1] - current_position[1]
        for obj in self.objects:
            obj.position = (obj.geometry.x + delta_x, obj.geometry.y + delta_y)
            # obj.geometry.x = obj.geometry.x + delta_x
            # obj.geometry.y = obj.geometry.y + delta_y
        # self.geometry.x = new_position[0]
        # self.geometry.y = new_position[1]
        self.update_geometry()
