from os import path

from .base_diagram import (
    DiagramBase,
    Geometry,
    import_shape_database,
    style_str_from_dict,
)
from .text_format import TextFormat

__all__ = ["Object", "BasicObject", "Group", "object_from_library"]

general = import_shape_database(
    file_name=path.join("shape_libraries", "general.toml"), relative=True
)
flowchart = import_shape_database(
    file_name=path.join("shape_libraries", "flowchart.toml"), relative=True
)
line_styles = import_shape_database(
    file_name=path.join("formatting_database", "line_styles.toml"), relative=True
)

base_libraries = {
    "general": general,
    "flowchart": flowchart,
}

container = {None: None, "vertical_container": None}


def import_shape_library(library_path, name):
    data = import_shape_database(filename=library_path)
    base_libraries[name] = data


def object_from_library(library, obj_name, **kwargs):
    """This function generates an Object from a library. The library can either be custom imported from a TOML or the name of one of the built-in Draw.io libraries.

    Any keyword arguments that can be passed in to a Object creation can be passed into this function and it will format the base object. These keyword arguments will overwrite any attributes defined in the library.

    Args:
        library (str or dict): The library containing the object
        obj_name (str): The name of the object in the library to generate

    Returns:
        Object: An object with the style from the library
    """
    new_obj = Object(**kwargs)
    new_obj.format_as_library_object(library, obj_name)
    new_obj.apply_attribute_dict(kwargs)
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

    def __init__(self, value="", position=(0, 0), **kwargs):
        """A Object can be initialized with as many or as few of its styling attributes as is desired.

        Args:
            value (str, optional): The text to fill the object with. Defaults to "".
            position (tuple, optional): The position of the object in pixels, in (X, Y). Defaults to (0, 0).

        Keyword Args:
            position_rel_to_parent (tuple, optional): The position of the object relative to the parent in pixels, in (X, Y). # TODO document
            width (int, optional): The width of the object in pixels. Defaults to 120.
            height (int, optional): The height of the object in pixels. Defaults to 80.
            parent (Object, optional): The parent object (container, etc) of this object. Defaults to None. # TODO document
            children (array of Objects, optional): The subobjects to add to this object as a parent. Defaults to []. # TODO document
            autosize_to_children (bool, optional): Whether to autoexpand when child objects are added. Defaults to false. # TODO document
            autocontract (bool, optional): Whether to contract to fit the child objects. Defaults to false.
            autosize_margin (int, optional): What margin in pixels to leave around the child objects. Defaults to 20px. # TODO document
            template_object (Object, optional): Another object to copy the style_attributes from
            aspect # TODO ?
            rounded (bool, optional): Whether to round the corners of the shape
            whiteSpace (str, optional): white space
            fillColor (str, optional): The object fill color in a hex color code (#ffffff)
            opacity  (int, optional): The object's opacity, 0-100
            strokeColor: The object stroke color in a hex color code (#ffffff)
            glass (bool, optional): Apply glass styling to  the object
            shadow (bool, optional): Add a shadow to the object
            sketch (bool, optional): Add sketch styling to the object
            comic (bool, optional): Add comic styling to the object
            line_pattern (str, optional): The stroke style of the object.
        """
        super().__init__(**kwargs)
        self._style_attributes = [
            "whiteSpace",
            "rounded",
            "fillColor",
            "strokeColor",
            "glass",
            "shadow",
            "comic",
            "sketch",
            "opacity",
            "dashed",
        ]

        self.geometry = Geometry(parent_object=self)

        # Subobjecting
        # If there is a parent passed in, disable that parents
        # autoexpanding until position is set
        if "parent" in kwargs:
            parent = kwargs.get("parent")
            old_parent_autosize = parent.autosize_to_children
            parent.autoexpand = False
            self.parent = parent
        else:
            self.parent = None
        self.children = kwargs.get("children", [])
        self.autosize_to_children = kwargs.get("autosize_to_children", False)
        self.autocontract = kwargs.get("autocontract", False)
        self.autosize_margin = kwargs.get("autosize_margin", 20)

        # Geometry
        self.position = position
        # Since the position is already set to either a passed in arg or the default this will
        # either override that default position or redundantly reset the position to the same value
        self.position_rel_to_parent = kwargs.get("position_rel_to_parent", position)
        self.width = kwargs.get("width", 120)
        self.height = kwargs.get("height", 80)
        self.vertex = kwargs.get("vertex", 1)

        # TODO enumerate to fixed
        self.aspect = kwargs.get("aspect", None)

        # Content
        self.text_format = kwargs.get("text_format", TextFormat())
        self.value = value

        # Style
        self.baseStyle = kwargs.get("baseStyle", None)

        self.rounded = kwargs.get("rounded", 0)
        self.whiteSpace = kwargs.get("whiteSpace", "wrap")
        self.opacity = kwargs.get("opacity", None)
        self.strokeColor = kwargs.get("strokeColor", None)
        self.fillColor = kwargs.get("fillColor", None)
        self.glass = kwargs.get("glass", None)
        self.shadow = kwargs.get("shadow", None)
        self.comic = kwargs.get("comic", None)
        self.sketch = kwargs.get("sketch", None)
        self.line_pattern = kwargs.get("line_pattern", "solid")

        self.out_edges = kwargs.get("out_edges", [])
        self.in_edges = kwargs.get("in_edges", [])

        self.xml_class = "mxCell"

        if "template_object" in kwargs:
            self.template_object = kwargs.get("template_object")
            self._apply_style_from_template(self.template_object)
            self.width = self.template_object.width
            self.height = self.template_object.height

        # If a parent was passed in, reactivate the parents autoexpanding and update it
        if "parent" in kwargs:
            self.parent.autosize_to_children = old_parent_autosize
            self.update_parent()

    def __repr__(self):
        if self.value != "":
            name_str = "{0} object with value {1}".format(
                self.__class__.__name__, self.value
            )
        else:
            name_str = "{0} object".format(self.__class__.__name__)
        return name_str

    def __str__(self):
        return self.__repr__()
    
    def __delete__(self):
        self.page.remove_object(self)

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
            width=template_object.width,
            height=template_object.height,
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
        cls.apply_style_from_string(style_string)
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
    def container(self):
        return container

    ###########################################################
    # Style properties
    ###########################################################

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

    @property
    def width(self):
        """This property makes geometry.width available to the owning class for ease of access."""
        return self.geometry.width

    @width.setter
    def width(self, value):
        self.geometry.width = value
        self.update_parent()

    @property
    def height(self):
        """This property makes geometry.height available to the owning class for ease of access."""
        return self.geometry.height

    @height.setter
    def height(self, value):
        self.geometry.height = value
        self.update_parent()

    # Position property
    @property
    def position(self):
        """The position of the object on the page. This is the top left corner. It's set with a tuple of ints, X and Y respectively.

        (X, Y)

        Returns:
            tuple: A tuple of ints describing the top left corner position of the object
        """
        if self.parent is not None:
            return (
                self.geometry.x + self.parent.position[0],
                self.geometry.y + self.parent.position[1],
            )
        return (self.geometry.x, self.geometry.y)

    @position.setter
    def position(self, value):
        if self.parent is not None:
            self.geometry.x = value[0] - self.parent.position[0]
            self.geometry.y = value[1] - self.parent.position[1]
        else:
            self.geometry.x = value[0]
            self.geometry.y = value[1]
        self.update_parent()

    # Position Rel to Parent
    @property
    def position_rel_to_parent(self):
        """The position of the object relative to its parent (container). If there's no parent this will be relative to the page. This is the top left corner. It's set with a tuple of ints, X and Y respectively.

        (X, Y)

        Returns:
            tuple: A tuple of ints describing the top left corner position of the object
        """
        return (self.geometry.x, self.geometry.y)

    @position_rel_to_parent.setter
    def position_rel_to_parent(self, value):
        self.geometry.x = value[0]
        self.geometry.y = value[1]
        self.update_parent()

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

    ###########################################################
    # Subobjects
    ###########################################################
    # TODO add to documentation

    @property
    def xml_parent_id(self):
        if self.parent is not None:
            return self.parent.id
        return 1

    @property
    def parent(self):
        """The parent object that owns this object. This is usually a container of some kind but can be any other object.

        Returns:
            Object: the parent object.
        """
        return self._parent

    @parent.setter
    def parent(self, value):
        if isinstance(value, Object):
            # value.add_object(self)
            value.children.append(self)
            self.update_parent()
        self._parent = value

    def add_object(self, child_object):
        """Adds a child object to this object, sets the child objects parent, and autoexpands this object if set to.

        Args:
            child_object (Object): object to add as a child
        """
        child_object._parent = self  # Bypass the setter to prevent a loop
        self.children.append(child_object)
        if self.autosize_to_children:
            self.resize_to_children()

    def remove_object(self, child_object):
        """Removes a child object from this object, clears the child objects parent, and autoexpands this object if set to.

        Args:
            child_object (Object): object to remove as a child
        """
        child_object._parent = None  # Bypass the setter to prevent a loop
        self.children.remove(child_object)
        if self.autosize_to_children:
            self.resize_to_children()

    def update_parent(self):
        """If a parent object is set and the parent is set to autoexpand, then autoexpand it."""
        # This function needs to be callable prior to the parent being set during init,
        # hence the hasattr() check.
        if (
            hasattr(self, "_parent")
            and self.parent is not None
            and self.parent.autosize_to_children
        ):
            # if the parent is autoexpanding, call the autoexpand function
            self.parent.resize_to_children()

    def resize_to_children(self):
        """If the object contains children (is a container, parent, etc) then expand the size and position to fit all of the children.

        By default this function will never shrink the size of the object, only expand it. The contract input can be set for that behavior.

        Args:
            contract (bool, optional): Contract the parent object to hug the children. Defaults to False.
        """
        # Get current extents
        if len(self.children) == 0:
            return
        if self.autocontract:
            topmost = 65536
            bottommost = -65536
            leftmost = 65536
            rightmost = -65536
        else:
            topmost = self.position[1]
            bottommost = self.position[1] + self.height
            leftmost = self.position[0]
            rightmost = self.position[0] + self.width

        # Check all child objects for extents
        for child_object in self.children:
            topmost = min(topmost, child_object.position[1] - self.autosize_margin)
            bottommost = max(
                bottommost,
                child_object.position[1] + child_object.height + self.autosize_margin,
            )
            leftmost = min(leftmost, child_object.position[0] - self.autosize_margin)
            rightmost = max(
                rightmost,
                child_object.position[0] + child_object.width + self.autosize_margin,
            )

        # Set self extents to furthest positions
        self.move_wo_children((leftmost, topmost))
        self.width = rightmost - leftmost
        self.height = bottommost - topmost

    def move_wo_children(self, position):
        """Move the parent object relative to the page without moving the children relative to the page.

        Args:
            position (Tuple of Ints): The target position for the parent object.
        """
        # Disable autoexpand to avoid recursion from child_objects
        # attempting to update their autoexpanding parent upon a move
        old_autoexpand = self.autosize_to_children
        self.autosize_to_children = False

        # Move children to counter upcoming parent move
        pos_delta = [
            old_pos - new_pos for old_pos, new_pos in zip(self.position, position)
        ]
        for child_object in self.children:
            child_object.position = [
                curr_pos + container_move
                for curr_pos, container_move in zip(child_object.position, pos_delta)
            ]

        # Set new position and re-enable autoexpand
        self.position = position
        self.autosize_to_children = old_autoexpand

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


class Group:
    """This class allows objects to be grouped together. It then provides a number of geometry functions and properties to move the entire group around.

    Currently this object doesn't replicate any of the functionality of groups in the Draw.io app but it may be extended to have that capability in the future.
    """

    def __init__(self, **kwargs):
        self.objects = kwargs.get("objects", [])
        self.geometry = Geometry()

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
