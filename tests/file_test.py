import drawpyo
from pathlib import Path
import xml.etree.ElementTree as ET
import pytest


@pytest.fixture
def empty_file() -> drawpyo.File:
    return drawpyo.File()


@pytest.fixture
def file_with_name() -> drawpyo.File:
    return drawpyo.File(file_name="Test Name.drawio")


def test_file_init_default_values(file_with_name) -> None:
    user_path = Path.home() / "Drawpyo Charts"
    assert file_with_name.file_name == "Test Name.drawio"
    assert file_with_name.file_path == str(user_path)
    assert len(file_with_name.pages) == 0
    assert file_with_name.host == "Drawpyo"
    assert file_with_name.type == "device"
    assert file_with_name.version == "21.6.5"
    assert file_with_name.xml_class == "mxfile"


def test_file_add_page(empty_file) -> None:
    page = drawpyo.Page()
    empty_file.add_page(page)
    
    assert page.file == empty_file
    assert len(empty_file.pages) == 1
    assert empty_file.pages[0] == page


def test_file_create_page_with_file(empty_file) -> None:
    page = drawpyo.Page(file=empty_file, name="Page-2")
    
    assert page.file == empty_file
    assert len(empty_file.pages) == 1
    assert page.name == "Page-2"


def test_file_remove_page_by_object(empty_file) -> None:
    page_1 = drawpyo.Page(file=empty_file)
    page_2 = drawpyo.Page(file=empty_file)
    page_3 = drawpyo.Page(file=empty_file)
    
    assert len(empty_file.pages) == 3
    
    empty_file.remove_page(page_1)
    assert len(empty_file.pages) == 2
    assert page_2 in empty_file.pages
    assert page_3 in empty_file.pages


def test_file_remove_page_by_name(empty_file) -> None:
    drawpyo.Page(file=empty_file, name="Page-1")
    drawpyo.Page(file=empty_file, name="Page-2")
    
    assert len(empty_file.pages) == 2
    
    empty_file.remove_page("Page-1")
    assert len(empty_file.pages) == 1
    assert empty_file.pages[0].name == "Page-2"


def test_file_remove_page_by_index(empty_file) -> None:
    page_1 = drawpyo.Page(file=empty_file)
    page_2 = drawpyo.Page(file=empty_file)
    
    assert len(empty_file.pages) == 2
    
    empty_file.remove_page(0)
    assert len(empty_file.pages) == 1
    assert empty_file.pages[0] == page_2


def test_page_remove_from_file(empty_file) -> None:
    page = drawpyo.Page(file=empty_file)
    
    assert len(empty_file.pages) == 1
    
    page.remove()
    assert len(empty_file.pages) == 0


def test_file_write(tmp_path: Path) -> None:
    output_dir = tmp_path / "sub"
    output_dir.mkdir()

    test_file = drawpyo.File(
        file_name="test_file.drawio",
        file_path=output_dir,
    )
    drawpyo.Page(file=test_file)

    file_path = test_file.write()
    assert Path(file_path).is_file()
    assert file_path == str(output_dir / "test_file.drawio")

    with open(file_path) as f:
        tree = ET.parse(f)
        root = tree.getroot()
        assert root.tag == "mxfile"

