from .base_diagram import DiagramBase


__all__ = ['ObjectBase']

###########################################################
# Objects
###########################################################

class ObjectBase(DiagramBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.geometry = ObjGeometry(parent_object = self)
        self.position = kwargs.get("position", (0,0))
        self.size = kwargs.get("size", (120, 60))
        self.value = kwargs.get("value", "")
        self.default_style ="rounded=0;whiteSpace=wrap;html=1;"
        self.style = kwargs.get("style", self.default_style)
        self.vertex = kwargs.get("vertex", 1)

        self.out_edges = kwargs.get("out_edges", [])
        self.in_edges = kwargs.get("in_edges", [])

        self.xml_class = "mxCell"

    @property
    def attributes(self):
        return {
            "id": self.id,
            "value": self.value,
            "style": self.style,
            "vertex": self.vertex,
            "parent": self.parent_id}

    def __repr__(self):
        if self.value is not None:
            name_str = "{0} object with value {1}".format(self.__class__.__name__, self.value)
        else:
            name_str = "{0} object".format(self.__class__.__name__)
        return name_str

    def __str_(self):
        return self.__repr__()

    # Position property
    @property
    def position(self):
        return (self.geometry.x, self.geometry.y)

    @position.setter
    def position(self, value):
        self.geometry.x = value[0]
        self.geometry.y = value[1]

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
            "as": self.as_attribute
        }