from .base_diagram import DiagramBase, import_shape_database, style_str_from_dict


__all__ = ['BasicEdge']

data = import_shape_database(file_name='formatting_database\\edge_styles.toml', relative=True)

connection_db = data['connection']
connection_db[None] = {"shape": ""}

pattern_db = data['pattern']
pattern_db[None] = {}

waypoints_db = data['waypoints']
waypoints_db[None] = {}

line_ends_db = data['line_ends']
line_ends_db[None] = {'fillable': False}
line_ends_db[""] = {'fillable': False}
line_ends_db["none"] = {'fillable': False}


###########################################################
# Edges
###########################################################

class BasicEdge(DiagramBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.xml_class = "mxCell"

        # Style

        self.waypoints = kwargs.get("waypoints", "orthogonal")
        self.connection = kwargs.get("connection", "line")
        self.pattern = kwargs.get("pattern", "solid")

        self.line_end_target = kwargs.get("line_end_target", None)
        self.line_end_source = kwargs.get("line_end_source", None)
        self.endFill_target = kwargs.get("endFill_target", False)
        self.endFill_source = kwargs.get("endFill_source", False)

        self.jettySize = kwargs.get("jettySize", "auto")
        self.html = kwargs.get("html", 1)
        self.rounded = kwargs.get("rounded", 0)

        # Connection and geometry
        self.edge = kwargs.get("edge", 1)
        self.source = kwargs.get("source", None)
        self.target = kwargs.get("target", None)
        self.geometry = EdgeGeometry()
        self.entryX = kwargs.get("entryX", None)
        self.entryY = kwargs.get("entryY", None)
        self.entryDx = kwargs.get("entryDx", None)
        self.entryDy = kwargs.get("entryDy", None)
        self.exitX = kwargs.get("exitX", None)
        self.exitY = kwargs.get("exitY", None)
        self.exitDx = kwargs.get("exitDx", None)
        self.exitDy = kwargs.get("exitDy", None)

    def __repr__(self):
        name_str = "{0} edge from {1} to {2}".format(self.__class__.__name__, self.source, self.target)
        return name_str

    def __str_(self):
        return self.__repr__()

    @property
    def attributes(self):
        return {
            "id": self.id,
            "style": self.style,
            "edge": self.edge,
            "parent": self.parent_id,
            "source": self.source_id,
            "target": self.target_id}


    ###########################################################
    # Source and Target Linking
    ###########################################################

    # Source
    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, f):
        f.add_out_edge(self)
        self._source = f

    @source.deleter
    def source(self):
        self._source.remove_out_edge(self)
        self._source = None

    @property
    def source_id(self):
        if self.source is not None:
            return self.source.id
        else:
            return 1

    # Target
    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, f):
        f.add_in_edge(self)
        self._target = f

    @target.deleter
    def target(self):
        self._target.remove_in_edge(self)
        self._target = None

    @property
    def target_id(self):
        if self.target is not None:
            return self.target.id
        else:
            return 1

    ###########################################################
    # Style properties
    ###########################################################

    @property
    def style_attributes(self):
        return ["html",
                "rounded",
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
                "endFill"]

    @property
    def baseStyle(self):
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
        return self.line_end_source

    @startArrow.setter
    def startArrow(self, val):
        self._line_end_source = val

    @property
    def startFill(self):
        if line_ends_db[self.line_end_source]['fillable']:
            return self.endFill_source
        else:
            return None

    @property
    def endArrow(self):
        return self.line_end_target

    @endArrow.setter
    def endArrow(self, val):
        self._line_end_target = val
        
    @property
    def endFill(self):
        if line_ends_db[self.line_end_target]['fillable']:
            return self.endFill_target
        else:
            return None

    # Base Line Style

    # Waypoints
    @property
    def waypoints(self):
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
        return self._pattern

    @pattern.setter
    def pattern(self, value):
        if value in pattern_db.keys():
            self._pattern = value
        else:
            raise ValueError("{0} is not an allowed value of pattern")

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

class EdgeGeometry(DiagramBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.xml_class = "mxGeometry"
        self.parent_object = kwargs.get("parent_object", None)

        self.relative = kwargs.get("relative", 1)
        self.x = kwargs.get("x", None)
        self.y = kwargs.get("y", None)
        self.as_attribute = kwargs.get("as_attribute", "geometry")

    @property
    def attributes(self):
        return {
            "x": self.x,
            "y": self.y,
            "relative": self.relative,
            "as": self.as_attribute
        }

class EdgeLabel(DiagramBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.xml_class = "mxCell"

        self.default_style = "edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];"

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

        self.parent_object = self.kwargs.get("parent_object", None)
        self.x = kwargs.get("x", 0)
        self.y = kwargs.get("y", 0)

    @property
    def attributes(self):
        return {
            "x": self.x,
            "y": self.y
        }

