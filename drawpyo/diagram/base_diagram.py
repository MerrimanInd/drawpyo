from ..xml_base import XMLBase
from os import path


__all__ = ["DiagramBase", "style_str_from_dict", "import_shape_database"]


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
            obj = data[obj["inherit"]].update(obj)

    return data


def style_str_from_dict(style_dict):
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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.page = kwargs.get("page", None)
        self.parent = kwargs.get("parent", None)

    @classmethod
    def create_from_library(cls, library, obj):
        return cls

    # Parent property
    @property
    def parent_id(self):
        if self.parent is not None:
            return self.parent.id
        else:
            return 1

    # Parent object linking
    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, p):
        if p is not None:
            p.add_object(self)
            self._parent = p
        else:
            self._parent = None

    @parent.deleter
    def parent(self):
        self._parent.remove_object(self)
        self._parent = None

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

    ###########################################################
    # Style properties
    ###########################################################
    @property
    def style_attributes(self):
        """
        This is a placeholder that should be replaced by the defined style
        attributes of the subclass.

        """
        return ["html"]

    @property
    def style(self):
        """
        This function returns the style string of the object to be appending
        into the style XML attribute.

        First it searches the object properties called out in
        self.style_attributes. If the property is initialized to something
        that isn't None or an empty string, it will add it. Otherwise it
        searches the base_style defined by the object template.

        Returns
        -------
        style_str : str
            The style string of the object.

        """
        style_str = ""
        if (
            hasattr(self, "baseStyle")
            and getattr(self, "baseStyle") is not None
        ):
            style_str = getattr(self, "baseStyle") + ";"

        for attribute in self.style_attributes:
            if (
                hasattr(self, attribute)
                and getattr(self, attribute) is not None
            ):
                attr_val = getattr(self, attribute)
                style_str = style_str + "{0}={1};".format(attribute, attr_val)
        return style_str

    def apply_style_string(self, style_str):
        """
        This function will apply a passed in style string to the object. It
        will iterate through the attributes in the style string and assign
        the corresponding property the value.

        Parameters
        ----------
        style_str : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        for attrib in style_str.split(";"):
            if attrib == '':
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

                setattr(self, a_name, a_value)
            else:
                self.baseStyle = attrib

    def apply_attribute_dict(self, attr_dict):
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
            if hasattr(self, attr):
                # if the style attribute exists, add it
                setattr(self, attr, val)
            else:
                # If the style attribute doesn't exist, add it and add to the
                # style dict
                setattr(self, attr, val)
                self.add_style_attribute(attr)

    @classmethod
    def from_style_string(cls, style_string):
        """
        This classmethod allows the intantiation of an object from a style
        string. This is useful since Draw.io allows copying the style string
        out of an object in their UI. This string can then be copied into the
        Python environment and further objects created that match the style.

        Parameters
        ----------
        style_string : TYPE
            DESCRIPTION.

        Returns
        -------
        new_obj : TYPE
            DESCRIPTION.

        """
        new_obj = cls()
        new_obj.apply_style_string(style_string)
        return new_obj
