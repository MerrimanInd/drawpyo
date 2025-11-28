from os import path
from typing import Optional, Dict, Any, List, Union, Tuple
from ..utils.logger import logger

from .base_diagram import (
    DiagramBase,
    import_shape_database,
    style_str_from_dict,
    color_input_check,
    width_input_check,
)
from .text_format import TextFormat
from ..utils.color_scheme import ColorScheme
from ..utils.standard_colors import StandardColor

__all__ = ["Edge", "BasicEdge", "EdgeGeometry", "EdgeLabel", "Point"]

data: Dict[str, Any] = import_shape_database(
    file_name=path.join("formatting_database", "edge_styles.toml"), relative=True
)

connection_db: Dict[Optional[str], Dict[str, Any]] = data["connection"]
connection_db[None] = {"shape": ""}

pattern_db: Dict[Optional[str], Dict[str, Any]] = data["pattern"]
pattern_db[None] = {}

waypoints_db: Dict[Optional[str], Dict[str, Any]] = data["waypoints"]
waypoints_db[None] = {}

line_ends_db: Dict[Optional[str], Dict[str, bool]] = data["line_ends"]
line_ends_db[None] = {"fillable": False}
line_ends_db[""] = {"fillable": False}
line_ends_db["none"] = {"fillable": False}


###########################################################
# Edges
###########################################################


class Edge(DiagramBase):
    """The Edge class is the simplest class for defining an edge or an arrow in a Draw.io diagram.

    The three primary styling inputs are the waypoints, connections, and pattern. These are how edges are styled in the Draw.io app, with dropdown menus for each one. But it's not how the style string is assembled in the XML. To abstract this, the Edge class loads a database called edge_styles.toml. The database maps the options in each dropdown to the style strings they correspond to. The Edge class then assembles the style strings on export.

    More information about edges are in the Usage documents at [Usage - Edges](../../usage/edges).
    """

    def __init__(self, **kwargs: Any) -> None:
        """Edges can be initialized with almost all styling parameters as args.
        See [Usage - Edges](../../usage/edges) for more information and the options for each parameter.

        Args:
            source (DiagramBase): The Draw.io object that the edge originates from
            target (DiagramBase): The Draw.io object that the edge points to
            label (str): The text to place on the edge.
            label_position (float): Where along the edge the label is positioned. -1 is the source, 1 is the target, 0 is the center
            label_offset (int): How far the label is offset away from the axis of the edge in pixels
            waypoints (str): How the edge should be styled in Draw.io
            connection (str): What type of style the edge should be rendered with
            pattern (str): How the line of the edge should be rendered
            shadow (bool, optional): Add a shadow to the edge
            rounded (bool): Whether the corner of the line should be rounded
            flowAnimation (bool): Add a marching ants animation along the edge
            sketch (bool, optional): Add sketch styling to the edge
            line_end_target (str): What graphic the edge should be rendered with at the target
            line_end_source (str): What graphic the edge should be rendered with at the source
            endFill_target (boolean): Whether the target graphic should be filled
            endFill_source (boolean): Whether the source graphic should be filled
            endSize (int): The size of the end arrow in points
            startSize (int): The size of the start arrow in points
            jettySize (str or int): Length of the straight sections at the end of the edge. "auto" or a number
            targetPerimeterSpacing (int): The negative or positive spacing between the target and end of the edge (points)
            sourcePerimeterSpacing (int): The negative or positive spacing between the source and end of the edge (points)
            entryX (int): From where along the X axis on the source object the edge originates (0-1)
            entryY (int): From where along the Y axis on the source object the edge originates (0-1)
            entryDx (int): Applies an offset in pixels to the X axis entry point
            entryDy (int): Applies an offset in pixels to the Y axis entry point
            exitX (int): From where along the X axis on the target object the edge originates (0-1)
            exitY (int): From where along the Y axis on the target object the edge originates (0-1)
            exitDx (int): Applies an offset in pixels to the X axis exit point
            exitDy (int): Applies an offset in pixels to the Y axis exit point
            color_scheme (ColorScheme, optional): Bundled set of color specifications. Defaults to None.
            strokeColor (str): The color of the border of the edge ('none', 'default', or hex color code)
            strokeWidth (int): The width of the border of the the edge within range (1-999)
            fillColor (str): The color of the fill of the edge ('none', 'default', or hex color code)
            jumpStyle (str): The line jump style ('arc', 'gap', 'sharp', 'line')
            jumpSize (int): The size of the line jumps in points.
            opacity (int): The opacity of the edge (0-100)
        """
        super().__init__(**kwargs)
        self.xml_class: str = "mxCell"

        # Style
        self.color_scheme: Optional[ColorScheme] = kwargs.get("color_scheme", None)
        self.text_format: Optional[TextFormat] = kwargs.get("text_format", TextFormat())
        if not self.text_format.fontColor and self.color_scheme:
            self.text_format.fontColor = self.color_scheme.font_color
        self.waypoints: Optional[str] = kwargs.get("waypoints", "orthogonal")
        self.connection: Optional[str] = kwargs.get("connection", "line")
        self.pattern: Optional[str] = kwargs.get("pattern", "solid")
        self.opacity: Optional[int] = kwargs.get("opacity", None)
        self.strokeWidth: Optional[int] = kwargs.get("strokeWidth", None)
        self.strokeColor: Optional[Union[str, StandardColor]] = kwargs.get(
            "stroke_color"
        ) or (self.color_scheme.stroke_color if self.color_scheme else None)
        self.fillColor: Optional[Union[str, StandardColor]] = kwargs.get(
            "fill_color"
        ) or (self.color_scheme.fill_color if self.color_scheme else None)

        # Line end
        self.line_end_target: Optional[str] = kwargs.get("line_end_target", None)
        self.line_end_source: Optional[str] = kwargs.get("line_end_source", None)
        self.endFill_target: bool = kwargs.get("endFill_target", False)
        self.endFill_source: bool = kwargs.get("endFill_source", False)
        self.endSize: Optional[int] = kwargs.get("endSize", None)
        self.startSize: Optional[int] = kwargs.get("startSize", None)

        self.rounded: int = kwargs.get("rounded", 0)
        self.sketch: Optional[bool] = kwargs.get("sketch", None)
        self.shadow: Optional[bool] = kwargs.get("shadow", None)
        self.flowAnimation: Optional[bool] = kwargs.get("flowAnimation", None)

        self._jumpStyle: Optional[str] = None
        self.jumpStyle = kwargs.get("jumpStyle", None)
        self.jumpSize: Optional[int] = kwargs.get("jumpSize", None)

        # Connection and geometry
        self.jettySize: Union[str, int] = kwargs.get("jettySize", "auto")
        self.geometry: EdgeGeometry = EdgeGeometry()
        self.edge: int = kwargs.get("edge", 1)
        self.targetPerimeterSpacing: Optional[int] = kwargs.get(
            "targetPerimeterSpacing", None
        )
        self.sourcePerimeterSpacing: Optional[int] = kwargs.get(
            "sourcePerimeterSpacing", None
        )
        self._source: Optional[DiagramBase] = None
        self.source = kwargs.get("source", None)
        self._target: Optional[DiagramBase] = None
        self.target = kwargs.get("target", None)
        self.entryX: Optional[float] = kwargs.get("entryX", None)
        self.entryY: Optional[float] = kwargs.get("entryY", None)
        self.entryDx: Optional[int] = kwargs.get("entryDx", None)
        self.entryDy: Optional[int] = kwargs.get("entryDy", None)
        self.exitX: Optional[float] = kwargs.get("exitX", None)
        self.exitY: Optional[float] = kwargs.get("exitY", None)
        self.exitDx: Optional[int] = kwargs.get("exitDx", None)
        self.exitDy: Optional[int] = kwargs.get("exitDy", None)

        # Label
        self.label: Optional[str] = kwargs.get("label", None)
        self.edge_axis_offset: Optional[int] = kwargs.get("edge_offset", None)
        self.label_offset: Optional[int] = kwargs.get("label_offset", None)
        self.label_position: Optional[float] = kwargs.get("label_position", None)

        logger.debug(f"➡️ Edge created: {self.__repr__()}")

    def __repr__(self) -> str:
        """
        A concise and informative representation of the edge for debugging.
        """
        cls = self.__class__.__name__
        parts = []

        # Source/Target
        parts.append(f"source: '{self.source.value if self.source else None}'")
        parts.append(f"target: '{self.target.value if self.target else None}'")

        # Label
        if self.label:
            parts.append(f"label={self.label!r}")

        # Entry/Exit geometry (only show if anything is set)
        geom_parts = []
        for attr in (
            "entryX",
            "entryY",
            "entryDx",
            "entryDy",
            "exitX",
            "exitY",
            "exitDx",
            "exitDy",
        ):
            val = getattr(self, attr, None)
            if val not in (None, 0):
                geom_parts.append(f"{attr}={val}")
        if geom_parts:
            parts.append("geom={" + ", ".join(geom_parts) + "}")

        return f"{cls}(" + ", ".join(parts) + ")"

    def __str__(self) -> str:
        return self.__repr__()

    def remove(self) -> None:
        """This function removes references to the Edge from its source and target objects then deletes the Edge."""
        if self.source is not None:
            self.source.remove_out_edge(self)
        if self.target is not None:
            self.target.remove_in_edge(self)
        del self

    @property
    def attributes(self) -> Dict[str, Any]:
        """Returns the XML attributes to be added to the tag for the object

        Returns:
            dict: Dictionary of object attributes and their values
        """
        base_attr_dict: Dict[str, Any] = {
            "id": self.id,
            "style": self.style,
            "edge": self.edge,
            "parent": self.xml_parent_id,
            "source": self.source_id,
            "target": self.target_id,
        }
        if self.value is not None:
            base_attr_dict["value"] = self.value
        return base_attr_dict

    ###########################################################
    # Source and Target Linking
    ###########################################################

    # Source
    @property
    def source(self) -> Optional[DiagramBase]:
        """The source object of the edge. Automatically adds the edge to the object when set and removes it when deleted.

        Returns:
            BaseDiagram: source object of the edge
        """
        return self._source

    @source.setter
    def source(self, f: Optional[DiagramBase]) -> None:
        if f is not None:
            f.add_out_edge(self)
            self._source = f

    @source.deleter
    def source(self) -> None:
        self._source.remove_out_edge(self)
        self._source = None

    @property
    def source_id(self) -> Union[int, Any]:
        """The ID of the source object or 1 if no source is set

        Returns:
            int: Source object ID
        """
        if self.source is not None:
            return self.source.id
        else:
            return 1

    # Target
    @property
    def target(self) -> Optional[DiagramBase]:
        """The target object of the edge. Automatically adds the edge to the object when set and removes it when deleted.

        Returns:
            BaseDiagram: target object of the edge
        """
        return self._target

    @target.setter
    def target(self, f: Optional[DiagramBase]) -> None:
        if f is not None:
            f.add_in_edge(self)
            self._target = f

    @target.deleter
    def target(self) -> None:
        self._target.remove_in_edge(self)
        self._target = None

    @property
    def target_id(self) -> Union[int, Any]:
        """The ID of the target object or 1 if no target is set

        Returns:
            int: Target object ID
        """
        if self.target is not None:
            return self.target.id
        else:
            return 1

    def add_point(self, x: int, y: int) -> None:
        """Add a point to the edge

        Args:
            x (int): The x coordinate of the point in pixels
            y (int): The y coordinate of the point in pixels
        """
        self.geometry.points.append(Point(x=x, y=y))

    def add_point_pos(self, position: Tuple[int, int]) -> None:
        """Add a point to the edge by position tuple

        Args:
            position (tuple): A tuple of ints describing the x and y coordinates in pixels
        """
        self.geometry.points.append(Point(x=position[0], y=position[1]))

    ###########################################################
    # Style properties
    ###########################################################

    @property
    def style_attributes(self) -> List[str]:
        """The style attributes to add to the style tag in the XML

        Returns:
            list: A list of style attributes
        """
        return [
            "rounded",
            "sketch",
            "shadow",
            "flowAnimation",
            "jettySize",
            "entryX",
            "entryY",
            "entryDx",
            "entryDy",
            "exitX",
            "exitY",
            "exitDx",
            "exitDy",
            "startArrow",
            "endArrow",
            "startFill",
            "endFill",
            "strokeColor",
            "strokeWidth",
            "fillColor",
            "jumpStyle",
            "jumpSize",
            "targetPerimeterSpacing",
            "sourcePerimeterSpacing",
            "endSize",
            "startSize",
            "opacity",
        ]

    @property
    def baseStyle(self) -> Optional[str]:
        """Generates the baseStyle string from the connection style, waypoint style, pattern style, and base style string.

        Returns:
            str: Concatenated baseStyle string
        """
        style_str: List[str] = []
        connection_style: Optional[str] = style_str_from_dict(
            connection_db[self.connection]
        )
        if connection_style is not None and connection_style != "":
            style_str.append(connection_style)

        waypoint_style: Optional[str] = style_str_from_dict(
            waypoints_db[self.waypoints]
        )
        if waypoint_style is not None and waypoint_style != "":
            style_str.append(waypoint_style)

        pattern_style: Optional[str] = style_str_from_dict(pattern_db[self.pattern])
        if pattern_style is not None and pattern_style != "":
            style_str.append(pattern_style)

        if len(style_str) == 0:
            return None
        else:
            return ";".join(style_str)

    @property
    def startArrow(self) -> Optional[str]:
        """What graphic the edge should be rendered with at the source

        Returns:
            str: The source edge graphic
        """
        return self.line_end_source

    @startArrow.setter
    def startArrow(self, val: Optional[str]) -> None:
        self.line_end_source = val

    @property
    def startFill(self) -> Optional[bool]:
        """Whether the graphic at the source should be filled

        Returns:
            bool: The source graphic fill
        """
        if line_ends_db[self.line_end_source]["fillable"]:
            return self.endFill_source
        else:
            return None

    @property
    def endArrow(self) -> Optional[str]:
        """What graphic the edge should be rendered with at the target

        Returns:
            str: The target edge graphic
        """
        return self.line_end_target

    @endArrow.setter
    def endArrow(self, val: Optional[str]) -> None:
        self.line_end_target = val

    @property
    def endFill(self) -> Optional[bool]:
        """Whether the graphic at the target should be filled

        Returns:
            bool: The target graphic fill
        """
        if line_ends_db[self.line_end_target]["fillable"]:
            return self.endFill_target
        else:
            return None

    # Base Line Style

    # Waypoints
    @property
    def waypoints(self) -> str:
        """The waypoint style. Checks if the passed in value is in the TOML database of waypoints before setting and throws a ValueError if not.

        Returns:
            str: The style of the waypoints
        """
        return self._waypoints

    @waypoints.setter
    def waypoints(self, value: str) -> None:
        if value in waypoints_db.keys():
            self._waypoints = value
        else:
            raise ValueError("{0} is not an allowed value of waypoints")

    # Connection
    @property
    def connection(self) -> str:
        """The connection style. Checks if the passed in value is in the TOML database of connections before setting and throws a ValueError if not.

        Returns:
            str: The style of the connections
        """
        return self._connection

    @connection.setter
    def connection(self, value: str) -> None:
        if value in connection_db.keys():
            self._connection = value
        else:
            raise ValueError("{0} is not an allowed value of connection".format(value))

    # Pattern
    @property
    def pattern(self) -> str:
        """The pattern style. Checks if the passed in value is in the TOML database of patterns before setting and throws a ValueError if not.

        Returns:
            str: The style of the patterns
        """
        return self._pattern

    @pattern.setter
    def pattern(self, value: str) -> None:
        if value in pattern_db.keys():
            self._pattern = value
        else:
            raise ValueError("{0} is not an allowed value of pattern")

    # Color properties (enforce value)
    ## strokeColor
    @property
    def strokeColor(self) -> Optional[str]:
        return self._strokeColor

    @strokeColor.setter
    def strokeColor(self, value: Optional[str]) -> None:
        self._strokeColor = color_input_check(value)

    @strokeColor.deleter
    def strokeColor(self) -> None:
        self._strokeColor = None

    ## strokeWidth
    @property
    def strokeWidth(self) -> Optional[int]:
        return self._strokeWidth

    @strokeWidth.setter
    def strokeWidth(self, value: Optional[int]) -> None:
        self._strokeWidth = width_input_check(value)

    @strokeWidth.deleter
    def strokeWidth(self) -> None:
        self._strokeWidth = None

    # fillColor
    @property
    def fillColor(self) -> Optional[str]:
        return self._fillColor

    @fillColor.setter
    def fillColor(self, value: Optional[str]) -> None:
        self._fillColor = color_input_check(value)

    @fillColor.deleter
    def fillColor(self) -> None:
        self._fillColor = None

    # Jump style (enforce value)
    @property
    def jumpStyle(self) -> Optional[str]:
        return self._jumpStyle

    @jumpStyle.setter
    def jumpStyle(self, value: Optional[str]) -> None:
        if value in [None, "arc", "gap", "sharp", "line"]:
            self._jumpStyle = value
        else:
            raise ValueError(f"'{value}' is not a permitted jumpStyle value!")

    @jumpStyle.deleter
    def jumpStyle(self) -> None:
        self._jumpStyle = None

    ###########################################################
    # XML Generation
    ###########################################################

    @property
    def label(self) -> Optional[str]:
        """The text to place on the label, aka its value."""
        return self.value

    @label.setter
    def label(self, value: Optional[str]) -> None:
        self.value = value

    @label.deleter
    def label(self) -> None:
        self.value = None

    @property
    def label_offset(self) -> Optional[int]:
        """How far the label is offset away from the axis of the edge in pixels"""
        return self.geometry.y

    @label_offset.setter
    def label_offset(self, value: Optional[int]) -> None:
        self.geometry.y = value

    @label_offset.deleter
    def label_offset(self) -> None:
        self.geometry.y = None

    @property
    def label_position(self) -> Optional[float]:
        """Where along the edge the label is positioned. -1 is the source, 1 is the target, 0 is the center."""
        return self.geometry.x

    @label_position.setter
    def label_position(self, value: Optional[float]) -> None:
        self.geometry.x = value

    @label_position.deleter
    def label_position(self) -> None:
        self.geometry.x = None

    @property
    def xml(self) -> str:
        """The opening and closing XML tags with the styling attributes included.

        Returns:
            str: _description_
        """
        tag: str = (
            self.xml_open_tag + "\n  " + self.geometry.xml + "\n" + self.xml_close_tag
        )
        return tag


class BasicEdge(Edge):
    pass


class EdgeGeometry(DiagramBase):
    """This class stores the geometry associated with an edge. This is rendered as a subobject in the Draw.io file so it's convenient for it to have its own class."""

    def __init__(self, **kwargs: Any) -> None:
        """This class is automatically instantiated by a Edge object so the user should never need to create it."""
        super().__init__(**kwargs)
        self.xml_class: str = "mxGeometry"

        self.relative: int = kwargs.get("relative", 1)
        self.points: List[Point] = kwargs.get("points", [])
        self.as_attribute: str = kwargs.get("as_attribute", "geometry")

    def add_point(self, x: int, y: int) -> None:
        """Add a point to the edge geometry

        Args:
            x (int): The x coordinate of the point in pixels
            y (int): The y coordinate of the point in pixels
        """
        self.points.append(Point(x=x, y=y))

    @property
    def attributes(self) -> Dict[str, Any]:
        return {
            "x": self.x,
            "y": self.y,
            "relative": self.relative,
            "as": self.as_attribute,
        }

    @property
    def xml(self) -> str:
        if len(self.points) == 0:
            return self.xml_open_tag[:-1] + " />"
        else:
            return (
                self.xml_open_tag
                + '\n<Array as="points">\n'
                + "\n".join([pnt.xml for pnt in self.points])
                + "\n</Array>\n"
                + self.xml_close_tag
            )


class EdgeLabel(DiagramBase):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.xml_class: str = "mxCell"

        self.default_style: str = (
            "edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];"
        )

        self.value: str = kwargs.get("value", "")
        self.style: str = kwargs.get("style", self.default_style)
        self.vertex: int = kwargs.get("vertex", 1)
        self.connectable: int = kwargs.get("connectable", 1)

    @property
    def attributes(self) -> List[Any]:
        return []


class Point(DiagramBase):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.xml_class: str = "mxPoint"

        self.x: int = kwargs.get("x", 0)
        self.y: int = kwargs.get("y", 0)

    @property
    def attributes(self) -> Dict[str, int]:
        return {"x": self.x, "y": self.y}
