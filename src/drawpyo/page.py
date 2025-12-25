from typing import List, Optional, Any, Union, Dict
from .xml_base import XMLBase
from .utils.logger import logger
from .utils.page_sizes import PageSize


class Page:
    def __init__(self, file: Optional[Any] = None, **kwargs: Any) -> None:
        """
        Args:
            file (Optional[File]): Parent File object this page belongs to.

        Keyword Args:
            objects (list[Any]): Initial list of objects on the page.

            name (str): Page name. Default: "Page-{page_num}"
            page_num (int): Page index within the file. Default: inferred from file.

            dx (int | float): Horizontal translation of the page. Default: 2037
            dy (int | float): Vertical translation of the page. Default: 830
            scale (int | float): Page scale factor. Default: 1

            grid (int): Whether grid is enabled. Default: 1
            grid_size (int): Grid spacing. Default: 10
            guides (int): Whether alignment guides are enabled. Default: 1
            tooltips (int): Whether tooltips are enabled. Default: 1
            connect (int): Whether connections are enabled. Default: 1
            arrows (int): Whether arrows are enabled. Default: 1
            fold (int): Whether page folding is enabled. Default: 1

            size_preset (PageSize): Optional predefined page size. Overrides width and height.
            width (int | float): Page width. Default: 850
            height (int | float): Page height. Default: 1100

            math (int): Whether math rendering is enabled. Default: 0
            shadow (int): Whether shadows are enabled. Default: 0
        """
        super().__init__()
        self.id: int = id(self)

        self.file: Optional[File] = file
        self.objects: List[Any] = kwargs.get("objects", [])

        # There are two empty top level objects in every Draw.io diagram
        self.objects.append(XMLBase(id=0, xml_class="mxCell"))
        self.objects.append(XMLBase(id=1, xml_class="mxCell", xml_parent=0))

        # Properties

        if self.file is not None:
            page_num = len(self.file.pages)
        else:
            page_num = 1
        self.name: str = kwargs.get("name", f"Page-{page_num}")
        self.page_num: int = kwargs.get("page_num", page_num)

        self.dx: Union[int, float] = kwargs.get("dx", 2037)
        self.dy: Union[int, float] = kwargs.get("dy", 830)
        self.grid: int = kwargs.get("grid", 1)
        self.grid_size: int = kwargs.get("grid_size", 10)
        self.guides: int = kwargs.get("guides", 1)
        self.tooltips: int = kwargs.get("tooltips", 1)
        self.connect: int = kwargs.get("connect", 1)
        self.arrows: int = kwargs.get("arrows", 1)
        self.fold: int = kwargs.get("fold", 1)
        self.scale: Union[int, float] = kwargs.get("scale", 1)
        self.size_preset: Optional[PageSize] = kwargs.get("size_preset", None)
        if self.size_preset and ("width" in kwargs or "height" in kwargs):
            logger.warning(
                "Page created with size_preset - This overrides width/height arguments."
            )
        self.width: Union[int, float] = (
            kwargs.get("width", 850) if not self.size_preset else self.size_preset[0]
        )
        self.height: Union[int, float] = (
            kwargs.get("height", 1100) if not self.size_preset else self.size_preset[1]
        )
        self.math: int = kwargs.get("math", 0)
        self.shadow: int = kwargs.get("shadow", 0)

        # In the Draw.io file format, each page is actually three nested XML
        # tags. These are defined as XMLBase subclasses below
        self.diagram: Diagram = Diagram(name=self.name)
        self.mxGraph: mxGraph = mxGraph(page=self)
        self.root: Root = Root()

        logger.info(f"📄 Page created: '{self.__repr__()}'")

    def __repr__(self) -> str:
        return f"drawpyo Page - {self.name}"

    def remove(self) -> None:
        """This function removes the Page from its linked File object then deletes itself."""
        if self.file is not None:
            self.file.remove_page(self)
        del self

    def add_object(self, obj: Any) -> None:
        if obj not in self.objects:
            self.objects.append(obj)

    def remove_object(self, obj: Any) -> None:
        self.objects.remove(obj)

    @property
    def file(self) -> Optional[Any]:
        return self._file

    @file.setter
    def file(self, f: Optional[Any]) -> None:
        if f is not None:
            f.add_page(self)
        self._file = f

    @file.deleter
    def file(self) -> None:
        self._file.remove_page(self)
        self._file = None

    ###########################################################
    # XML Generation
    ###########################################################
    @property
    def xml(self) -> str:
        xml_string = self.xml_open_tag
        for obj in self.objects:
            xml_string = xml_string + "\n        " + obj.xml
        xml_string = xml_string + "\n" + self.xml_close_tag
        return xml_string

    @property
    def xml_open_tag(self) -> str:
        tag = (
            self.diagram.xml_open_tag
            + "\n    "
            + self.mxGraph.xml_open_tag
            + "\n      "
            + self.root.xml_open_tag
        )
        return tag

    @property
    def xml_close_tag(self) -> str:
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
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.name: str = kwargs.get("name", "")
        self.xml_class: str = "diagram"

    @property
    def attributes(self) -> Dict[str, Union[str, int]]:
        return {"name": self.name, "id": self.id}


class mxGraph(XMLBase):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.xml_class: str = "mxGraphModel"
        self.page: Optional[Page] = kwargs.get("page", None)

    @property
    def attributes(self) -> Dict[str, Union[int, float]]:
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
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.xml_class: str = "root"

    @property
    def attributes(self) -> Dict[str, Any]:
        return {}
