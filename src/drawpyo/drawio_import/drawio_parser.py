import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from drawpyo import Page, logger
from drawpyo.diagram import DiagramBase, Edge, Object

from .raw import RawGeometry, RawMxCell


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

    @property
    def element_count(self) -> int:
        """Total number of elements (shapes + edges)."""
        return len(self.shapes) + len(self.edges)

    def add_to(
        self,
        page: Page,
        offset: tuple = (0, 0),
        include_shapes: bool = True,
        include_edges: bool = True,
    ) -> None:
        """Attach diagram elements to a page, optionally applying an offset.

        Args:
            page: Target Page instance to attach elements to
            offset: (dx, dy) applied to top-level objects and edge points
            include_shapes: Whether to add shapes to the page
            include_edges: Whether to add edges to the page
        """
        dx, dy = offset

        if include_shapes:
            for shape in self.shapes:
                _update_page_links(shape, page)
                shape.page = page
            if dx or dy:
                for shape in self.shapes:
                    if isinstance(shape, Object) and shape.parent is None:
                        shape.position = (
                            shape.position[0] + dx,
                            shape.position[1] + dy,
                        )

        if include_edges:
            for edge in self.edges:
                _update_page_links(edge, page)
                edge.page = page
            if dx or dy:
                for edge in self.edges:
                    for point in edge.geometry.points:
                        point.x = point.x + dx
                        point.y = point.y + dy


# -----------------------------
# XML Parsing
# -----------------------------
def _build_raw_cell(
    cell_elem: ET.Element, cell_id_override: Optional[str] = None
) -> Optional[RawMxCell]:
    """
    Builds a RawMxCell object from an XML element.

    Args:
        cell_elem: The XML element representing a cell.
        cell_id_override: An optional override for the cell ID.

    Returns:
        A RawMxCell object or None if the cell ID is missing.
    """
    cell_id = cell_id_override or cell_elem.get("id")
    if not cell_id:
        return None

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
            x=float(geo_elem.get("x")) if geo_elem.get("x") else None,
            y=float(geo_elem.get("y")) if geo_elem.get("y") else None,
            width=float(geo_elem.get("width")) if geo_elem.get("width") else None,
            height=(float(geo_elem.get("height")) if geo_elem.get("height") else None),
            relative=geo_elem.get("relative") == "1",
            points=points,
        )

    return cell


def _update_page_links(element: DiagramBase, page: Page) -> None:
    """
    Updates the 'link' attribute of user object attributes if it points to a Draw.io page.

    Args:
        element: The diagram element (shape or edge) to update.
        page: The target Page instance.
    """
    user_attrs = getattr(element, "user_object_attributes", None)
    if not user_attrs:
        return
    link = user_attrs.get("link")
    if link and link.startswith("data:page/id,"):
        user_attrs["link"] = f"data:page/id,{page.diagram.id}"


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

    for wrapper_tag in ("object", "UserObject"):
        for wrapper_elem in root.findall(f".//{wrapper_tag}"):
            cell_elem = wrapper_elem.find("mxCell")
            if cell_elem is None:
                continue

            wrapper_attrs = dict(wrapper_elem.attrib)
            cell_id = cell_elem.get("id") or wrapper_attrs.get("id")
            cell = _build_raw_cell(cell_elem, cell_id_override=cell_id)
            if cell is None:
                continue

            if wrapper_tag == "UserObject":
                cell.user_object_attributes = wrapper_attrs
            else:
                cell.object_attributes = wrapper_attrs

            cells[cell.id] = cell

    for cell_elem in root.findall(".//mxCell"):
        cell = _build_raw_cell(cell_elem)
        if cell is None or cell.id in cells:
            continue

        cells[cell.id] = cell

    # Link parent -> children (required for nested objects)
    for cell in cells.values():
        if cell.parent and cell.parent in cells:
            cells[cell.parent].children.append(cell.id)

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
def _build_vertices(raw_cells: Dict[str, RawMxCell]) -> Dict[str, DiagramBase]:
    """Build all vertex objects from raw cells.

    Args:
        raw_cells: Dictionary of raw cell data

    Returns:
        Dictionary mapping cell IDs to DiagramBase objects
    """
    elements: Dict[str, DiagramBase] = {}

    for cell in raw_cells.values():
        if not cell.is_vertex:
            continue

        obj = Object(
            id=cell.id,
            object_attributes=cell.object_attributes,
            user_object_attributes=cell.user_object_attributes,
        )
        if cell.style:
            obj.apply_style_string(cell.style)

        elements[cell.id] = obj

    return elements


def _attach_children(raw_cells: Dict[str, RawMxCell], elements: Dict[str, DiagramBase]):
    """Attach child vertices to their parent vertices based on Draw.io hierarchy."""
    for cell in raw_cells.values():
        if not cell.is_vertex:
            continue
        if cell.parent in ("0", "1", None):
            continue
        if cell.parent in elements:
            parent_obj: Object = elements[cell.parent]
            child_obj: Object = elements[cell.id]
            parent_obj.add_object(child_obj)


def _apply_geometry_recursive(
    cell_id: str,
    raw_cells: Dict[str, RawMxCell],
    elements: Dict[str, DiagramBase],
):
    """Apply geometry recursively, preserving relative positions.

    Args:
        cell_id: The ID of the current cell to process.
        raw_cells: Dictionary of all raw cell data.
        elements: Dictionary of DiagramBase objects, to which geometry will be applied.
    """
    cell = raw_cells[cell_id]
    obj = elements[cell_id]

    if cell.geometry:
        # Store relative position to parent, not absolute
        obj.position_rel_to_parent = (
            cell.geometry.x or 0,
            cell.geometry.y or 0,
        )
        obj.width = cell.geometry.width or obj.width
        obj.height = cell.geometry.height or obj.height

    for child_id in cell.children:
        if child_id in elements:
            _apply_geometry_recursive(child_id, raw_cells, elements)


def _build_edges(raw_cells: Dict[str, RawMxCell], elements: Dict[str, DiagramBase]):
    """Build all edge objects and add them to the elements dictionary.

    Args:
        raw_cells: Dictionary of raw cell data
        elements: Dictionary to add edges to (modified in place)
    """
    for cell in raw_cells.values():
        if not cell.is_edge:
            continue

        e = Edge(
            id=cell.id,
            object_attributes=cell.object_attributes,
            user_object_attributes=cell.user_object_attributes,
        )
        if cell.style:
            e.apply_style_string(cell.style)

        if cell.source in elements:
            e.source = elements[cell.source]
        if cell.target in elements:
            e.target = elements[cell.target]

        if cell.geometry:
            e.geometry.relative = cell.geometry.relative
            for x, y in cell.geometry.points:
                e.add_point(int(x), int(y))

        e.label = cell.value
        elements[cell.id] = e


# -----------------------------
# Diagram Builder
# -----------------------------
def _build_diagram(raw_cells: Dict[str, RawMxCell]) -> ParsedDiagram:
    """Convert RawMxCell dictionary into a structured ParsedDiagram.

    Args:
        raw_cells: Dictionary of raw cell data

    Returns:
        ParsedDiagram with organized shapes and edges
    """
    elements = _build_vertices(raw_cells)
    _attach_children(raw_cells, elements)

    # Apply geometry starting from layer roots (parent == "1")
    root_ids = [
        cell.id for cell in raw_cells.values() if cell.is_vertex and cell.parent == "1"
    ]

    for root_id in root_ids:
        _apply_geometry_recursive(root_id, raw_cells, elements)

    _build_edges(raw_cells, elements)

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
    """
    try:
        logger.info(f"📂 Loading .drawio: '{file_path}'")
        raw_cells = _parse_drawio_file(file_path)
        if not raw_cells:
            raise ValueError("No diagram elements found in file")
        return _build_diagram(raw_cells)
    except ET.ParseError as e:
        raise ValueError(f"Invalid Draw.io XML format: {e}")
