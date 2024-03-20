xmlize = {}
xmlize[">"] = "&gt;"
xmlize["<"] = "&gt;"
xmlize['"'] = "&#34;"
xmlize["&"] = "&#38;"
xmlize["'"] = "&#39;"

class XMLBase:
    """
    XMLBase is the base class for all exportable objects in drawpyo. This class defines a few useful properties that drawpyo needs to use to generate a Draw.io file.
    """
    def __init__(self, **kwargs):
        self._id = id(self)
        self.xml_class = kwargs.get("xml_class", "xml_tag")

        # There's only one situation where XMLBase is called directly: to
        # create the two empty mxCell objects at the beginning of every
        # Draw.io diagram. The following declarations should be overwritten
        # in every other use case.
        self.parent = kwargs.get("parent", None)

    @property
    def id(self):
        """
        id is a unique identifier. Draw.io generated diagrams use an ID many more characters but the app isn't picky when parsing so drawpyo just uses Python's built-in id() function as it guarantees unique identifiers.

        Returns:
            int: A unique identifier for the Draw.io object
        """
        return self._id
        

    @property
    def attributes(self):
        """
        The most basic attributes of a Draw.io object. Extended by subclasses.

        Returns:
            dict: A dict containing an 'id' and 'parent' object.
        """
        return {'id': self.id, 'parent': self.parent}

    ###########################################################
    # XML Tags
    ###########################################################

    @property
    def xml_open_tag(self):
        """
        The open tag contains the name of the object but also the attribute tags. This property function concatenates all the attributes in the class along with the opening and closing angle brackets and returns them as a string.
        
        Example:
        <class_name attribute_name=attribute_value>

        Returns:
            str: The opening tag of the object with all the attributes.
        """
        open_tag = "<" + self.xml_class
        for (att, value) in self.attributes.items():
            if value is not None:
                xml_parameter = self.xml_ify(str(value))
                open_tag = open_tag + " " + att + '="' + xml_parameter + '"'
        return open_tag + ">"

    @property
    def xml_close_tag(self):
        """
        The closing tag contains the name of the object wrapped in angle brackets.

        Example:
        </class_name>

        Returns:
            str: The closing tag of the object with all the attributes.
        """
        return "</{0}>".format(self.xml_class)

    @property
    def xml(self):
        """
        All drawpyo exportable classes contain an xml property that returns the formatted string of their XML output.
        
        This default version of the function assumes no inner value so it just returns the opening tag closed with a '/>'. Subclasses that require more printing overload this function with their own implementation.
        
        Example:
        <class_name attribute_name=attribute_value/>
        
        Returns:
            str: A single XML tag containing the object name, style attributes, and a closer.
        """
        open_tag = self.xml_open_tag
        return open_tag[:-1] + " />"
    
    def xml_ify(self, parameter_string):
        return parameter_string.translate(xmlize)