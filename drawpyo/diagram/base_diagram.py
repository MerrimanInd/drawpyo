from ..xml_base import XMLBase



def import_shape_databases(self):
    # Import the shape and edge definitions
    from sys import version_info
    # toml path
    
    
    if version_info.minor < 11:
        import toml
    else:
        import tomllib

__all__ = ['DiagramBase']

class DiagramBase(XMLBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.page = kwargs.get("page", None)
        self.parent = kwargs.get("parent", None)
        
    @property
    def base_styles(self):
        return {
            None: ""}

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
        return {
            "html": self.html}
    
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
        base_styles = self.base_attribute_dict
        if '' in base_styles:
            del base_styles['']
        for attribute, value in self.style_attributes.items():
            if value is not None and not value == "":
                style_str = style_str + "{0}={1};".format(attribute, value)
            elif attribute in base_styles:
                style_str = style_str + base_styles.pop(attribute)
        for attribute in base_styles.values():
            style_str = style_str + attribute + ';'
        return style_str

    def style_str_from_dict(self, style_dict):
        #return ";".join(["{0}={1}".format(att,style) for (att,style) in style_dict.items()])
        return ";".join(["{0}={1}".format(att,style) for (att,style) in style_dict.items() if style != "" and style != None])
    
    @property
    def base_style_str(self):
        """
        This property returns the style string of the assigned base_style.
        This string will be in the format:
            attribute=value;attribute2=value

        Returns
        -------
        string
            The base style string.

        """
        return self.base_styles[self.base_style]
    
    def attribute_from_base(self, attribute):
        """
        This function returns a single attribute string from the base_style
        string. The attribute will be a string name nad the return will be that
        string name plus the assigned attribute:
            attribute returns "attribute=val"

        Parameters
        ----------
        attribute : string
            The name of the attribute to return.

        Returns
        -------
        string
            Attribute assignment string.

        """
        base_attribs = self.base_style_str.split(';')
        return next((attrib for attrib in base_attribs if attribute == attrib.split("=")[0]), None)
        
    @property
    def base_attribute_dict(self):
        """
        This function returns a dictionary of the base_style attributes. The
        dict keys will be the attribute names and the values will be the names
        plus the value.
        
        base_attribute_dict{"attribute": "attribute=value"}

        Returns
        -------
        dict
            A dict of the base_style attributes.

        """
        attr_strings = self.base_style_str.split(';')
        attr_keys = [attr_string.split('=')[0] for attr_string in attr_strings]
        return dict(zip(attr_keys, attr_strings))
            
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
        for attrib in style_str.split(';'):
            if "=" in attrib:
                a_name = attrib.split('=')[0]
                a_value = attrib.split('=')[1]
                if a_value.isdigit():
                    if "."  in a_value:
                        a_value = float(a_value)
                    else:
                        a_value = int(a_value)
                elif a_value == "True" or a_value == "False":
                    a_value = bool(a_value)
                    
                setattr(self, a_name, a_value)
                
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