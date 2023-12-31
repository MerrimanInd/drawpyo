from .xml_base import XMLBase
from datetime import datetime
from os import path, makedirs, getcwd


class File(XMLBase):
    def __init__(self, **kwargs):
        super().__init__()
        self.file_name = kwargs.get(
            "file_name", "Draw.pyo Generated page.drawio"
        )
        self.file_path = kwargs.get(
            "file_path", r"C:/"
        )
        self.pages = kwargs.get("pages", [])

        # Attributes
        self.host = "Draw.pyo"
        self.type = "device"
        self.version = "21.6.5"
        self.xml_class = "mxfile"

    @property
    def attributes(self):
        return {
            "host": self.host,
            "modified": self.modified,
            "agent": self.agent,
            "etag": self.etag,
            "version": self.version,
            "type": self.type,
        }

    def add_page(self, page):
        self.pages.append(page)

    def remove_page(self, page):
        self.pages.remove(page)

    ###########################################################
    # File Properties
    ###########################################################

    @property
    def modified(self):
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    @property
    def agent(self):
        # TODO return Python and Draw.pyo version
        return "Python v3.10, Draw.pyo 0.1"

    @property
    def etag(self):
        # TODO determine if I need to calculate an etag
        return None

    ###########################################################
    # XML Generation
    ###########################################################

    @property
    def xml(self):
        xml_string = self.xml_open_tag
        for diag in self.pages:
            xml_string = xml_string + "\n  " + diag.xml
        xml_string = xml_string + "\n" + self.xml_close_tag
        return xml_string

    ###########################################################
    # File Handling
    ###########################################################
    def write(self, **kwargs):

        # Check if file_path or file_name were passed in, or are preexisting
        self.file_path = kwargs.get(
            "file_path", self.file_path
        )

        self.file_name = kwargs.get(
            "file_name", self.file_name
        )


        overwrite = kwargs.get("overwrite", True)
        if overwrite:
            write_mode = "w"
        else:
            write_mode = "x"

        if not path.exists(self.file_path):
            makedirs(self.file_path)

        f = open(path.join(self.file_path, self.file_name), write_mode, encoding="utf-8")
        f.write(self.xml)
        f.close

    def read(self, file):
        # TODO read a Drawio file into the Python object structure
        # This function is a long way away as most or all of Draw.io's
        # functionality will need to be supported in the library to work.
        pass