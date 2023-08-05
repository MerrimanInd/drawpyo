from .xml_base import XMLBase

class Page:
    def __init__(self, **kwargs):
        super().__init__()
        self.id = id(self)

        self.file = kwargs.get("file", None)
        self.objects = kwargs.get("objects", [])

        # There are two empty top level objects in every Draw.io diagram
        self.objects.append(XMLBase(id=0, xml_class="mxCell"))
        self.objects.append(XMLBase(id=1, xml_class="mxCell", parent=0))

        # Properties

        # TODO increment pages based on total pages in File object
        self.name = kwargs.get("name", "Page-1")
        self.page_num = kwargs.get("page", 1)

        self.dx = kwargs.get("dx", 2037)
        self.dy = kwargs.get("dy", 830)
        self.grid = kwargs.get("grid", 1)
        self.grid_size = kwargs.get("grid_size", 10)
        self.guides = kwargs.get("guides", 1)
        self.tooltips = kwargs.get("tooltips", 1)
        self.connect = kwargs.get("connect", 1)
        self.arrows = kwargs.get("arrows", 1)
        self.fold = kwargs.get("fold", 1)
        self.page_scale = kwargs.get("page_scale", 1)
        self.page_width = kwargs.get("page_width", 850)
        self.page_height = kwargs.get("page_height", 1100)
        self.math = kwargs.get("math", 0)
        self.shadow = kwargs.get("shadow", 0)

        # In the Draw.io file format, each page is actually three nested XML
        # tags. These are defined as XMLBase subclasses below
        self.diagram = Diagram(name = self.name)
        self.mxGraph = mxGraph(page=self)
        self.root = Root()

    def add_object(self, obj):
        self.objects.append(obj)

    def remove_object(self, obj):
        self.objects.remove(obj)

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, f):
        f.add_page(self)
        self._file = f

    @file.deleter
    def file(self):
        self._file.remove_page(self)
        self._file = None

    ###########################################################
    # XML Generation
    ###########################################################
    @property
    def xml(self):
        xml_string = self.xml_open_tag
        for obj in self.objects:
            xml_string = xml_string + "\n        " + obj.xml
        xml_string = xml_string + "\n" + self.xml_close_tag
        return xml_string

    @property
    def xml_open_tag(self):
        tag = (
            self.diagram.xml_open_tag
            + "\n    "
            + self.mxGraph.xml_open_tag
            + "\n      "
            + self.root.xml_open_tag
        )
        return tag

    @property
    def xml_close_tag(self):
        tag = ("      " +
            self.root.xml_close_tag
            + "\n    "
            + self.mxGraph.xml_close_tag
            + "\n  "
            + self.diagram.xml_close_tag
        )
        return tag

###########################################################
# Formatting classes
###########################################################

class Diagram(XMLBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = kwargs.get("name", "")
        self.xml_class="diagram"

    @property
    def attributes(self):
        return {"name": self.name, "id": self.id}

class mxGraph(XMLBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.xml_class="mxGraphModel"
        self.page = kwargs.get("page", None)

    @property
    def attributes(self):
        return {
            "dx": self.page.dx,
            "dy": self.page.dy,
            "grid": self.page.grid,
            "gridSize": self.page.grid_size,
            "guides": self.page.guides,
            "toolTips": self.page.tooltips,
            "connect": self.page.connect,
            "arrows": self.page.arrows,
            "fold": self.page.fold,
            "page": self.page.page_num,
            "pageScale": self.page.page_scale,
            "pageWidth": self.page.page_width,
            "pageHeight": self.page.page_height,
            "math": self.page.math,
            "shadow": self.page.shadow,
        }

class Root(XMLBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.xml_class="root"

    @property
    def attributes(self):
        return {}