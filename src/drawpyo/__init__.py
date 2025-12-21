from .xml_base import XMLBase
from .file import File
from .page import Page

from .utils.standard_colors import StandardColor
from .utils.color_scheme import ColorScheme
from .utils.logger import logger

from . import utils
from . import diagram
from . import diagram_types

__all__ = [
    XMLBase,
    File,
    Page,
    StandardColor,
    ColorScheme,
    logger,
    utils,
    diagram,
    diagram_types,
]

__version__ = "0.2.4"
