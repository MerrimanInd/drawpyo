from typing import Dict, Optional, Any, Union

xmlize: Dict[str, str] = {}
xmlize[">"] = "&gt;"
xmlize["<"] = "&lt;"
xmlize["&"] = "&amp;"
xmlize['"'] = "&quot;"
xmlize["'"] = "&apos;"

# Escape control characters
xmlize["\n"] = "&#xa;"  # Newline
xmlize["\t"] = "&#x9;"  # Tab
xmlize["\r"] = "&#xd;"  # Carriage return


# When saving Draw.io uses this for single quotes and also has some funky XML character escaping (double escaping ampersands) but handles normal XML escapes (above) fine on loading
# xmlize["'"] = "&#39;"
# xmlize['"'] = "&#34;"
# xmlize["&"] = "&#38;"


class XMLBase:
    """
    XMLBase is the base class for all exportable objects in drawpyo. This class defines a few useful properties that drawpyo needs to use to generate a Draw.io file.
    """

    def __init__(self, **kwargs: Any) -> None:
        self._id: Union[int, str] = kwargs.get("id", id(self))
        self.xml_class: str = kwargs.get("xml_class", "xml_tag")

        # There's only one situation where XMLBase is called directly: to
        # create the two empty mxCell objects at the beginning of every
        # Draw.io diagram. The following declarations should be overwritten
        # in every other use case.
        self.xml_parent: Optional[Any] = kwargs.get("xml_parent", None)

        self.tag: Optional[str] = kwargs.get("tag", None)
        self.tooltip: Optional[str] = kwargs.get("tooltip", None)

    @property
    def id(self) -> Union[int, str]:
        """
        id is a unique identifier. Draw.io generated diagrams use an ID many more characters but the app isn't picky when parsing so drawpyo just uses Python's built-in id() function as it guarantees unique identifiers.

        Returns:
            int: A unique identifier for the Draw.io object
        """
        return self._id

    @property
    def attributes(self) -> Dict[str, Any]:
        """
        The most basic attributes of a Draw.io object. Extended by subclasses.

        Returns:
            dict: A dict containing an 'id' and 'xml_parent' object.
        """
        return {"id": self.id, "parent": self.xml_parent}

    ###########################################################
    # XML Tags
    ###########################################################

    @property
    def xml_open_tag(self) -> str:
        """
        The open tag contains the name of the object but also the attribute tags. This property function concatenates all the attributes in the class along with the opening and closing angle brackets and returns them as a string.

        When the "tag" attribute tag is provided, a tags attribute is applied to the object. This allows for selecting, hiding, or displaying multiple elements in the diagram.
        When the "tooltip" attribute tag is provided, a tooltip attribute is applied to the object. This allows for extra information to be displayed when an element is hovered over in the diagram.
        When using tags or tooltips, the open_tag value and id are shifted to the <UserObject> tag.


        Example:
        <class_name attribute_name=attribute_value>

        Returns:
            str: The opening tag of the object with all the attributes.
        """
        if self.tag or self.tooltip:
            open_user_object_tag = f'<UserObject label="{self.value}" id="{self.id}"'
            if self.tag:
                open_user_object_tag += f' tags="{self.tag}"'
            if self.tooltip:
                open_user_object_tag += f' tooltip="{self.xml_ify(self.tooltip)}"'
            open_user_object_tag += ">"

            open_tag = "<" + self.xml_class
            for att, value in self.attributes.items():
                if att == "id" or att == "value":
                    continue
                if value is not None:
                    xml_parameter = self.xml_ify(str(value))
                    open_tag = open_tag + " " + att + '="' + xml_parameter + '"'
            return open_user_object_tag + "\n" + open_tag + ">"
        open_tag = "<" + self.xml_class
        for att, value in self.attributes.items():
            if value is not None:
                xml_parameter = self.xml_ify(str(value))
                open_tag = open_tag + " " + att + '="' + xml_parameter + '"'
        return open_tag + ">"

    @property
    def xml_close_tag(self) -> str:
        """
        The closing tag contains the name of the object wrapped in angle brackets.

        Example:
        </class_name>

        Returns:
            str: The closing tag of the object with all the attributes.
        """
        if self.tag or self.tooltip:
            return "</{0}>\n</UserObject>".format(self.xml_class)
        return "</{0}>".format(self.xml_class)

    @property
    def xml(self) -> str:
        """
        All drawpyo exportable classes contain an xml property that returns the formatted string of their XML output.

        This default version of the function assumes no inner value so it just returns the opening tag closed with a '/>'. Subclasses that require more printing overload this function with their own implementation.

        Example:
        <class_name attribute_name=attribute_value/>

        Returns:
            str: A single XML tag containing the object name, style attributes, and a closer.
        """
        return self.xml_open_tag[:-1] + " />"

    def xml_ify(self, parameter_string: str) -> str:
        return self.translate_txt(parameter_string, xmlize)

    @staticmethod
    def translate_txt(string: str, replacement_dict: Dict[str, str]) -> str:
        new_str = ""
        for char in string:
            if char in replacement_dict:
                new_str = new_str + replacement_dict[char]
            else:
                new_str = new_str + char
        return new_str
