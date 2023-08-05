from .base_object import DiagramBase


__all__ = ['EdgeBase']

###########################################################
# Edges
###########################################################

class EdgeBase(DiagramBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.xml_class = "mxCell"

        self.default_style = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;"
        self.style = kwargs.get("style", self.default_style)

        self.edge = kwargs.get("edge", 1)
        self.source = kwargs.get("source", None)
        self.target = kwargs.get("target", None)
        self.geometry = EdgeGeometry()

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

