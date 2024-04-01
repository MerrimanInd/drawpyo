from .xml_base import XMLBase


class Page:
    """
    This class defines a page in a Draw.io document. It contains a list of objects and a reference to the File it's in as well as formatting attributes.
    """

    def __init__(self, file=None, **kwargs):
        super().__init__()
        self.id = id(self)

        self.file = file
        self.objects = kwargs.get("objects", [])

        # There are two empty top level objects in every Draw.io diagram
        self.objects.append(XMLBase(id=0, xml_class="mxCell"))
        self.objects.append(XMLBase(id=1, xml_class="mxCell", xml_parent=0))

        # Properties

        if self.file is not None:
            page_num = len(self.file.pages)
        else:
            page_num = 1
        self.name = kwargs.get("name", f"Page-{page_num}")
        self.page_num = kwargs.get("page_num", page_num)

        self.dx = kwargs.get("dx", 2037)
        self.dy = kwargs.get("dy", 830)
        self.grid = kwargs.get("grid", 1)
        self.grid_size = kwargs.get("grid_size", 10)
        self.guides = kwargs.get("guides", 1)
        self.tooltips = kwargs.get("tooltips", 1)
        self.connect = kwargs.get("connect", 1)
        self.arrows = kwargs.get("arrows", 1)
        self.fold = kwargs.get("fold", 1)
        self.scale = kwargs.get("scale", 1)
        self.width = kwargs.get("width", 850)
        self.height = kwargs.get("height", 1100)
        self.math = kwargs.get("math", 0)
        self.shadow = kwargs.get("shadow", 0)

        # In the Draw.io file format, each page is actually three nested XML
        # tags. These are defined as XMLBase subclasses below
        self.diagram = Diagram(name=self.name)
        self.mxGraph = mxGraph(page=self)
        self.root = Root()

    def __repr__(self):
        return f"drawpyo Page - {self.name}"

    def remove(self):
        """This function removes the Page from its linked File object then deletes itself."""
        if self.file is not None:
            self.file.remove_page(self)
        del self

    def add_object(self, obj):
        if obj not in self.objects:
            self.objects.append(obj)

    def remove_object(self, obj):
        self.objects.remove(obj)

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, f):
        if f is not None:
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
        tag = (
            "      "
            + self.root.xml_close_tag
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
        self.xml_class = "diagram"

    @property
    def attributes(self):
        return {"name": self.name, "id": self.id}


class mxGraph(XMLBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.xml_class = "mxGraphModel"
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
            "pageScale": self.page.scale,
            "pageWidth": self.page.width,
            "pageHeight": self.page.height,
            "math": self.page.math,
            "shadow": self.page.shadow,
        }


class Root(XMLBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.xml_class = "root"

    @property
    def attributes(self):
        return {}
