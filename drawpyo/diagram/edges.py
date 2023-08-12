from .base_diagram import DiagramBase


__all__ = ['BasicEdge']

line_shape = {
    None: "",
    "straight": "",
    "orthogonal": "edgeStyle=orthogonalEdgeStyle;orthogonalLoop=1;",
    "vertical": "edgeStyle=elbowEdgeStyle;",
    "horizontal": "edgeStyle=elbowEdgeStyle;elbow=vertical;",
    "isometric": "edgeStyle=isometricEdgeStyle;",
    "isometric_vertical": "edgeStyle=isometricEdgeStyle;elbow=vertical;",
    "curved": "edgeStyle=orthogonalEdgeStyle;elbow=vertical;curved=1;",
    "entity_relation": "edgeStyle=entityRelationEdgeStyle;elbow=vertical;"}

line_type = {
    None: "",
    "line": "",
    "link": "shape=link;",
    "arrow": "shape=flexArrow;",
    "simple_arrow": "shape=arrow;"}

line_style = {
    None: "",
    "solid": "",
    "dashed_small": "dashed=1;",
    "dashed_medium": "dashed=1;dashPattern=8 8;",
    "dashed_large": "dashed=1;dashPattern=12 12;",
    "dotted_small": "dashed=1;dashPattern=1 1;",
    "dotted_medium": "dashed=1;dashPattern=1 2;",
    "dotted_large": "dashed=1;dashPattern=1 4;"}

# first argument is the style name, second is whether it's fillable
line_ends = {
    None:False,
    "":False,
    "classic":True,
    "classicThin":True,
    "open":False,
    "openThin":False,
    "openAsync":False,
    "block":True,
    "blockThin":True,
    "async":True,
    "oval":True,
    "diamond":True,
    "diamondThin":True,
    "dash":False,
    "halfCircle":False,
    "cross":False,
    "circlePlus":False,
    "circle":False,
    "baseDash":False,
    "ERone":False,
    "ERmandOne":False,
    "ERmany":False,
    "ERoneToMany":False,
    "ERzeroToOne":False,
    "ERzeroToMany":False,
    "doubleBlock":True}

###########################################################
# Edges
###########################################################

class BasicEdge(DiagramBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.xml_class = "mxCell"

        # Style
        #self.default_style = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;"
        self.extra_styles = kwargs.get("style", None)
        
        self.line_shape = kwargs.get("line_shape", "orthogonal")
        self.line_type = kwargs.get("line_type", "line")
        self.line_style = kwargs.get("line_style", "solid")
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
    def style(self):
        style_str = self.base_style
        for att, value in self.style_attributes.items():
            if value is not None and not value == "":
                style_str = style_str + "{0}={1};".format(att, value)
        style_str = style_str + self.extra_styles
        return style_str
    
    @property
    def base_style(self):
        style_str = ""
        style_str = style_str + line_shape[self.line_shape]
        style_str = style_str + line_type[self.line_type]
        style_str = style_str + line_style[self.line_style]
        return style_str
    
    @property
    def start_arrow(self):
        return self.line_end_source
    
    @property
    def start_fill(self):
        if line_ends[self.line_end_source]:
            return self.end_fill_source
        else:
            return None
    
    @property
    def end_arrow(self):
        return self.line_end_target
    
    @property
    def end_fill(self):
        if line_ends[self.line_end_target]:
            return self.end_fill_target
        else:
            return None
    
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

