from .base_diagram import (
    DiagramBase,
    import_shape_database,
    style_str_from_dict,
)

__all__ = ["BasicObject", "Group", "object_from_library"]

general = import_shape_database(
    file_name="shape_libraries\\general.toml", relative=True
)
line_styles = import_shape_database(
    file_name="formatting_database\\line_styles.toml", relative=True
)

base_libraries = {"general": general}

text_directions = {None: None, "horizontal": 1, "vertical": 0}
text_directions_inv = {v: k for k, v in text_directions.items()}

container = {None: None, "vertical_container": None}

def import_shape_library(library_path, name):
    data = import_shape_database(
        filename=library_path
    )
    base_libraries[name] = data

def object_from_library(library, obj_name, **kwargs):
    new_obj = BasicObject(**kwargs)
    new_obj.format_as_library_object(library, obj_name)
    return new_obj


###########################################################
# Objects
###########################################################


class BasicObject(DiagramBase):
    ###########################################################
    # Initialization Functions
    ###########################################################
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._style_attributes = [
            "html",
            "whiteSpace",
            "rounded",
            "fillColor",
            "fontColor",
            "strokeColor",
            "glass",
            "shadow",
            "comic",
            "fontFamily",
            "align",
            "verticalAlign",
            "labelPosition",
            "labelBackgroundColor",
            "labelBorderColor",
            "fontSize",
            "horizontal",
            "textOpacity",
            "opacity",
            "dashed",
        ]

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
        self.baseStyle = kwargs.get("baseStyle", None)

        self.html = kwargs.get("html", 1)
        self.rounded = kwargs.get("rounded", 0)
        self.whiteSpace = kwargs.get("whiteSpace", "wrap")
        self.fillColor = kwargs.get("fillColor", None)
        self.fontColor = kwargs.get("fontColor", None)
        self.opacity = kwargs.get("opacity", None)
        self.strokeColor = kwargs.get("strokeColor", None)
        self.glass = kwargs.get("glass", None)
        self.shadow = kwargs.get("shadow", None)
        self.comic = kwargs.get("comic", None)
        self.linePattern = kwargs.get("linePattern", "solid")

        self.fontFamily = kwargs.get("fontFamily", None)
        self.fontSize = kwargs.get("fontSize", None)
        self.align = kwargs.get("align", None)
        self.verticalAlign = kwargs.get("verticalAlign", None)
        self.labelPosition = kwargs.get("labelPosition", None)
        self.labelBackgroundColor = kwargs.get("labelBackgroundColor", None)
        self.labelBorderColor = kwargs.get("labelBorderColor", None)

        # These need to be enumerated
        self.text_direction = kwargs.get("font_direction", None)
        # This is actually horizontal. 0 means vertical text, 1 or not present
        # means horizontal

        self.textOpacity = kwargs.get("textOpacity", None)
        self.bold_font = kwargs.get("bold_font", False)
        self.italic_font = kwargs.get("italic_font", False)
        self.underline_font = kwargs.get("underline_font", False)

        self.out_edges = kwargs.get("out_edges", [])
        self.in_edges = kwargs.get("in_edges", [])

        self.xml_class = "mxCell"

    @classmethod
    def create_from_style_string(cls, style_string):
        cls.apply_style_from_string(style_string)
        return cls

    @classmethod
    def create_from_library(cls, library, obj_name):
        new_obj = cls()
        new_obj.format_as_library_object(library, obj_name)
        return new_obj

    def format_as_library_object(self, library, obj_name):
        if type(library) == str:
            if library in base_libraries:
                library_dict = base_libraries[library]
                if obj_name in library_dict:
                    obj_dict = library_dict[obj_name]
                    self.apply_attribute_dict(obj_dict)
                else:
                    raise ValueError(
                        "Object {0} not in Library {1}".format(obj_name, library)
                    )
            else:
                raise ValueError(
                    "Library {0} not in base_libraries".format(library)
                )
        elif type(library) == dict:
            obj_dict = library[obj_name]
            self.apply_attribute_dict(obj_dict)
        else:
            raise ValueError("Unparseable libary passed in.")


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

    ###########################################################
    # Style properties
    ###########################################################

    # The direction of the text is encoded as 'horizontal' in Draw.io. This is
    # unintuitive so I provided a text_direction alternate syntax.
    @property
    def horizontal(self):
        return text_directions[self._text_direction]

    @horizontal.setter
    def horizontal(self, value):
        if value in text_directions_inv.keys():
            self._text_direction = text_directions_inv[value]
        else:
            raise ValueError(
                "{0} is not an allowed value of horizontal".format(value)
            )

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
        return line_styles[self._linePattern]

    @property
    def linePattern(self):
        return self._linePattern

    @linePattern.setter
    def linePattern(self, value):
        if value in line_styles.keys():
            self._linePattern = value
        else:
            raise ValueError(
                "{0} is not an allowed value of linePattern".format(value)
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
        self.update_geometry()
