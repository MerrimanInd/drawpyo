from .xml_base import XMLBase
from .file import File
from .page import Page

from .utils.standard_colors import StandardColor
from .utils.color_scheme import ColorScheme
from .utils.logger import logger
from .utils.page_sizes import PageSize

from .drawio_import import load_diagram, load_mxlibrary

from . import utils
from . import diagram
from . import diagram_types
from . import drawio_import

def register_mxlibrary(name: str, source: str) -> None:
    """
    Register an mxlibrary from a file path or URL as a named library.
    
    This allows you to import external shape libraries (like Azure icons, AWS icons, etc.)
    and use them with the object_from_library function just like built-in libraries.
    
    Args:
        name: The name to register the library under (e.g., "azure", "aws")
        source: Local file path or HTTP/HTTPS URL to the mxlibrary XML file
        
    Raises:
        ValueError: If the library cannot be loaded or contains no valid shapes
        FileNotFoundError: If the local file doesn't exist
        
    Example:
        >>> import drawpyo
        >>> # Register Azure icons library
        >>> drawpyo.register_mxlibrary(
        ...     "azure",
        ...     "https://example.com/azure-icons.xml"
        ... )
        >>> # Use shapes from the registered library
        >>> file = drawpyo.File()
        >>> page = drawpyo.Page(file=file)
        >>> icon = drawpyo.diagram.object_from_library(
        ...     library="azure",
        ...     obj_name="Virtual-Machine",
        ...     page=page
        ... )
    """
    from .diagram.objects import base_libraries
    
    shapes = load_mxlibrary(source)
    
    if not shapes:
        raise ValueError(
            f"No valid shapes found in mxlibrary from '{source}'. "
            f"Cannot register empty library '{name}'."
        )
    
    base_libraries[name] = shapes
    logger.info(
        f"Successfully registered mxlibrary '{name}' with {len(shapes)} shapes"
    )

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
    load_mxlibrary,
    register_mxlibrary,
]

__version__ = "0.2.4"
