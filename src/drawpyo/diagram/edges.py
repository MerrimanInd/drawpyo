from os import path

from .base_diagram import (
    DiagramBase,
    import_shape_database,
    style_str_from_dict,
    color_input_check,
    width_input_check,
)
from .text_format import TextFormat

__all__ = ["Edge", "BasicEdge", "EdgeGeometry", "Point"]

data = import_shape_database(
    file_name=path.join("formatting_database", "edge_styles.toml"), relative=True
)

connection_db = data["connection"]
connection_db[None] = {"shape": ""}

pattern_db = data["pattern"]
pattern_db[None] = {}

waypoints_db = data["waypoints"]
waypoints_db[None] = {}

line_ends_db = data["line_ends"]
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

    def __init__(self, **kwargs):
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
            strokeColor (str): The color of the border of the edge ('none', 'default', or hex color code)
            strokeWidth (int): The width of the border of the the edge within range (1-999)
            fillColor (str): The color of the fill of the edge ('none', 'default', or hex color code)
            jumpStyle (str): The line jump style ('arc', 'gap', 'sharp', 'line')
            jumpSize (int): The size of the line jumps in points.
            opacity (int): The opacity of the edge (0-100)
        """
        super().__init__(**kwargs)
        self.xml_class = "mxCell"

        # Style
        self.text_format = kwargs.get("text_format", TextFormat())
        self.waypoints = kwargs.get("waypoints", "orthogonal")
        self.connection = kwargs.get("connection", "line")
        self.pattern = kwargs.get("pattern", "solid")
        self.opacity = kwargs.get("opacity", None)
        self.strokeColor = kwargs.get("strokeColor", None)
        self.strokeWidth = kwargs.get("strokeWidth", None)
        self.fillColor = kwargs.get("fillColor", None)

        # Line end
        self.line_end_target = kwargs.get("line_end_target", None)
        self.line_end_source = kwargs.get("line_end_source", None)
        self.endFill_target = kwargs.get("endFill_target", False)
        self.endFill_source = kwargs.get("endFill_source", False)
        self.endSize = kwargs.get("endSize", None)
        self.startSize = kwargs.get("startSize", None)

        self.rounded = kwargs.get("rounded", 0)
        self.sketch = kwargs.get("sketch", None)
        self.shadow = kwargs.get("shadow", None)
        self.flowAnimation = kwargs.get("flowAnimation", None)

        self.jumpStyle = kwargs.get("jumpStyle", None)
        self.jumpSize = kwargs.get("jumpSize", None)

        # Connection and geometry
        self.jettySize = kwargs.get("jettySize", "auto")
        self.geometry = EdgeGeometry()
        self.edge = kwargs.get("edge", 1)
        self.targetPerimeterSpacing = kwargs.get("targetPerimeterSpacing", None)
        self.sourcePerimeterSpacing = kwargs.get("sourcePerimeterSpacing", None)
        self.source = kwargs.get("source", None)
        self.target = kwargs.get("target", None)
        self.entryX = kwargs.get("entryX", None)
        self.entryY = kwargs.get("entryY", None)
        self.entryDx = kwargs.get("entryDx", None)
        self.entryDy = kwargs.get("entryDy", None)
        self.exitX = kwargs.get("exitX", None)
        self.exitY = kwargs.get("exitY", None)
        self.exitDx = kwargs.get("exitDx", None)
        self.exitDy = kwargs.get("exitDy", None)

        # Label
        self.label = kwargs.get("label", None)
        self.edge_axis_offset = kwargs.get("edge_offset", None)
        self.label_offset = kwargs.get("label_offset", None)
        self.label_position = kwargs.get("label_position", None)

    def __repr__(self):
        name_str = "{0} edge from {1} to {2}".format(
            self.__class__.__name__, self.source, self.target
        )
        return name_str

    def __str__(self):
        return self.__repr__()

    def remove(self):
        """This function removes references to the Edge from its source and target objects then deletes the Edge."""
        if self.source is not None:
            self.source.remove_out_edge(self)
        if self.target is not None:
            self.target.remove_in_edge(self)
        del self

    @property
    def attributes(self):
        """Returns the XML attributes to be added to the tag for the object

        Returns:
            dict: Dictionary of object attributes and their values
        """
        base_attr_dict = {
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
    def source(self):
        """The source object of the edge. Automatically adds the edge to the object when set and removes it when deleted.

        Returns:
            BaseDiagram: source object of the edge
        """
        return self._source

    @source.setter
    def source(self, f):
        if f is not None:
            f.add_out_edge(self)
            self._source = f

    @source.deleter
    def source(self):
        self._source.remove_out_edge(self)
        self._source = None

    @property
    def source_id(self):
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
    def target(self):
        """The target object of the edge. Automatically adds the edge to the object when set and removes it when deleted.

        Returns:
            BaseDiagram: target object of the edge
        """
        return self._target

    @target.setter
    def target(self, f):
        if f is not None:
            f.add_in_edge(self)
            self._target = f

    @target.deleter
    def target(self):
        self._target.remove_in_edge(self)
        self._target = None

    @property
    def target_id(self):
        """The ID of the target object or 1 if no target is set

        Returns:
            int: Target object ID
        """
        if self.target is not None:
            return self.target.id
        else:
            return 1

    def add_point(self, x, y):
        """Add a point to the edge

        Args:
            x (int): The x coordinate of the point in pixels
            y (int): The y coordinate of the point in pixels
        """
        self.geometry.points.append(Point(x=x, y=y))

    def add_point_pos(self, position):
        """Add a point to the edge by position tuple

        Args:
            position (tuple): A tuple of ints describing the x and y coordinates in pixels
        """
        self.geometry.points.append(Point(x=position[0], y=position[1]))

    ###########################################################
    # Style properties
    ###########################################################

    @property
    def style_attributes(self):
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
    def baseStyle(self):
        """Generates the baseStyle string from the connection style, waypoint style, pattern style, and base style string.

        Returns:
            str: Concatenated baseStyle string
        """
        style_str = []
        connection_style = style_str_from_dict(connection_db[self.connection])
        if connection_style is not None and connection_style != "":
            style_str.append(connection_style)

        waypoint_style = style_str_from_dict(waypoints_db[self.waypoints])
        if waypoint_style is not None and waypoint_style != "":
            style_str.append(waypoint_style)

        pattern_style = style_str_from_dict(pattern_db[self.pattern])
        if pattern_style is not None and pattern_style != "":
            style_str.append(pattern_style)

        if len(style_str) == 0:
            return None
        else:
            return ";".join(style_str)

    @property
    def startArrow(self):
        """What graphic the edge should be rendered with at the source

        Returns:
            str: The source edge graphic
        """
        return self.line_end_source

    @startArrow.setter
    def startArrow(self, val):
        self.line_end_source = val

    @property
    def startFill(self):
        """Whether the graphic at the source should be filled

        Returns:
            bool: The source graphic fill
        """
        if line_ends_db[self.line_end_source]["fillable"]:
            return self.endFill_source
        else:
            return None

    @property
    def endArrow(self):
        """What graphic the edge should be rendered with at the target

        Returns:
            str: The target edge graphic
        """
        return self.line_end_target

    @endArrow.setter
    def endArrow(self, val):
        self.line_end_target = val

    @property
    def endFill(self):
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
    def waypoints(self):
        """The waypoint style. Checks if the passed in value is in the TOML database of waypoints before setting and throws a ValueError if not.

        Returns:
            str: The style of the waypoints
        """
        return self._waypoints

    @waypoints.setter
    def waypoints(self, value):
        if value in waypoints_db.keys():
            self._waypoints = value
        else:
            raise ValueError("{0} is not an allowed value of waypoints")

    # Connection
    @property
    def connection(self):
        """The connection style. Checks if the passed in value is in the TOML database of connections before setting and throws a ValueError if not.

        Returns:
            str: The style of the connections
        """
        return self._connection

    @connection.setter
    def connection(self, value):
        if value in connection_db.keys():
            self._connection = value
        else:
            raise ValueError("{0} is not an allowed value of connection".format(value))

    # Pattern
    @property
    def pattern(self):
        """The pattern style. Checks if the passed in value is in the TOML database of patterns before setting and throws a ValueError if not.

        Returns:
            str: The style of the patterns
        """
        return self._pattern

    @pattern.setter
    def pattern(self, value):
        if value in pattern_db.keys():
            self._pattern = value
        else:
            raise ValueError("{0} is not an allowed value of pattern")

    # Color properties (enforce value)
    ## strokeColor
    @property
    def strokeColor(self):
        return self._strokeColor

    @strokeColor.setter
    def strokeColor(self, value):
        self._strokeColor = color_input_check(value)

    @strokeColor.deleter
    def strokeColor(self):
        self._strokeColor = None

    ## strokeWidth
    @property
    def strokeWidth(self):
        return self._strokeWidth

    @strokeWidth.setter
    def strokeWidth(self, value):
        self._strokeWidth = width_input_check(value)

    @strokeWidth.deleter
    def strokeWidth(self):
        self._strokeWidth = None

    # fillColor
    @property
    def fillColor(self):
        return self._fillColor

    @fillColor.setter
    def fillColor(self, value):
        self._fillColor = color_input_check(value)

    @fillColor.deleter
    def fillColor(self):
        self._fillColor = None

    # Jump style (enforce value)
    @property
    def jumpStyle(self):
        return self._jumpStyle

    @jumpStyle.setter
    def jumpStyle(self, value):
        if value in [None, "arc", "gap", "sharp", "line"]:
            self._jumpStyle = value
        else:
            raise ValueError(f"'{value}' is not a permitted jumpStyle value!")

    @jumpStyle.deleter
    def jumpStyle(self):
        self._jumpStyle = None

    ###########################################################
    # XML Generation
    ###########################################################

    @property
    def label(self):
        """The text to place on the label, aka its value."""
        return self.value

    @label.setter
    def label(self, value):
        self.value = value

    @label.deleter
    def label(self):
        self.value = None

    @property
    def label_offset(self):
        """How far the label is offset away from the axis of the edge in pixels"""
        return self.geometry.y

    @label_offset.setter
    def label_offset(self, value):
        self.geometry.y = value

    @label_offset.deleter
    def label_offset(self):
        self.geometry.y = None

    @property
    def label_position(self):
        """Where along the edge the label is positioned. -1 is the source, 1 is the target, 0 is the center."""
        return self.geometry.x

    @label_position.setter
    def label_position(self, value):
        self.geometry.x = value

    @label_position.deleter
    def label_position(self):
        self.geometry.x = None

    @property
    def xml(self):
        """The opening and closing XML tags with the styling attributes included.

        Returns:
            str: _description_
        """
        tag = self.xml_open_tag + "\n  " + self.geometry.xml + "\n" + self.xml_close_tag
        return tag


class BasicEdge(Edge):
    pass


class EdgeGeometry(DiagramBase):
    """This class stores the geometry associated with an edge. This is rendered as a subobject in the Draw.io file so it's convenient for it to have its own class."""

    def __init__(self, **kwargs):
        """This class is automatically instantiated by a Edge object so the user should never need to create it."""
        super().__init__(**kwargs)
        self.xml_class = "mxGeometry"

        self.relative = kwargs.get("relative", 1)
        self.points = kwargs.get("points", [])
        self.as_attribute = kwargs.get("as_attribute", "geometry")

    def add_point(self, x, y):
        """Add a point to the edge geometry

        Args:
            x (int): The x coordinate of the point in pixels
            y (int): The y coordinate of the point in pixels
        """
        self.points.append(Point(x=x, y=y))

    @property
    def attributes(self):
        return {
            "x": self.x,
            "y": self.y,
            "relative": self.relative,
            "as": self.as_attribute,
        }

    @property
    def xml(self):
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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.xml_class = "mxCell"

        self.default_style = (
            "edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];"
        )

        self.value = kwargs.get("value", "")
        self.style = kwargs.get("style", self.default_style)
        self.vertex = kwargs.get("vertex", 1)
        self.connectable = kwargs.get("connectable", 1)

    @property
    def attributes(self):
        return []


class Point(DiagramBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.xml_class = "mxPoint"

        self.x = kwargs.get("x", 0)
        self.y = kwargs.get("y", 0)

    @property
    def attributes(self):
        return {"x": self.x, "y": self.y}
