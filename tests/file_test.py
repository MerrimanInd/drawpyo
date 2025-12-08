"""
Tests for the File class.

A File is a Draw.io file (.drawio), which can contain one or more diagram pages.
"""

import drawpyo
from pathlib import Path
import xml.etree.ElementTree as ET
import pytest


class TestFileInit:
    """File object initialization tests"""

    def test_default_values(self, empty_file: drawpyo.File) -> None:
        """Checks default values when creating an empty file"""
        user_path = Path.home() / "Drawpyo Charts"
        assert empty_file.file_path == str(user_path)
        assert len(empty_file.pages) == 0
        assert empty_file.host == "Drawpyo"
        assert empty_file.type == "device"
        assert empty_file.xml_class == "mxfile"

    def test_with_custom_name(self, file_with_name: drawpyo.File) -> None:
        """Checks if a file with a custom name is created"""
        assert file_with_name.file_name == "Test Name.drawio"

    def test_with_custom_path(self, tmp_path: Path) -> None:
        """Checks if a file with a custom path has been created"""
        file = drawpyo.File(file_name="test.drawio", file_path=tmp_path)
        assert str(file.file_path) == str(tmp_path)

    def test_version_attribute(self, empty_file: drawpyo.File) -> None:
        """Checks for the presence of the version attribute"""
        assert hasattr(empty_file, "version")
        assert empty_file.version == "21.6.5"


class TestFileAddPage:
    """Tests adding pages to a file"""

    def test_add_page_basic(self, empty_file: drawpyo.File) -> None:
        """Checks basic page addition"""
        page = drawpyo.Page()
        empty_file.add_page(page)

        assert page.file == empty_file
        assert len(empty_file.pages) == 1
        assert empty_file.pages[0] == page

    def test_create_page_with_file(self, empty_file: drawpyo.File) -> None:
        """Checks if a page is created with a file link"""
        page = drawpyo.Page(file=empty_file, name="Page-2")

        assert page.file == empty_file
        assert len(empty_file.pages) == 1
        assert page.name == "Page-2"

    def test_add_multiple_pages(self, empty_file: drawpyo.File) -> None:
        """Checks for adding multiple pages"""
        page_1 = drawpyo.Page(file=empty_file, name="Page-1")
        page_2 = drawpyo.Page(file=empty_file, name="Page-2")
        page_3 = drawpyo.Page(file=empty_file, name="Page-3")

        assert len(empty_file.pages) == 3
        assert empty_file.pages[0] == page_1
        assert empty_file.pages[1] == page_2
        assert empty_file.pages[2] == page_3


class TestFileRemovePage:
    """Tests for deleting pages from a file"""

    def test_remove_page_by_object(self, empty_file: drawpyo.File) -> None:
        """Checks for page deletion by object"""
        page_1 = drawpyo.Page(file=empty_file)
        page_2 = drawpyo.Page(file=empty_file)
        page_3 = drawpyo.Page(file=empty_file)

        assert len(empty_file.pages) == 3

        empty_file.remove_page(page_1)
        assert len(empty_file.pages) == 2
        assert page_2 in empty_file.pages
        assert page_3 in empty_file.pages

    def test_remove_page_by_name(self, empty_file: drawpyo.File) -> None:
        """Checks for deletion of a page by name"""
        drawpyo.Page(file=empty_file, name="Page-1")
        drawpyo.Page(file=empty_file, name="Page-2")

        assert len(empty_file.pages) == 2

        empty_file.remove_page("Page-1")
        assert len(empty_file.pages) == 1
        assert empty_file.pages[0].name == "Page-2"

    def test_remove_page_by_index(self, empty_file: drawpyo.File) -> None:
        """Checks for page deletion by index"""
        page_1 = drawpyo.Page(file=empty_file)
        page_2 = drawpyo.Page(file=empty_file)

        assert len(empty_file.pages) == 2

        empty_file.remove_page(0)
        assert len(empty_file.pages) == 1
        assert empty_file.pages[0] == page_2

    def test_page_remove_from_file(self, empty_file: drawpyo.File) -> None:
        """Checks if a page has been deleted via the page method"""
        page = drawpyo.Page(file=empty_file)

        assert len(empty_file.pages) == 1

        page.remove()
        assert len(empty_file.pages) == 0

    def test_remove_all_pages(self, empty_file: drawpyo.File) -> None:
        """Checks if all pages have been deleted"""
        drawpyo.Page(file=empty_file, name="Page-1")
        drawpyo.Page(file=empty_file, name="Page-2")
        drawpyo.Page(file=empty_file, name="Page-3")

        assert len(empty_file.pages) == 3

        empty_file.remove_page(0)
        empty_file.remove_page(0)
        empty_file.remove_page(0)

        assert len(empty_file.pages) == 0


class TestFileWrite:
    """Tests for writing a file to disk"""

    def test_write_basic(self, test_output_dir: Path) -> None:
        """Checks the base record of a file"""
        test_file = drawpyo.File(
            file_name="test_file.drawio",
            file_path=test_output_dir,
        )
        drawpyo.Page(file=test_file)

        file_path = test_file.write()
        assert Path(file_path).is_file()
        assert file_path == str(test_output_dir / "test_file.drawio")

    def test_write_xml_structure(self, test_output_dir: Path) -> None:
        """Checks the correctness of the XML structure of the written file"""
        test_file = drawpyo.File(
            file_name="test_file.drawio",
            file_path=test_output_dir,
        )
        drawpyo.Page(file=test_file)

        file_path = test_file.write()

        with open(file_path) as f:
            tree = ET.parse(f)
            root = tree.getroot()
            assert root.tag == "mxfile"

    def test_write_with_multiple_pages(self, test_output_dir: Path) -> None:
        """Checks a file record with multiple pages"""
        test_file = drawpyo.File(
            file_name="multi_page.drawio",
            file_path=test_output_dir,
        )
        drawpyo.Page(file=test_file, name="Page-1")
        drawpyo.Page(file=test_file, name="Page-2")
        drawpyo.Page(file=test_file, name="Page-3")

        file_path = test_file.write()
        assert Path(file_path).is_file()

        with open(file_path) as f:
            tree = ET.parse(f)
            root = tree.getroot()
            diagrams = root.findall("diagram")
            assert len(diagrams) == 3

    def test_write_creates_directory(self, tmp_path: Path) -> None:
        """Checks for directory creation when writing a file"""
        new_dir = tmp_path / "new" / "nested" / "dir"
        test_file = drawpyo.File(
            file_name="test.drawio",
            file_path=new_dir,
        )
        drawpyo.Page(file=test_file)

        file_path = test_file.write()
        assert Path(file_path).is_file()
        assert Path(file_path).parent == new_dir
