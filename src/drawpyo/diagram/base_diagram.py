from ..xml_base import XMLBase
from .style import Style
from os import path


__all__ = ["DiagramBase", "import_shape_database"]


def import_shape_database(file_name, relative=False):
    """
    This function imports a TOML shape database and returns a dictionary of the
    shapes defined therein. It supports inheritance, meaning that if there is
    an inherit value in any of the shape dictionaries it will attempt to go
    find the inherited master shape and use it as a starting format, but
    overwriting any styles defined in both with the style defined in the child
    object.

    Parameters
    ----------
    filename : str
        The path to a TOML file containing a style library database.

    Returns
    -------
    data : dict
        A database of shapes defined in the TOML file.

    """
    # Import the shape and edge definitions
    from sys import version_info

    if relative:
        # toml path
        dirname = path.dirname(__file__)
        dirname = path.split(dirname)[0]
        file_name = path.join(dirname, file_name)

    if version_info.minor < 11:
        import toml

        data = toml.load(file_name)
    else:
        import tomllib

        with open(file_name, "rb") as f:
            data = tomllib.load(f)

    for obj in data.values():
        if "inherit" in obj:
            obj.update(data[obj['inherit']])

    return data

class DiagramBase(XMLBase):
    """
    This class is the base for all diagram objects to inherit from. It defines some general creation methods and properties to make diagram objects printable and useful.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.style = Style()
        self.style.attributes = ["html"]
        self.page = kwargs.get("page", None)
        self.xml_parent = kwargs.get("xml_parent", None)

    @classmethod
    def create_from_library(cls, library, obj):
        return cls

    # XML_parent property
    @property
    def xml_parent_id(self):
        if self.xml_parent is not None:
            return self.xml_parent.id
        else:
            return 1

    # Parent object linking
    @property
    def xml_parent(self):
        return self._xml_parent

    @xml_parent.setter
    def xml_parent(self, p):
        if p is not None:
            p.add_object(self)
            self._xml_parent = p
        else:
            self._xml_parent = None

    @xml_parent.deleter
    def xml_parent(self):
        self._xml_parent.remove_object(self)
        self._xml_parent = None

    # Page property
    @property
    def page_id(self):
        if self.page is not None:
            return self.page.id
        else:
            return 1

    # page object linking
    @property
    def page(self):
        return self._page

    @page.setter
    def page(self, p):
        if p is not None:
            p.add_object(self)
            self._page = p
        else:
            self._page = None

    @page.deleter
    def page(self):
        self._page.remove_object(self)
        self._page = None
