from .base_diagram import DiagramBase


__all__ = ["ObjectBase", "Group"]

###########################################################
# Objects
###########################################################


class ObjectBase(DiagramBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.geometry = ObjGeometry(parent_object=self)
        self.position = kwargs.get("position", (0, 0))
        self.size = kwargs.get("size", (120, 60))
        self.value = kwargs.get("value", "")
        self.default_style = "rounded=0;whiteSpace=wrap;html=1;"
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
            "parent": self.parent_id,
        }

    def __repr__(self):
        if self.value is not None:
            name_str = "{0} object with value {1}".format(
                self.__class__.__name__, self.value
            )
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

    @property
    def center_position(self):
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
            "as": self.as_attribute,
        }


class Group:
    def __init__(self, **kwargs):
        self.objects = kwargs.get("objects", [])
        self.geometry = ObjGeometry()

    def add_object(self, obj):
        if obj not in self.objects:
            self.objects.append(obj)

    ###########################################################
    # Passive properties
    ###########################################################

    @property
    def left(self):
        return min([obj.geometry.x for obj in self.objects])

    @property
    def right(self):
        return max(
            [obj.geometry.x + obj.geometry.width for obj in self.objects]
        )

    @property
    def top(self):
        return min([obj.geometry.y for obj in self.objects])

    @property
    def bottom(self):
        return max(
            [obj.geometry.y + obj.geometry.height for obj in self.objects]
        )

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.bottom - self.top

    @property
    def size(self):
        return (self.width, self.height)

    ###########################################################
    # Position properties
    ###########################################################

    @property
    def center_position(self):
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
            obj.geometry.x = obj.geometry.x + delta_x
            obj.geometry.y = obj.geometry.y + delta_y

    @property
    def position(self):
        return (self.left, self.top)

    @position.setter
    def position(self, new_position):
        current_position = (self.left, self.top)
        delta_x = new_position[0] - current_position[0]
        delta_y = new_position[1] - current_position[1]
        for obj in self.objects:
            obj.geometry.x = obj.geometry.x + delta_x
            obj.geometry.y = obj.geometry.y + delta_y
