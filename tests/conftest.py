"""
Common fixtures for all drawpyo tests.
"""

import pytest
from pathlib import Path
import drawpyo


@pytest.fixture
def empty_file() -> drawpyo.File:
    """Creates an empty File object with no pages"""
    return drawpyo.File()


@pytest.fixture
def file_with_name() -> drawpyo.File:
    """Creates a File object with the given name"""
    return drawpyo.File(file_name="Test Name.drawio")


@pytest.fixture
def empty_page() -> drawpyo.Page:
    """Creates a blank page with no file association"""
    return drawpyo.Page()


@pytest.fixture
def basic_object(empty_page: drawpyo.Page) -> drawpyo.diagram.Object:
    """Creates a basic object on the page"""
    return drawpyo.diagram.Object(
        page=empty_page,
        value="Test Object",
        position=(100, 100),
        width=120,
        height=80,
    )


@pytest.fixture
def test_output_dir(tmp_path: Path) -> Path:
    """Creates a temporary directory for test files"""
    output_dir = tmp_path / "test_output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def xml_base() -> drawpyo.XMLBase:
    """Creates a basic XMLBase object"""
    return drawpyo.XMLBase()


@pytest.fixture
def xml_base_with_class() -> drawpyo.XMLBase:
    """Creates an XMLBase object with a custom class"""
    return drawpyo.XMLBase(xml_class="mxCell")


@pytest.fixture
def basic_color_scheme() -> drawpyo.ColorScheme:
    """Creates a basic color scheme"""
    return drawpyo.ColorScheme(
        fill_color="#DAE8FC",
        stroke_color="#6C8EBF",
        font_color="#000000",
    )
