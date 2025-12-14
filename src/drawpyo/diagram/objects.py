from os import path
from typing import Optional, Dict, Any, List, Union, Tuple
from ..utils.logger import logger

from .base_diagram import (
    DiagramBase,
    Geometry,
    import_shape_database,
)
from .text_format import TextFormat
from ..utils.color_scheme import ColorScheme
from ..utils.standard_colors import StandardColor

__all__ = ["Object", "BasicObject", "Group", "object_from_library"]

general: Dict[str, Any] = import_shape_database(
    file_name=path.join("shape_libraries", "general.toml"), relative=True
)
flowchart: Dict[str, Any] = import_shape_database(
    file_name=path.join("shape_libraries", "flowchart.toml"), relative=True
)
infographics: Dict[str, Any] = import_shape_database(
    file_name=path.join("shape_libraries", "infographics.toml"), relative=True
)
line_styles: Dict[str, Any] = import_shape_database(
    file_name=path.join("formatting_database", "line_styles.toml"), relative=True
)

base_libraries: Dict[str, Dict[str, Any]] = {
    "general": general,
    "flowchart": flowchart,
    "infographics": infographics,
}

container: Dict[Optional[str], None] = {None: None, "vertical_container": None}


def import_shape_library(library_path: str, name: str) -> None:
    data: Dict[str, Any] = import_shape_database(filename=library_path)
    base_libraries[name] = data


def object_from_library(
    library: Union[str, Dict[str, Any]], obj_name: str, **kwargs: Any
) -> "Object":
    """This function generates an Object from a library. The library can either be custom imported from a TOML or the name of one of the built-in Draw.io libraries.

    Any keyword arguments that can be passed in to a Object creation can be passed into this function and it will format the base object. These keyword arguments will overwrite any attributes defined in the library.

    Args:
        library (str or dict): The library containing the object
        obj_name (str): The name of the object in the library to generate

    Returns:
        Object: An object with the style from the library
    """
    new_obj: Object = Object(**kwargs)
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

    def __init__(
        self, value: str = "", position: Tuple[int, int] = (0, 0), **kwargs: Any
    ) -> None:
        """A Object can be initialized with as many or as few of its styling attributes as is desired.

        Args:
            value (str, optional): The text to fill the object with. Defaults to "".
            position (tuple, optional): The position of the object in pixels, in (X, Y). Defaults to (0, 0).

        Keyword Args:
            aspect (optional): Aspect ratio handling. Defaults to None.
            autocontract (bool, optional): Whether to contract to fit the child objects. Defaults to False.
            autosize_margin (int, optional): What margin in pixels to leave around the child objects. Defaults to 20.
            autosize_to_children (bool, optional): Whether to autoexpand when child objects are added. Defaults to False.
            baseStyle (optional): Base style for the object. Defaults to None.
            children (list of Objects, optional): The subobjects to add to this object as a parent. Defaults to [].
            color_scheme (ColorScheme, optional): Bundled set of color specifications. Defaults to None.
            comic (bool, optional): Add comic styling to the object. Defaults to None.
            fillColor (Union[str, StandardColor], optional): The object fill color. Defaults to None.
            glass (bool, optional): Apply glass styling to the object. Defaults to None.
            height (int, optional): The height of the object in pixels. Defaults to 80.
            in_edges (list, optional): List of incoming edges to this object. Defaults to [].
            line_pattern (str, optional): The stroke style of the object. Defaults to "solid".
            opacity (int, optional): The object's opacity, 0-100. Defaults to None.
            out_edges (list, optional): List of outgoing edges from this object. Defaults to [].
            parent (Object, optional): The parent object (container, etc) of this object. Defaults to None.
            position_rel_to_parent (tuple, optional): The position of the object relative to the parent in pixels, in (X, Y).
            rounded (int or bool, optional): Whether to round the corners of the shape. Defaults to 0.
            shadow (bool, optional): Add a shadow to the object. Defaults to None.
            sketch (bool, optional): Add sketch styling to the object. Defaults to None.
            strokeColor (Union[str, StandardColor], optional): The object stroke color. Defaults to None.
            template_object (Object, optional): Another object to copy the style_attributes from. Defaults to None.
            text_format (TextFormat, optional): Formatting specifically around text. Defaults to TextFormat().
            vertex (int, optional): Vertex flag for the object. Defaults to 1.
            whiteSpace (str, optional): White space handling. Defaults to "wrap".
            width (int, optional): The width of the object in pixels. Defaults to 120.
        """
        super().__init__(**kwargs)
        self._style_attributes: List[str] = [
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

        self.geometry: Geometry = Geometry(parent_object=self)

        # Subobjecting
        # If there is a parent passed in, disable that parents
        # autoexpanding until position is set
        if "parent" in kwargs:
            parent: Object = kwargs.get("parent")
            old_parent_autosize: bool = parent.autosize_to_children
            parent.autoexpand = False
            self.parent: Optional[Object] = parent
        else:
            self._parent: Optional[Object] = None
        self.children: List[Object] = kwargs.get("children", [])
        self.autosize_to_children: bool = kwargs.get("autosize_to_children", False)
        self.autocontract: bool = kwargs.get("autocontract", False)
        self.autosize_margin: int = kwargs.get("autosize_margin", 20)

        # Geometry
        self.position: Optional[tuple] = position
        # Since the position is already set to either a passed in arg or the default this will
        # either override that default position or redundantly reset the position to the same value
        self.position_rel_to_parent: Optional[tuple] = kwargs.get(
            "position_rel_to_parent", position
        )
        self.width: int = kwargs.get("width", 120)
        self.height: int = kwargs.get("height", 80)
        self.vertex: int = kwargs.get("vertex", 1)

        # TODO enumerate to fixed
        self.aspect = kwargs.get("aspect", None)

        # Style
        self.baseStyle: Optional[str] = kwargs.get("baseStyle", None)

        self.rounded: Optional[bool] = kwargs.get("rounded", 0)
        self.whiteSpace: Optional[str] = kwargs.get("whiteSpace", "wrap")
        self.opacity: Optional[int] = kwargs.get("opacity", None)
        self.color_scheme: Optional[ColorScheme] = kwargs.get("color_scheme", None)
        self.strokeColor: Optional[Union[str, StandardColor]] = kwargs.get(
            "strokeColor"
        ) or (self.color_scheme.stroke_color if self.color_scheme else None)
        self.fillColor: Optional[Union[str, StandardColor]] = kwargs.get(
            "fillColor"
        ) or (self.color_scheme.fill_color if self.color_scheme else None)
        self.glass: Optional[bool] = kwargs.get("glass", None)
        self.shadow: Optional[bool] = kwargs.get("shadow", None)
        self.comic: Optional[bool] = kwargs.get("comic", None)
        self.sketch: Optional[bool] = kwargs.get("sketch", None)
        self.line_pattern: Optional[str] = kwargs.get("line_pattern", "solid")

        self.out_edges: List[Any] = kwargs.get("out_edges", [])
        self.in_edges: List[Any] = kwargs.get("in_edges", [])

        self.xml_class: str = "mxCell"

        if "template_object" in kwargs:
            self.template_object: Object = kwargs.get("template_object")
            self._apply_style_from_template(self.template_object)
            self.width = self.template_object.width
            self.height = self.template_object.height

        # Content
        self.text_format: Optional[TextFormat] = kwargs.get("text_format", TextFormat())
        if not self.text_format.fontColor and self.color_scheme:
            self.text_format.fontColor = self.color_scheme.font_color
        self.value: Optional[str] = value

        # If a parent was passed in, reactivate the parents autoexpanding and update it
        if "parent" in kwargs:
            self.parent.autosize_to_children = old_parent_autosize
            self.update_parent()

        logger.debug(f"🔲 Object created: {self.__repr__()}")

    def __repr__(self) -> str:
        """
        A more informative representation for debugging.
        """
        parts = []

        # Geometry
        parts.append(f"pos: {self.position}")
        parts.append(f"size: ({self.width}x{self.height})")

        # Parent info
        if getattr(self, "parent", None):
            parts.append(f"parent: {self.parent.__class__.__name__}")

        # Child count
        if getattr(self, "children", None):
            parts.append(f"children: {len(self.children)}")

        joined = " | ".join(parts)
        return f"{self.value} | {joined}"

    def __str__(self) -> str:
        return self.__repr__()

    def __delete__(self) -> None:
        self.page.remove_object(self)

    @classmethod
    def create_from_template_object(
        cls,
        template_object: "Object",
        value: Optional[str] = None,
        position: Optional[Tuple[int, int]] = None,
        page: Optional[Any] = None,
    ) -> "Object":
        """Object can be instantiated from another object. This will initialize the Object with the same formatting, then set a new position and value.

        Args:
            template_object (Object): Another drawpyo Object to use as a template
            value (str, optional): The text contents of the object. Defaults to None.
            position (tuple, optional): The position where the object should be placed. Defaults to (0, 0).
            page (Page, optional): The Page object to place the object on. Defaults to None.

        Returns:
            Object: The newly created object
        """
        new_obj: Object = cls(
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
    def create_from_style_string(cls, style_string: str) -> "Object":
        """Objects can be instantiated from a style string. These strings are most easily found in the Draw.io app, by styling an object as desired then right-clicking and selecting "Edit Style". Copying that text into this function will generate an object styled the same.

        Args:
            style_string (str): A Draw.io generated style string.

        Returns:
            Object: An object formatted with the style string
        """
        cls.apply_style_from_string(style_string)
        return cls

    @classmethod
    def create_from_library(
        cls, library: Union[str, Dict[str, Any]], obj_name: str
    ) -> "Object":
        """This function generates a Object from a library. The library can either be custom imported from a TOML or the name of one of the built-in Draw.io libraries.

        Any keyword arguments that can be passed in to a Object creation can be passed into this function and it will format the base object. However, the styling in the library will overwrite that formatting.

        Args:
            library (str or dict): The library containing the object
            obj_name (str): The name of the object in the library to generate

        Returns:
            Object: An object with the style from the library
        """
        new_obj: Object = cls()
        new_obj.format_as_library_object(library, obj_name)
        return new_obj

    def format_as_library_object(
        self, library: Union[str, Dict[str, Any]], obj_name: str
    ) -> None:
        """This function applies the style from a library to an existing object. The library can either be custom imported from a TOML or the name of one of the built-in Draw.io libraries.

        Args:
            library (str or dict): The library containing the object
            obj_name (str): The name of the object in the library to generate
        """
        if type(library) == str:
            if library in base_libraries:
                library_dict: Dict[str, Any] = base_libraries[library]
                if obj_name in library_dict:
                    obj_dict: Dict[str, Any] = library_dict[obj_name]
                    self.apply_attribute_dict(obj_dict)
                else:
                    raise ValueError(
                        "Object {0} not in Library {1}".format(obj_name, library)
                    )
            else:
                raise ValueError("Library {0} not in base_libraries".format(library))
        elif type(library) == dict:
            obj_dict: Dict[str, Any] = library[obj_name]
            self.apply_attribute_dict(obj_dict)
        else:
            raise ValueError("Unparseable libary passed in.")

    @property
    def attributes(self) -> Dict[str, Any]:
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
    def line_styles(self) -> Dict[str, Any]:
        return line_styles

    @property
    def container(self) -> Dict[Optional[str], None]:
        return container

    ###########################################################
    # Style properties
    ###########################################################

    @property
    def line_pattern(self) -> Optional[str]:
        """Two properties are enumerated together into line_pattern: dashed and dashPattern. line_pattern simplifies this with an external database that contains the dropdown options from the Draw.io app then outputs the correct combination of dashed and dashPattern.

        However in some cases dashed and dashpattern need to be set individually, such as when formatting from a style string. In that case, the setters for those two attributes will disable the other.

        Returns:
            str: The line style
        """
        return self._line_pattern

    @line_pattern.setter
    def line_pattern(self, value: str) -> None:
        if value in line_styles.keys():
            self._line_pattern = value
        else:
            raise ValueError(
                "{0} is not an allowed value of line_pattern".format(value)
            )

    @property
    def dashed(self) -> Optional[Union[bool, Any]]:
        """This is one of the properties that defines the line style. Along with dashPattern, it can be overriden by setting line_pattern or set directly.

        Returns:
            str: Whether the object stroke is dashed.
        """
        if self._line_pattern is None:
            return self._dashed
        else:
            return line_styles[self._line_pattern]

    @dashed.setter
    def dashed(self, value: bool) -> None:
        self._line_pattern = None
        self._dashed = value

    @property
    def dashPattern(self) -> Optional[Union[str, Any]]:
        """This is one of the properties that defines the line style. Along with dashed, it can be overriden by setting line_pattern or set directly.

        Returns:
            str: What style the object stroke is dashed with.
        """
        if self._line_pattern is None:
            return self._dashPattern
        else:
            return line_styles[self._line_pattern]

    @dashPattern.setter
    def dashPattern(self, value: str) -> None:
        self._line_pattern = None
        self._dashPattern = value

    ###########################################################
    # Geometry properties
    ###########################################################

    @property
    def width(self) -> int:
        """This property makes geometry.width available to the owning class for ease of access."""
        return self.geometry.width

    @width.setter
    def width(self, value: int) -> None:
        self.geometry.width = value
        self.update_parent()

    @property
    def height(self) -> int:
        """This property makes geometry.height available to the owning class for ease of access."""
        return self.geometry.height

    @height.setter
    def height(self, value: int) -> None:
        self.geometry.height = value
        self.update_parent()

    # Position property
    @property
    def position(self) -> Tuple[Union[int, float], Union[int, float]]:
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
    def position(self, value: Tuple[Union[int, float], Union[int, float]]) -> None:
        if self.parent is not None:
            self.geometry.x = value[0] - self.parent.position[0]
            self.geometry.y = value[1] - self.parent.position[1]
        else:
            self.geometry.x = value[0]
            self.geometry.y = value[1]
        self.update_parent()

    # Position Rel to Parent
    @property
    def position_rel_to_parent(self) -> Tuple[Union[int, float], Union[int, float]]:
        """The position of the object relative to its parent (container). If there's no parent this will be relative to the page. This is the top left corner. It's set with a tuple of ints, X and Y respectively.

        (X, Y)

        Returns:
            tuple: A tuple of ints describing the top left corner position of the object
        """
        return (self.geometry.x, self.geometry.y)

    @position_rel_to_parent.setter
    def position_rel_to_parent(
        self, value: Tuple[Union[int, float], Union[int, float]]
    ) -> None:
        self.geometry.x = value[0]
        self.geometry.y = value[1]
        self.update_parent()

    @property
    def center_position(self) -> Tuple[Union[int, float], Union[int, float]]:
        """The position of the object on the page. This is the center of the object. It's set with a tuple of ints, X and Y respectively.

        (X, Y)

        Returns:
            tuple: A tuple of ints describing the center position of the object
        """
        x: Union[int, float] = self.geometry.x + self.geometry.width / 2
        y: Union[int, float] = self.geometry.y + self.geometry.height / 2
        return (x, y)

    @center_position.setter
    def center_position(
        self, position: Tuple[Union[int, float], Union[int, float]]
    ) -> None:
        self.geometry.x = position[0] - self.geometry.width / 2
        self.geometry.y = position[1] - self.geometry.height / 2

    ###########################################################
    # Subobjects
    ###########################################################
    # TODO add to documentation

    @property
    def xml_parent_id(self) -> Union[int, Any]:
        if self.parent is not None:
            return self.parent.id
        return 1

    @property
    def parent(self) -> Optional["Object"]:
        """The parent object that owns this object. This is usually a container of some kind but can be any other object.

        Returns:
            Object: the parent object.
        """
        return self._parent

    @parent.setter
    def parent(self, value: Optional["Object"]) -> None:
        if isinstance(value, Object):
            # value.add_object(self)
            value.children.append(self)
            self.update_parent()
        self._parent = value

    def add_object(self, child_object: "Object") -> None:
        """Adds a child object to this object, sets the child objects parent, and autoexpands this object if set to.

        Args:
            child_object (Object): object to add as a child
        """
        child_object._parent = self  # Bypass the setter to prevent a loop
        self.children.append(child_object)
        if self.autosize_to_children:
            self.resize_to_children()

    def remove_object(self, child_object: "Object") -> None:
        """Removes a child object from this object, clears the child objects parent, and autoexpands this object if set to.

        Args:
            child_object (Object): object to remove as a child
        """
        child_object._parent = None  # Bypass the setter to prevent a loop
        self.children.remove(child_object)
        if self.autosize_to_children:
            self.resize_to_children()

    def update_parent(self) -> None:
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

    def resize_to_children(self) -> None:
        """If the object contains children (is a container, parent, etc) then expand the size and position to fit all of the children.

        By default this function will never shrink the size of the object, only expand it. The contract input can be set for that behavior.

        Args:
            contract (bool, optional): Contract the parent object to hug the children. Defaults to False.
        """
        # Get current extents
        if len(self.children) == 0:
            return
        if self.autocontract:
            topmost: Union[int, float] = 65536
            bottommost: Union[int, float] = -65536
            leftmost: Union[int, float] = 65536
            rightmost: Union[int, float] = -65536
        else:
            topmost: Union[int, float] = self.position[1]
            bottommost: Union[int, float] = self.position[1] + self.height
            leftmost: Union[int, float] = self.position[0]
            rightmost: Union[int, float] = self.position[0] + self.width

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

    def move_wo_children(
        self, position: Tuple[Union[int, float], Union[int, float]]
    ) -> None:
        """Move the parent object relative to the page without moving the children relative to the page.

        Args:
            position (Tuple of Ints): The target position for the parent object.
        """
        # Disable autoexpand to avoid recursion from child_objects
        # attempting to update their autoexpanding parent upon a move
        old_autoexpand: bool = self.autosize_to_children
        self.autosize_to_children = False

        # Move children to counter upcoming parent move
        pos_delta: List[Union[int, float]] = [
            old_pos - new_pos for old_pos, new_pos in zip(self.position, position)
        ]
        for child_object in self.children:
            child_object.position = (
                child_object.position[0] + pos_delta[0],
                child_object.position[1] + pos_delta[1],
            )

        # Set new position and re-enable autoexpand
        self.position = position
        self.autosize_to_children = old_autoexpand

    ###########################################################
    # Edge Tracking
    ###########################################################

    def add_out_edge(self, edge: Any) -> None:
        """Add an edge out of the object. If an edge is created with this object set as the source this function will be called automatically.

        Args:
            edge (Edge): An Edge object originating at this object
        """
        self.out_edges.append(edge)

    def remove_out_edge(self, edge: Any) -> None:
        """Remove an edge out of the object. If an edge linked to this object has the source changed or removed this function will be called automatically.

        Args:
            edge (Edge): An Edge object originating at this object
        """
        self.out_edges.remove(edge)

    def add_in_edge(self, edge: Any) -> None:
        """Add an edge into the object. If an edge is created with this object set as the target this function will be called automatically.

        Args:
            edge (Edge): An Edge object ending at this object
        """
        self.in_edges.append(edge)

    def remove_in_edge(self, edge: Any) -> None:
        """Remove an edge into the object. If an edge linked to this object has the target changed or removed this function will be called automatically.

        Args:
            edge (Edge): An Edge object ending at this object
        """
        self.in_edges.remove(edge)

    ###########################################################
    # XML Generation
    ###########################################################

    @property
    def xml(self) -> str:
        """
        Returns the XML object for the Object: the opening tag with the style attributes, the value, and the closing tag.

        Example:
        <class_name attribute_name=attribute_value>Text in object</class_name>

        Returns:
            str: A single XML tag containing the object name, style attributes, and a closer.
        """
        tag: str = (
            self.xml_open_tag + "\n  " + self.geometry.xml + "\n" + self.xml_close_tag
        )
        return tag


class BasicObject(Object):
    pass


class Group:
    """This class allows objects to be grouped together. It then provides a number of geometry functions and properties to move the entire group around.

    Currently this object doesn't replicate any of the functionality of groups in the Draw.io app but it may be extended to have that capability in the future.
    """

    def __init__(self, **kwargs: Any) -> None:
        self.objects: List[Object] = kwargs.get("objects", [])
        self.geometry: Geometry = Geometry()

    def add_object(self, object: Union[Object, List[Object]]) -> None:
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

    def update_geometry(self) -> None:
        """Update the geometry of the group. This includes the left and top coordinates and the width and height of the entire group."""
        self.geometry.x = self.left
        self.geometry.y = self.top
        self.geometry.width = self.width
        self.geometry.height = self.height

    ###########################################################
    # Passive properties
    ###########################################################

    @property
    def left(self) -> Union[int, float]:
        """The leftmost X-coordinate of the objects in the group

        Returns:
            int: Left edge of the group
        """
        return min([obj.geometry.x for obj in self.objects])

    @property
    def right(self) -> Union[int, float]:
        """The rightmost X-coordinate of the objects in the group

        Returns:
            int: Right edge of the group
        """
        return max([obj.geometry.x + obj.geometry.width for obj in self.objects])

    @property
    def top(self) -> Union[int, float]:
        """The topmost Y-coordinate of the objects in the group

        Returns:
            int: Top edge of the group
        """
        return min([obj.geometry.y for obj in self.objects])

    @property
    def bottom(self) -> Union[int, float]:
        """The bottommost Y-coordinate of the objects in the group

        Returns:
            int: The bottom edge of the group
        """
        return max([obj.geometry.y + obj.geometry.height for obj in self.objects])

    @property
    def width(self) -> Union[int, float]:
        """The width of all the objects in the group

        Returns:
            int: Width of the group
        """
        return self.right - self.left

    @property
    def height(self) -> Union[int, float]:
        """The height of all the objects in the group

        Returns:
            int: Height of the group
        """
        return self.bottom - self.top

    @property
    def size(self) -> Tuple[Union[int, float], Union[int, float]]:
        """The size of the group. Returns a tuple of ints, with the width and height.

        Returns:
            tuple: A tuple of ints (width, height)
        """
        return (self.width, self.height)

    ###########################################################
    # Position properties
    ###########################################################

    def _move_by_delta(
        self, delta_x: Union[int, float], delta_y: Union[int, float]
    ) -> None:
        """Apply position delta to all objects in the group.

        Args:
            delta_x: Horizontal offset to apply
            delta_y: Vertical offset to apply
        """
        for obj in self.objects:
            obj.position = (obj.geometry.x + delta_x, obj.geometry.y + delta_y)
        self.update_geometry()

    @property
    def center_position(self) -> Tuple[Union[int, float], Union[int, float]]:
        """The center position of the group. Returns a tuple of ints, with the X and Y coordinate. When this property is set, the coordinates of every object in the group are updated.

        Returns:
            tuple: A tuple of ints (X, Y)
        """
        return (self.left + self.width / 2, self.top + self.height / 2)

    @center_position.setter
    def center_position(
        self, new_center: Tuple[Union[int, float], Union[int, float]]
    ) -> None:
        delta_x = new_center[0] - self.center_position[0]
        delta_y = new_center[1] - self.center_position[1]
        self._move_by_delta(delta_x, delta_y)

    @property
    def position(self) -> Tuple[Union[int, float], Union[int, float]]:
        """The top left position of the group. Returns a tuple of ints, with the X and Y coordinate. When this property is set, the coordinates of every object in the group are updated.

        Returns:
            tuple: A tuple of ints (X, Y)
        """
        return (self.left, self.top)

    @position.setter
    def position(
        self, new_position: Tuple[Union[int, float], Union[int, float]]
    ) -> None:
        delta_x = new_position[0] - self.position[0]
        delta_y = new_position[1] - self.position[1]
        self._move_by_delta(delta_x, delta_y)
