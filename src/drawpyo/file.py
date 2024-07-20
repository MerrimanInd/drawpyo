from .xml_base import XMLBase
from datetime import datetime
from os import path, makedirs
from sys import version_info
from .page import Page


class File(XMLBase):
    """The File class defines a Draw.io file, its properties, and the methods required for saving it."""

    def __init__(
        self,
        file_name="Drawpyo Diagram.drawio",
        file_path=path.join(path.expanduser("~"), "Drawpyo Charts"),
    ):
        """To initiate a File object, pass in a name and path or leave it to the defaults.

        Args:
            file_name (str, optional): The name of the file.
            file_path (str, optional): The location where the file will be saved.
        """

        super().__init__()

        self.pages = []
        self.file_name = file_name
        self.file_path = file_path

        # Attributes
        self.host = "Drawpyo"
        self.type = "device"
        self.version = "21.6.5"  # This is the version of the Draw.io spec
        self.xml_class = "mxfile"

    def __repr__(self):
        return f"drawpyo File - {self.file_name}"

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
        page._file = self
        self.pages.append(page)

    def remove_page(self, page):
        """Remove a page from the file. The page argument can be either a Page object, the integer number of the page, or the string name of the page.

        Args:
            page (drawpyo.diagram.Page or str or int): A Page object that's currently contained in the file
        """
        if isinstance(page, int):
            del self.pages[page]
        elif isinstance(page, str):
            for pg in self.pages:
                if pg.name == page:
                    self.pages.remove(pg)
        elif isinstance(page, Page):
            self.pages.remove(page)

    ###########################################################
    # File Properties
    ###########################################################

    @property
    def modified(self):
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    @property
    def agent(self):
        python_version = f"{version_info.major}.{version_info.minor}"
        drawpyo_version = f"0.01"
        return f"Python {python_version}, Drawpyo {drawpyo_version}"

    @property
    def etag(self):
        # etag is in the Draw.io spec but not sure how it's used or if I need to create it
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
        self.file_path = kwargs.get("file_path", self.file_path)

        self.file_name = kwargs.get("file_name", self.file_name)

        overwrite = kwargs.get("overwrite", True)
        if overwrite:
            write_mode = "w"
        else:
            write_mode = "x"

        if not path.exists(self.file_path):
            makedirs(self.file_path)

        with open(
            path.join(self.file_path, self.file_name), write_mode, encoding="utf-8"
        ) as f:
            f.write(self.xml)

        return path.join(self.file_path, self.file_name)
