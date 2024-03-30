import drawpyo
from os import path
import xml.etree.ElementTree as ET


def test_file_init():
    user_path = path.join(path.expanduser("~"), "Drawpyo Charts")
    test_file = drawpyo.File(file_name="Test Name.drawio")
    assert test_file.file_name == "Test Name.drawio"
    assert test_file.file_path == user_path

    assert len(test_file.pages) == 0
    assert test_file.host == "Drawpyo"
    assert test_file.type == "device"
    assert test_file.version == "21.6.5"
    assert test_file.xml_class == "mxfile"


def test_file_pages():
    test_file = drawpyo.File()

    # Create a page without a file then add it to the file
    page_1 = drawpyo.Page()
    test_file.add_page(page_1)
    # Check if file is added to the page and vice versa
    assert page_1.file == test_file
    assert len(test_file.pages) == 1

    # Create some more pages then delete them in a variety of ways
    page_2 = drawpyo.Page(file=test_file, name="Page-2")
    page_3 = drawpyo.Page(file=test_file)
    page_4 = drawpyo.Page(file=test_file)
    assert len(test_file.pages) == 4

    test_file.remove_page(page_1)
    assert len(test_file.pages) == 3

    test_file.remove_page("Page-2")
    assert len(test_file.pages) == 2

    test_file.remove_page(0)
    assert len(test_file.pages) == 1

    page_4.remove()
    assert len(test_file.pages) == 0


def test_file_write(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()

    # Create a File and Page object
    test_file = drawpyo.File(
        file_name="test_file.drawio",
        file_path=d,
    )
    page_1 = drawpyo.Page(file=test_file)

    # Write the File object
    f = test_file.write()
    assert path.isfile(f)

    with open(f) as test_file:
        tree = ET.parse(test_file)
        root = tree.getroot()
        assert root.tag == "mxfile"
