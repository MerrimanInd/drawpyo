from .xml_base import XMLBase
from datetime import datetime
from os import path, makedirs

class File(XMLBase):
    """The File class defines a Draw.io file, its properties, and the methods required for saving it.
    """

    def __init__(self, file_name="Drawpyo Diagram.drawio", file_path=path.join(path.expanduser('~'), "Drawpyo Charts")):
        """To initiate a File object, pass in a name and path or leave it to the defaults.

        Args:
            file_name (str, optional): The name of the file.
            file_path (str, optional): The location where the file will be saved.
        """


        super().__init__()
        # self.file_name = kwargs.get(
        #     "file_name", "Draw.pyo Generated page.drawio"
        # )
        # self.file_path = kwargs.get(
        #     "file_path", path.join(path.expanduser('~'), "Drawpyo Charts")
        # )
        # self.pages = kwargs.get("pages", [])

        self.file_name = file_name
        self.file_path = file_path

        # Attributes
        self.host = "Drawpyo"
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
        """Add a page to the file.

        Args:
            page (drawpyo.diagram.Page): A Page object
        """
        self.pages.append(page)

    # TODO make this take a page number, name as string, or object
    def remove_page(self, page):
        """Remove a page from the file.

        Args:
            page (drawpyo.diagram.Page): A Page object that's currently contained in the file
        """
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
        return "Python v3.10, Drawpyo 0.1"

    @property
    def etag(self):
        # TODO determine if I need to calculate an etag
        return None

    ###########################################################
    # XML Generation
    ###########################################################

    @property
    def xml(self):
        """This function goes through each page in the file, retrieves its XML, and appends it to a list, then wraps that list in the file's open and close tags.

        Returns:
            str: The XML data for the file and all the pages in it
        """
        xml_string = self.xml_open_tag
        for diag in self.pages:
            xml_string = xml_string + "\n  " + diag.xml
        xml_string = xml_string + "\n" + self.xml_close_tag
        return xml_string

    ###########################################################
    # File Handling
    ###########################################################
    def write(self, **kwargs):
        """This function write the file to disc at the path and name specified.
        
        Args:
            file_path (str, opt): The path to save the file in
            file_name (str, opt): The name of the file
            overwrite (bool, opt): Whether to overwrite an existing file or not
        """

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