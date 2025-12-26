from .xml_base import XMLBase
from .file import File
from .page import Page

from .utils.standard_colors import StandardColor
from .utils.color_scheme import ColorScheme
from .utils.logger import logger
from .utils.page_sizes import PageSize

from .drawio_import import load_diagram

from . import utils
from . import diagram
from . import diagram_types
from . import drawio_import

__all__ = [
    XMLBase,
    File,
    Page,
    StandardColor,
    ColorScheme,
    PageSize,
    logger,
    utils,
    diagram,
    diagram_types,
    drawio_import,
    load_diagram,
]

__version__ = "0.2.4"
