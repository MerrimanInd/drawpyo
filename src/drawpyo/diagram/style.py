__all__ = ["style_str_from_dict"]

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


class Style:
    def __init__(self):
        self.attributes = []
        
    ###########################################################
    # Style properties
    ###########################################################
    def add_style_attribute(self, style_attr):
        if style_attr not in self._style_attributes:
            self._style_attributes.append(style_attr)

    @property
    def style_attributes(self):
        """
        The style attributes are the list of style tags that should be printed into the style XML attribute. This is a subset of the attributes defined on the object method.

        Returns:
            list: A list of the names of the style_attributes.
        """
        return self._style_attributes

    @style_attributes.setter
    def style_attributes(self, value):
        self._style_attributes = value

    @property
    def style(self):
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
        if hasattr(self, "baseStyle") and getattr(self, "baseStyle") is not None:
            style_str = getattr(self, "baseStyle") + ";"

        for attribute in self.style_attributes:
            if hasattr(self, attribute) and getattr(self, attribute) is not None:
                attr_val = getattr(self, attribute)
                # reformat different datatypes to strings
                if isinstance(attr_val, bool):
                    attr_val = format(attr_val * 1)
                style_str = style_str + "{0}={1};".format(attribute, attr_val)
        return style_str

    def _add_and_set_style_attrib(self, attrib, value):
        if hasattr(self, attrib):
            setattr(self, attrib, value)
        else:
            setattr(self, attrib, value)
            self.add_style_attribute(attrib)

    def apply_style_string(self, style_str):
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

    def _apply_style_from_template(self, template):
        for attrib in template.style_attributes:
            value = getattr(template, attrib)
            self._add_and_set_style_attrib(attrib, value)

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
            self._add_and_set_style_attrib(attr, val)

    @classmethod
    def from_style_string(cls, style_string):
        """
        This classmethod allows the intantiation of an object from a style
        string. This is useful since Draw.io allows copying the style string
        out of an object in their UI. This string can then be copied into the
        Python environment and further objects created that match the style.

        Args:
            style_string (str): A Draw.io style string

        Returns:
            BaseDiagram: A BaseDiagram or subclass instantiated with the style from the Draw.io string
        """
        new_obj = cls()
        new_obj.apply_style_string(style_string)
        return new_obj
