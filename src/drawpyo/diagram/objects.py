from os import path

from .base_diagram import (
    DiagramBase,
    import_shape_database,
)
from .style import (
    Style,
    style_str_from_dict,
)

__all__ = ["Object", "BasicObject", "Group", "object_from_library"]

general = import_shape_database(
    file_name=path.join("shape_libraries", "general.toml"), relative=True
)
line_styles = import_shape_database(
    file_name=path.join("formatting_database", "line_styles.toml"), relative=True
)

base_libraries = {"general": general}

text_directions = {None: None, "horizontal": 1, "vertical": 0}
text_directions_inv = {v: k for k, v in text_directions.items()}

container = {None: None, "vertical_container": None}


def import_shape_library(library_path, name):
    data = import_shape_database(filename=library_path)
    base_libraries[name] = data


def object_from_library(library, obj_name, **kwargs):
    """This function generates a Object from a library. The library can either be custom imported from a TOML or the name of one of the built-in Draw.io libraries.

    Any keyword arguments that can be passed in to a Object creation can be passed into this function and it will format the base object. However, the styling in the library will overwrite that formatting.

    Args:
        library (str or dict): The library containing the object
        obj_name (str): The name of the object in the library to generate

    Returns:
        Object: An object with the style from the library
    """
    new_obj = Object(**kwargs)
    new_obj.format_as_library_object(library, obj_name)
    return new_obj


###########################################################
# Objects
###########################################################


class Object(DiagramBase):
    """
    The Object class is the base object for all shapes in Draw.io.

    More information about objects are in the Usage documents at [Usage - Objects](../../usage/objects).
    """

    ###########################################################
    # Initialization Functions
    ###########################################################

    def __init__(self, value="", size=(120, 80), position=(0, 0), **kwargs):
        """A Object can be initialized with as many or as few of its styling attributes as is desired.

        Args:
            value (str, optional): The text to fill the object with. Defaults to "".
            size (tuple, optional): The size of the object in pixels, in (W, H). Defaults to (120, 80).
            position (tuple, optional): The position of the object in pixels, in (X, Y). Defaults to (0, 0).

        Keyword Args:
            template_object (Object, optional): Another object to copy the style_attributes from
            aspect
            rounded (bool, optional): Whether to round the corners of the shape
            whiteSpace (str, optional): white space
            fillColor (str, optional): The object fill color in a hex color code (#ffffff)
            opacity  (int, optional): The object's opacity, 0-100
            strokeColor: The object stroke color in a hex color code (#ffffff)
            glass (bool, optional): Apply glass styling to  the object
            shadow (bool, optional): Add a shadow to the object
            comic (bool, optional): Add comic styling to the object
            line_pattern (str, optional): The stroke style of the object.
            fontColor (int, optional): The color of the text in the object (#ffffff)
            fontFamily (str, optional): The typeface of the text in the object (see Draw.io for available fonts)
            fontSize (int, optional): The size of the text in the object in points
            align (str, optional): The horizontal alignment of the text in the object ('left', 'center', or 'right')
            verticalAlign (str, optional): The vertical alignment of the text in the object ('top', 'middle', 'bottom')
            textOpacity (int, optional): The opacity of the text in the object
            text_direction (str, optional): The direction to print the text ('vertical', 'horizontal')
            bold_font (bool, optional): Whether the text in the object should be bold
            italic_font (bool, optional): Whether the text in the object should be italic
            underline_font (bool, optional): Whether the text in the object should be underlined
            labelPosition (str, optional): The position of the object label ('left', 'center', or 'right')
            labelBackgroundColor (str, optional): The background color of the object label (#ffffff)
            labelBorderColor (str, optional): The border color of the object label (#ffffff)
        """
        super().__init__(**kwargs)
        self.style.attributes = [
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

        # Geometry
        self.geometry = ObjGeometry(parent_object=self)
        self.position = kwargs.get("position", (0, 0))
        self.size = kwargs.get("size", [120, 80])
        self.vertex = kwargs.get("vertex", 1)

        # TODO enumerate to fixed
        self.aspect = kwargs.get("aspect", None)

        # Content
        self.value = value

        # Style
        self.style.baseStyle = kwargs.get("baseStyle", None)

        self.style.rounded = kwargs.get("rounded", 0)
        self.style.html = kwargs.get("html", 1)
        self.style.whiteSpace = kwargs.get("whiteSpace", "wrap")
        self.style.fillColor = kwargs.get("fillColor", None)
        self.style.fontColor = kwargs.get("fontColor", None)
        self.style.opacity = kwargs.get("opacity", None)
        self.style.strokeColor = kwargs.get("strokeColor", None)
        self.style.glass = kwargs.get("glass", None)
        self.style.shadow = kwargs.get("shadow", None)
        self.style.comic = kwargs.get("comic", None)
        self.style.line_pattern = kwargs.get("line_pattern", "solid")

        self.style.fontFamily = kwargs.get("fontFamily", None)
        self.style.fontSize = kwargs.get("fontSize", None)
        self.style.align = kwargs.get("align", None)
        self.style.verticalAlign = kwargs.get("verticalAlign", None)
        self.style.labelPosition = kwargs.get("labelPosition", None)
        self.style.labelBackgroundColor = kwargs.get("labelBackgroundColor", None)
        self.style.labelBorderColor = kwargs.get("labelBorderColor", None)

        # These need to be enumerated
        self.style.text_direction = kwargs.get("text_direction", None)
        # This is actually horizontal. 0 means vertical text, 1 or not present
        # means horizontal

        self.style.textOpacity = kwargs.get("textOpacity", None)
        self.style.bold_font = kwargs.get("bold_font", False)
        self.style.italic_font = kwargs.get("italic_font", False)
        self.style.underline_font = kwargs.get("underline_font", False)

        self.out_edges = kwargs.get("out_edges", [])
        self.in_edges = kwargs.get("in_edges", [])

        self.xml_class = "mxCell"

        # TODO rework template object
        # if "template_object" in kwargs:
        #     self.template_object = kwargs.get("template_object")
        #     self._apply_style_from_template(self.template_object)

    def __repr__(self):
        if self.value != "":
            name_str = "{0} object with value {1}".format(
                self.__class__.__name__, self.value
            )
        else:
            name_str = "{0} object".format(self.__class__.__name__)
        return name_str

    def __str_(self):
        return self.__repr__()

    @classmethod
    def create_from_template_object(
        cls, template_object, value=None, position=None, page=None
    ):
        """Object can be instantiated from another object. This will initialize the Object with the same formatting, then set a new position and value.

        Args:
            template_object (Object): Another drawpyo Object to use as a template
            value (str, optional): The text contents of the object. Defaults to None.
            position (tuple, optional): The position where the object should be placed. Defaults to (0, 0).
            page (Page, optional): The Page object to place the object on. Defaults to None.

        Returns:
            Object: The newly created object
        """
        new_obj = cls(
            value=value,
            page=page,
            size=template_object.size,
            template_object=template_object,
        )
        if position is not None:
            new_obj.position = position
        if value is not None:
            new_obj.value = value
        return new_obj

    @classmethod
    def create_from_style_string(cls, style_string):
        """Objects can be instantiated from a style string. These strings are most easily found in the Draw.io app, by styling an object as desired then right-clicking and selecting "Edit Style". Copying that text into this function will generate an object styled the same.

        Args:
            style_string (str): A Draw.io generated style string.

        Returns:
            Object: An object formatted with the style string
        """
        cls.style.apply_style_from_string(style_string)
        return cls

    @classmethod
    def create_from_library(cls, library, obj_name):
        """This function generates a Object from a library. The library can either be custom imported from a TOML or the name of one of the built-in Draw.io libraries.

        Any keyword arguments that can be passed in to a Object creation can be passed into this function and it will format the base object. However, the styling in the library will overwrite that formatting.

        Args:
            library (str or dict): The library containing the object
            obj_name (str): The name of the object in the library to generate

        Returns:
            Object: An object with the style from the library
        """
        new_obj = cls()
        new_obj.format_as_library_object(library, obj_name)
        return new_obj

    def format_as_library_object(self, library, obj_name):
        """This function applies the style from a library to an existing object. The library can either be custom imported from a TOML or the name of one of the built-in Draw.io libraries.

        Args:
            library (str or dict): The library containing the object
            obj_name (str): The name of the object in the library to generate
        """
        #TODO make this function apply Base, Style, and maybe Geometry separately
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
                raise ValueError("Library {0} not in base_libraries".format(library))
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
            "parent": self.xml_parent_id,
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
            raise ValueError("{0} is not an allowed value of horizontal".format(value))

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
        """The font_style is a numeric format that corresponds to a combination of three other attributes: bold_font, italic_font, and underline_font. Any combination of them can be true."""
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
    def line_pattern(self):
        """Two properties are enumerated together into line_pattern: dashed and dashPattern. line_pattern simplifies this with an external database that contains the dropdown options from the Draw.io app then outputs the correct combination of dashed and dashPattern.

        However in some cases dashed and dashpattern need to be set individually, such as when formatting from a style string. In that case, the setters for those two attributes will disable the other.

        Returns:
            str: The line style
        """
        return self._line_pattern

    @line_pattern.setter
    def line_pattern(self, value):
        if value in line_styles.keys():
            self._line_pattern = value
        else:
            raise ValueError(
                "{0} is not an allowed value of line_pattern".format(value)
            )

    @property
    def dashed(self):
        """This is one of the properties that defines the line style. Along with dashPattern, it can be overriden by setting line_pattern or set directly.

        Returns:
            str: Whether the object stroke is dashed.
        """
        if self._line_pattern is None:
            return self._dashed
        else:
            return line_styles[self._line_pattern]

    @dashed.setter
    def dashed(self, value):
        self._line_pattern = None
        self._dashed = value

    @property
    def dashPattern(self):
        """This is one of the properties that defines the line style. Along with dashed, it can be overriden by setting line_pattern or set directly.

        Returns:
            str: What style the object stroke is dashed with.
        """
        if self._line_pattern is None:
            return self._dashed
        else:
            return line_styles[self._line_pattern]

    @dashPattern.setter
    def dashPattern(self, value):
        self._line_pattern = None
        self._dashPattern = value

    ###########################################################
    # Geometry properties
    ###########################################################

    # Position property
    @property
    def position(self):
        """The position of the object on the page. This is the top left corner. It's set with a tuple of ints, X and Y respectively.

        (X, Y)

        Returns:
            tuple: A tuple of ints describing the top left corner position of the object
        """
        return (self.geometry.x, self.geometry.y)

    @position.setter
    def position(self, value):
        self.geometry.x = value[0]
        self.geometry.y = value[1]

    @property
    def center_position(self):
        """The position of the object on the page. This is the center of the object. It's set with a tuple of ints, X and Y respectively.

        (X, Y)

        Returns:
            tuple: A tuple of ints describing the center position of the object
        """
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
        """The size of the object. It's set with a tuple of ints, width and height respectively.

        (width, height)

        Returns:
            tuple: A tuple of ints describing the size of the object
        """
        return (self.geometry.width, self.geometry.height)

    @size.setter
    def size(self, value):
        self.geometry.width = value[0]
        self.geometry.height = value[1]

    ###########################################################
    # Edge Tracking
    ###########################################################

    def add_out_edge(self, edge):
        """Add an edge out of the object. If an edge is created with this object set as the source this function will be called automatically.

        Args:
            edge (Edge): An Edge object originating at this object
        """
        self.out_edges.append(edge)

    def remove_out_edge(self, edge):
        """Remove an edge out of the object. If an edge linked to this object has the source changed or removed this function will be called automatically.

        Args:
            edge (Edge): An Edge object originating at this object
        """
        self.out_edges.remove(edge)

    def add_in_edge(self, edge):
        """Add an edge into the object. If an edge is created with this object set as the target this function will be called automatically.

        Args:
            edge (Edge): An Edge object ending at this object
        """
        self.in_edges.append(edge)

    def remove_in_edge(self, edge):
        """Remove an edge into the object. If an edge linked to this object has the target changed or removed this function will be called automatically.

        Args:
            edge (Edge): An Edge object ending at this object
        """
        self.in_edges.remove(edge)

    ###########################################################
    # XML Generation
    ###########################################################

    @property
    def xml(self):
        """
        Returns the XML object for the Object: the opening tag with the style attributes, the value, and the closing tag.

        Example:
        <class_name attribute_name=attribute_value>Text in object</class_name>

        Returns:
            str: A single XML tag containing the object name, style attributes, and a closer.
        """
        tag = self.xml_open_tag + "\n  " + self.geometry.xml + "\n" + self.xml_close_tag
        return tag


class BasicObject(Object):
    pass


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
    """This class allows objects to be grouped together. It then provides a number of geometry functions and properties to move the entire group around.

    Currently this object doesn't replicate any of the functionality of groups in the Draw.io app but it may be extended to have that capability in the future.
    """

    def __init__(self, **kwargs):
        self.objects = kwargs.get("objects", [])
        self.geometry = ObjGeometry()

    def add_object(self, object):
        """Adds one or more objects to the group and updates the geometry of the group.

        Args:
            object (Object or list): Object or list of objects to be added to the group
        """
        if not isinstance(object, list):
            object = [object]
        for o in object:
            if o not in self.objects:
                self.objects.append(o)
        self.update_geometry()

    def update_geometry(self):
        """Update the geometry of the group. This includes the left and top coordinates and the width and height of the entire group."""
        self.geometry.x = self.left
        self.geometry.y = self.top
        self.geometry.width = self.width
        self.geometry.height = self.height

    ###########################################################
    # Passive properties
    ###########################################################

    @property
    def left(self):
        """The leftmost X-coordinate of the objects in the group

        Returns:
            int: Left edge of the group
        """
        return min([obj.geometry.x for obj in self.objects])

    @property
    def right(self):
        """The rightmost X-coordinate of the objects in the group

        Returns:
            int: Right edge of the group
        """
        return max([obj.geometry.x + obj.geometry.width for obj in self.objects])

    @property
    def top(self):
        """The topmost Y-coordinate of the objects in the group

        Returns:
            int: Top edge of the group
        """
        return min([obj.geometry.y for obj in self.objects])

    @property
    def bottom(self):
        """The bottommost Y-coordinate of the objects in the group

        Returns:
            int: The bottom edge of the group
        """
        return max([obj.geometry.y + obj.geometry.height for obj in self.objects])

    @property
    def width(self):
        """The width of all the objects in the group

        Returns:
            int: Width of the group
        """
        return self.right - self.left

    @property
    def height(self):
        """The height of all the objects in the group

        Returns:
            int: Height of the group
        """
        return self.bottom - self.top

    @property
    def size(self):
        """The size of the group. Returns a tuple of ints, with the width and height.

        Returns:
            tuple: A tuple of ints (width, height)
        """
        return (self.width, self.height)

    ###########################################################
    # Position properties
    ###########################################################

    @property
    def center_position(self):
        """The center position of the group. Returns a tuple of ints, with the X and Y coordinate. When this property is set, the coordinates of every object in the group are updated.

        Returns:
            tuple: A tuple of ints (X, Y)
        """
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
        """The top left position of the group. Returns a tuple of ints, with the X and Y coordinate. When this property is set, the coordinates of every object in the group are updated.

        Returns:
            tuple: A tuple of ints (X, Y)
        """
        return (self.left, self.top)

    @position.setter
    def position(self, new_position):
        current_position = (self.left, self.top)
        delta_x = new_position[0] - current_position[0]
        delta_y = new_position[1] - current_position[1]
        for obj in self.objects:
            obj.position = (obj.geometry.x + delta_x, obj.geometry.y + delta_y)
        self.update_geometry()
