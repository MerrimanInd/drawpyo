class XMLBase:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", id(self))
        self.xml_class = kwargs.get("xml_class", "xml_tag")

        # There's only one situation where XMLBase is called directly: to
        # create the two empty mxCell objects at the beginning of every
        # Draw.io diagram. The following declarations should be overwritten
        # in every other use case.
        self.parent = kwargs.get("parent", None)

    @property
    def attributes(self):
        return {'id': self.id, 'parent': self.parent}

    ###########################################################
    # XML Tags
    ###########################################################

    @property
    def xml_open_tag(self):
        open_tag = "<" + self.xml_class
        for (att, value) in self.attributes.items():
            if value is not None:
                open_tag = open_tag + " " + att + '="' + str(value) + '"'
        return open_tag + ">"

    @property
    def xml_close_tag(self):
        return "</{0}>".format(self.xml_class)

    @property
    def xml(self):
        open_tag = self.xml_open_tag
        return open_tag[:-1] + " />"