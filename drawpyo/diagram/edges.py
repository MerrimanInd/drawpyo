from .base_diagram import DiagramBase


__all__ = ['BasicEdge']

# Import the shape and edge definitions
from sys import version_info
from os import path
# toml path

dirname = path.dirname(__file__)
dirname = path.split(dirname)[0]
filename = path.join(dirname, 'formatting_database\\edge_styles.toml')

if version_info.minor < 11:
    import toml
    # TODO write an importer for Python versions prior to the Python 3.11
    # inclusion of tomllib as a base library
    
else:
    import tomllib
    with open(filename, "rb") as f:
        data = tomllib.load(f)
    connection_db = data['connection']
    connection_db[None] = {"shape": ""}
    
    pattern_db = data['pattern']
    pattern_db[None] = {}
    
    waypoints_db = data['waypoints']
    waypoints_db[None] = {}
    
    line_ends_db = data['line_ends']
    line_ends_db[None] = {'fillable': False}
    line_ends_db[""] = {'fillable': False}
        

###########################################################
# Edges
###########################################################

class BasicEdge(DiagramBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.xml_class = "mxCell"

        # Style
        self.extra_styles = kwargs.get("style", None)
        
        self.waypoints = kwargs.get("waypoints", "orthogonal")
        self.connection = kwargs.get("connection", "line")
        self.pattern = kwargs.get("pattern", "solid")
        
        self.line_end_target = kwargs.get("line_end_target", None)
        self.line_end_source = kwargs.get("line_end_source", None)
        self.end_fill_target = kwargs.get("end_fill_target", False)
        self.end_fill_source = kwargs.get("end_fill_source", False)
        
        self.jetty_size = kwargs.get("jetty_size", "auto")
        self.html = kwargs.get("html", 1)
        self.rounded = kwargs.get("rounded", 0)
        
        # Connection and geometry
        self.edge = kwargs.get("edge", 1)
        self.source = kwargs.get("source", None)
        self.target = kwargs.get("target", None)
        self.geometry = EdgeGeometry()
        self.entry_x = kwargs.get("entry_x", None)
        self.entry_y = kwargs.get("entry_y", None)
        self.entry_dx = kwargs.get("entry_dx", None)
        self.entry_dy = kwargs.get("entry_dy", None)
        self.exit_x = kwargs.get("exit_x", None)
        self.exit_y = kwargs.get("exit_y", None)
        self.exit_dx = kwargs.get("exit_dx", None)
        self.exit_dy = kwargs.get("exit_dy", None)

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
        return {
            "html": self.html,
            "rounded": self.rounded,
            "jettySize": self.jetty_size,
            "entryX": self.entry_x,
            "entryY": self.entry_y,
            "entryDx": self.entry_dx,
            "entryDy": self.entry_dy,
            "exitX": self.exit_x,
            "exitY": self.exit_y,
            "exitDx": self.exit_dx,
            "exitDy": self.exit_dy,
            "startArrow": self.start_arrow,
            "endArrow": self.end_arrow,
            "startFill": self.start_fill,
            "endFill": self.end_fill
        }
    
    @property
    def base_style_str(self):
        
        shape_str = self.style_str_from_dict(connection_db[self.connection])
        style_str = shape_str
     
        waypoint_style = self.style_str_from_dict(waypoints_db[self.waypoints])
        if waypoint_style is not None:
            style_str = style_str + ';' + waypoint_style
        
        pattern_style = self.style_str_from_dict(pattern_db[self.pattern])
        if pattern_style is not None:
            style_str = style_str + ';' + pattern_style
        return style_str
    
    @property
    def start_arrow(self):
        return self.line_end_source
    
    @property
    def start_fill(self):
        if line_ends_db[self.line_end_source]['fillable']:
            return self.end_fill_source
        else:
            return None
    
    @property
    def end_arrow(self):
        return self.line_end_target
    
    @property
    def end_fill(self):
        if line_ends_db[self.line_end_target]['fillable']:
            return self.end_fill_target
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
        return {}


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

