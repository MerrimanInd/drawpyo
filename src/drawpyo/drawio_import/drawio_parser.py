import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field

from .raw import RawMxCell, RawGeometry
from drawpyo import logger
from drawpyo.diagram import Object, Edge, DiagramBase


# -----------------------------
# Public Data Structure
# -----------------------------
@dataclass
class ParsedDiagram:
    """High-level diagram representation with convenient access methods."""

    shapes: List[DiagramBase] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)
    _id_map: Dict[str, DiagramBase] = field(default_factory=dict, repr=False)

    def get_by_id(self, cell_id: str) -> Optional[DiagramBase]:
        """Get an element by its Draw.io cell ID.

        Args:
            cell_id: The Draw.io cell ID

        Returns:
            The diagram element or None if not found
        """
        return self._id_map.get(cell_id)

    def get_roots(self) -> List[DiagramBase]:
        """Get top-level shapes (shapes that aren't connected as targets).

        Returns:
            List of root-level shapes
        """
        target_shapes = {edge.target for edge in self.edges if edge.target}
        return [shape for shape in self.shapes if shape not in target_shapes]

    def find_shapes_by_value(
        self, value: str, exact: bool = False
    ) -> List[DiagramBase]:
        """Find shapes by their text content.

        Args:
            value: Text to search for
            exact: If True, requires exact match; if False, does substring match

        Returns:
            List of matching shapes
        """
        if exact:
            return [s for s in self.shapes if s.value == value]
        else:
            return [s for s in self.shapes if value in (s.value or "")]

    def get_connected_edges(self, shape: DiagramBase) -> List[Edge]:
        """Get all edges connected to a shape.

        Args:
            shape: The shape to find connections for

        Returns:
            List of edges connected to the shape
        """
        return [e for e in self.edges if e.source == shape or e.target == shape]

    def get_outgoing_edges(self, shape: DiagramBase) -> List[Edge]:
        """Get edges originating from a shape.

        Args:
            shape: The source shape

        Returns:
            List of outgoing edges
        """
        return [e for e in self.edges if e.source == shape]

    def get_incoming_edges(self, shape: DiagramBase) -> List[Edge]:
        """Get edges pointing to a shape.

        Args:
            shape: The target shape

        Returns:
            List of incoming edges
        """
        return [e for e in self.edges if e.target == shape]

    @property
    def element_count(self) -> int:
        """Total number of elements (shapes + edges)."""
        return len(self.shapes) + len(self.edges)


# -----------------------------
# XML Parsing
# -----------------------------
def _parse_drawio_xml(xml_string: str) -> Dict[str, RawMxCell]:
    """Parses draw.io XML into a dictionary of RawMxCell objects keyed by their IDs.

    Args:
        xml_string: Draw.io XML content

    Returns:
        Dictionary mapping cell IDs to RawMxCell objects

    Raises:
        ET.ParseError: If XML is malformed
    """
    root = ET.fromstring(xml_string)
    cells: Dict[str, RawMxCell] = {}

    for cell_elem in root.findall(".//mxCell"):
        cell_id = cell_elem.get("id")
        if not cell_id:
            continue

        cell = RawMxCell(
            id=cell_id,
            parent=cell_elem.get("parent"),
            value=cell_elem.get("value"),
            style=cell_elem.get("style"),
            is_vertex=cell_elem.get("vertex") == "1",
            is_edge=cell_elem.get("edge") == "1",
            source=cell_elem.get("source"),
            target=cell_elem.get("target"),
        )

        geo_elem = cell_elem.find("mxGeometry")
        if geo_elem is not None:
            points = []

            points_array = geo_elem.find("Array[@as='points']")
            if points_array is not None:
                for point_elem in points_array.findall("mxPoint"):
                    x = point_elem.get("x")
                    y = point_elem.get("y")
                    if x is not None and y is not None:
                        points.append((float(x), float(y)))

            cell.geometry = RawGeometry(
                x=float(geo_elem.get("x", 0)) if geo_elem.get("x") else None,
                y=float(geo_elem.get("y", 0)) if geo_elem.get("y") else None,
                width=(
                    float(geo_elem.get("width", 0)) if geo_elem.get("width") else None
                ),
                height=(
                    float(geo_elem.get("height", 0)) if geo_elem.get("height") else None
                ),
                relative=geo_elem.get("relative") == "1",
                points=points,
            )

        cells[cell.id] = cell

    return cells


def _parse_drawio_file(file_path: str) -> Dict[str, RawMxCell]:
    """Loads a Draw.io file and parses it into RawMxCell objects.

    Args:
        file_path: Path to the .drawio file

    Returns:
        Dictionary mapping cell IDs to RawMxCell objects

    Raises:
        FileNotFoundError: If file doesn't exist
        ET.ParseError: If XML is malformed
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    xml_content = path.read_text(encoding="utf-8")
    return _parse_drawio_xml(xml_content)


# -----------------------------
# Vertex / Edge Builder
# -----------------------------
def _vertex_from_raw(cell: RawMxCell) -> DiagramBase:
    """Create a drawpyo DiagramBase object from a RawMxCell vertex.

    Args:
        cell: Raw cell data

    Returns:
        DiagramBase object representing the shape
    """
    obj = Object(value=cell.value)

    if cell.style:
        obj.apply_style_string(cell.style)

    if cell.geometry:
        obj.geometry.x = cell.geometry.x
        obj.geometry.y = cell.geometry.y
        obj.geometry.width = cell.geometry.width
        obj.geometry.height = cell.geometry.height

    return obj


def _build_vertices(raw_cells: Dict[str, RawMxCell]) -> Dict[str, DiagramBase]:
    """Build all vertex objects from raw cells.

    Args:
        raw_cells: Dictionary of raw cell data

    Returns:
        Dictionary mapping cell IDs to DiagramBase objects
    """
    elements = {}
    for cell in raw_cells.values():
        if cell.is_vertex:
            element = _vertex_from_raw(cell)
            elements[cell.id] = element
    return elements


def _edge_from_raw(cell: RawMxCell, elements: Dict[str, DiagramBase]) -> Edge:
    """Create a drawpyo Edge object from a RawMxCell edge.

    Args:
        cell: Raw cell data for the edge
        elements: Dictionary of already-built elements for linking

    Returns:
        Edge object with source/target connections
    """
    e = Edge()

    if cell.style:
        e.apply_style_string(cell.style)

    # Source/Target linking
    if cell.source in elements:
        e.source = elements[cell.source]
    if cell.target in elements:
        e.target = elements[cell.target]

    if cell.geometry:
        e.geometry.relative = cell.geometry.relative
        for x, y in cell.geometry.points:
            e.add_point(int(x), int(y))

    e.label = cell.value

    return e


def _build_edges(raw_cells: Dict[str, RawMxCell], elements: Dict[str, DiagramBase]):
    """Build all edge objects and add them to the elements dictionary.

    Args:
        raw_cells: Dictionary of raw cell data
        elements: Dictionary to add edges to (modified in place)
    """
    for cell in raw_cells.values():
        if cell.is_edge:
            edge = _edge_from_raw(cell, elements)
            elements[cell.id] = edge


def _build_diagram(raw_cells: Dict[str, RawMxCell]) -> ParsedDiagram:
    """Convert RawMxCell dictionary into a structured ParsedDiagram.

    Args:
        raw_cells: Dictionary of raw cell data

    Returns:
        ParsedDiagram with organized shapes and edges
    """
    # Build all elements
    elements = _build_vertices(raw_cells)
    _build_edges(raw_cells, elements)

    # Separate into shapes and edges
    shapes = [e for e in elements.values() if isinstance(e, Object)]
    edges = [e for e in elements.values() if isinstance(e, Edge)]

    return ParsedDiagram(shapes=shapes, edges=edges, _id_map=elements)


# -----------------------------
# Public API
# -----------------------------
def load_diagram(file_path: str) -> ParsedDiagram:
    """Load a Draw.io file into a structured diagram object.

    This is the main entry point for parsing Draw.io files. It reads the file,
    parses the XML, and returns a high-level diagram structure with convenient
    access methods.

    Args:
        file_path: Path to the .drawio or .xml file

    Returns:
        ParsedDiagram containing shapes, edges, and convenience methods

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the XML is invalid or not a valid Draw.io file

    Example:
        >>> diagram = load_diagram("my_flowchart.drawio")
        >>> print(f"Found {len(diagram.shapes)} shapes and {len(diagram.edges)} edges")
        >>> for shape in diagram.shapes:
        ...     print(f"Shape: {shape.value}")
    """
    try:
        logger.info(f"📂 Loading .drawio: '{file_path}'")
        raw_cells = _parse_drawio_file(file_path)
        if not raw_cells:
            raise ValueError("No diagram elements found in file")
        return _build_diagram(raw_cells)
    except ET.ParseError as e:
        raise ValueError(f"Invalid Draw.io XML format: {e}")
