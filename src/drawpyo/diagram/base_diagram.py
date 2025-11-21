from __future__ import annotations

from typing import List, Optional, Tuple, Dict, Any, Union

from ..xml_base import XMLBase
from os import path


__all__ = [
    "DiagramBase",
    "Geometry",
    "style_str_from_dict",
    "import_shape_database",
    "color_input_check",
    "width_input_check",
]


def color_input_check(color_str: Optional[str]) -> Optional[str]:
    if color_str == None:
        return None
    elif color_str == "none":
        return color_str
    elif color_str == "default":
        return color_str
    elif color_str[0] == "#" and len(color_str) == 7:
        return color_str
    return None


def width_input_check(width: Optional[Union[int, str]]) -> Optional[int]:
    if not width or (isinstance(width, str) and not width.isdigit()):
        return None

    width = int(width)
    if width < 1:
        return 1
    elif width > 999:
        return 999
    else:
        return width


def import_shape_database(file_name: str, relative: bool = False) -> Dict[str, Any]:
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
            # To make the inheritor styles take precedence the inherited
            # object needs to be updated not the other way around. The copy is
            # created, updated, and replaced.
            new_obj = data[obj["inherit"]]
            new_obj.update(obj)
            obj = new_obj

    return data


def style_str_from_dict(style_dict: Dict[str, Any]) -> str:
    """
    This function returns a concatenated style string from a style dictionary.
    This format is:
            baseStyle;attr1=value;attr2=value
    It will concatenate the key:value pairs with the appropriate semicolons and
    equals except for the baseStyle, which it will prepend to the front with no
    equals sign.

    Parameters
    ----------
    style_dict : dict
        A dictionary of style:value pairs.

    Returns
    -------
    str
        A string with the style_dicts values concatenated correctly.

    """
    if "baseStyle" in style_dict:
        style_str = [style_dict.pop("baseStyle")]
    else:
        style_str = []
    style_str = style_str + [
        "{0}={1}".format(att, style)
        for (att, style) in style_dict.items()
        if style != "" and style != None
    ]
    return ";".join(style_str)


class DiagramBase(XMLBase):
    """
    This class is the base for all diagram objects to inherit from. It defines some general creation methods and properties to make diagram objects printable and useful.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._style_attributes: List[str] = ["html"]
        self.page: Optional[Any] = kwargs.get("page", None)
        self.xml_parent: Optional[DiagramBase] = kwargs.get("xml_parent", None)

    @classmethod
    def create_from_library(cls, library: Dict[str, Any], obj: str) -> DiagramBase:
        return cls()

    # XML_parent property
    @property
    def xml_parent_id(self) -> int:
        if self.xml_parent is not None:
            return self.xml_parent.id
        else:
            return 1

    # Parent object linking
    @property
    def xml_parent(self) -> Optional[DiagramBase]:
        return self._xml_parent

    @xml_parent.setter
    def xml_parent(self, p: Optional[DiagramBase]) -> None:
        if p is not None:
            p.add_object(self)
            self._xml_parent = p
        else:
            self._xml_parent = None

    @xml_parent.deleter
    def xml_parent(self) -> None:
        self._xml_parent.remove_object(self)
        self._xml_parent = None

    # Page property
    @property
    def page_id(self) -> int:
        if self.page is not None:
            return self.page.id
        else:
            return 1

    # page object linking
    @property
    def page(self) -> Optional[Any]:
        return self._page

    @page.setter
    def page(self, p: Optional[Any]) -> None:
        if p is not None:
            p.add_object(self)
            self._page = p
        else:
            self._page = None

    @page.deleter
    def page(self) -> None:
        self._page.remove_object(self)
        self._page = None

    def add_object(self, obj: DiagramBase) -> None:
        self.page.add_object(obj)

    ###########################################################
    # Style properties
    ###########################################################
    def add_style_attribute(self, style_attr: str) -> None:
        if style_attr not in self._style_attributes:
            self._style_attributes.append(style_attr)

    @property
    def style_attributes(self) -> List[str]:
        """
        The style attributes are the list of style tags that should be printed into the style XML attribute. This is a subset of the attributes defined on the object method.

        Returns:
            list: A list of the names of the style_attributes.
        """
        return self._style_attributes

    @style_attributes.setter
    def style_attributes(self, value: List[str]) -> None:
        self._style_attributes = value

    @property
    def style(self) -> str:
        """
        This function returns the style string of the object to be appended into the style XML attribute.

        First it searches the object properties called out in
        self.style_attributes. If the property is initialized to something
        that isn't None or an empty string, it will add it. Otherwise it
        searches the base_style defined by the object template.

        Returns:
            str: The style string of the object.

        """

        style_str = ""
        if (
            hasattr(self, "baseStyle")
            and getattr(self, "baseStyle") is not None
            and getattr(self, "baseStyle") != ""
        ):
            style_str = getattr(self, "baseStyle") + ";"

        # Add style attributes
        for attribute in self.style_attributes:
            if hasattr(self, attribute) and getattr(self, attribute) is not None:
                attr_val = getattr(self, attribute)
                # reformat different datatypes to strings
                if isinstance(attr_val, bool):
                    attr_val = format(attr_val * 1)
                style_str = style_str + "{0}={1};".format(attribute, attr_val)

        # Add style objects
        if hasattr(self, "text_format") and self.text_format is not None:
            style_str = style_str + self.text_format.style
        return style_str

    def _add_and_set_style_attrib(self, attrib: str, value: Any) -> None:
        if hasattr(self, attrib):
            setattr(self, attrib, value)
        else:
            setattr(self, attrib, value)
            self.add_style_attribute(attrib)

    def apply_style_string(self, style_str: str) -> None:
        """
        This function will apply a passed in style string to the object. This style string can be obtained from the Draw.io app by selecting Edit Style from the context menu of any object. This function will iterate through the attributes in the style string and assign the corresponding property the value.

        Args:
            style_str (str): A Draw.io style string
        """
        for attrib in style_str.split(";"):
            if attrib == "":
                pass
            elif "=" in attrib:
                a_name = attrib.split("=")[0]
                a_value = attrib.split("=")[1]
                if a_value.isdigit():
                    if "." in a_value:
                        a_value = float(a_value)
                    else:
                        a_value = int(a_value)
                elif a_value == "True" or a_value == "False":
                    a_value = bool(a_value)

                self._add_and_set_style_attrib(a_name, a_value)
            else:
                self.baseStyle = attrib

    def _apply_style_from_template(self, template: DiagramBase) -> None:
        for attrib in template.style_attributes:
            value = getattr(template, attrib)
            self._add_and_set_style_attrib(attrib, value)

    def apply_attribute_dict(self, attr_dict: Dict[str, Any]) -> None:
        """
        This function takes in a dictionary of attributes and applies them
        to the object. These attributes can be style or properties. If the
        attribute isn't already defined as a property of the class it's
        assumed to be a style attribute. It will then be added as a property
        and also appended to the .style_attributes list.

        Parameters
        ----------
        attr_dict : dict
            A dictionary of attributes to set or add to the object.

        Returns
        -------
        None.

        """
        for attr, val in attr_dict.items():
            self._add_and_set_style_attrib(attr, val)

    @classmethod
    def from_style_string(cls, style_string: str) -> DiagramBase:
        """
        This classmethod allows the intantiation of an object from a style
        string. This is useful since Draw.io allows copying the style string
        out of an object in their UI. This string can then be copied into the
        Python environment and further objects created that match the style.

        Args:
            style_string (str): A Draw.io style string

        Returns:
            DiagramBase: A DiagramBase or subclass instantiated with the style from the Draw.io string
        """
        new_obj = cls()
        new_obj.apply_style_string(style_string)
        return new_obj


class Geometry(DiagramBase):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.xml_class: str = "mxGeometry"

        self.parent_object: Optional[Any] = kwargs.get("parent_object", None)
        self._x: Union[int, float] = kwargs.get("x", 0)
        self._y: Union[int, float] = kwargs.get("y", 0)
        self.width: Union[int, float] = kwargs.get("width", 120)
        self.height: Union[int, float] = kwargs.get("height", 60)
        self.as_attribute: str = kwargs.get("as_attribute", "geometry")

    @property
    def x(self) -> Union[int, float]:
        return self._x

    @x.setter
    def x(self, value: Union[int, float]) -> None:
        self._x = value

    @property
    def y(self) -> Union[int, float]:
        return self._y

    @y.setter
    def y(self, value: Union[int, float]) -> None:
        self._y = value

    @property
    def attributes(self) -> Dict[str, Union[int, float, str]]:
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "as": self.as_attribute,
        }

    # Size property
    @property
    def size(self) -> Tuple[Union[int, float], Union[int, float]]:
        """The size of the object. It's set with a tuple of ints, width and height respectively.

        (width, height)

        Returns:
            tuple: A tuple of ints describing the size of the object
        """
        return (self.width, self.height)

    @size.setter
    def size(self, value: Tuple[Union[int, float], Union[int, float]]) -> None:
        self.width = value[0]
        self.height = value[1]
