import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict

from .raw import RawMxCell, RawGeometry
from drawpyo.diagram import Object, Edge, DiagramBase


# -----------------------------
# XML Parsing
# -----------------------------
def parse_drawio_xml(xml_string: str) -> Dict[str, RawMxCell]:
    """Parses draw.io XML into a dictionary of RawMxCell objects keyed by their IDs."""
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
            for point_elem in geo_elem.findall("mxPoint"):
                x = point_elem.get("x")
                y = point_elem.get("y")
                if x is not None and y is not None:
                    points.append((float(x), float(y)))

            cell.geometry = RawGeometry(
                x=float(geo_elem.get("x", 0)),
                y=float(geo_elem.get("y", 0)),
                width=float(geo_elem.get("width", 0)),
                height=float(geo_elem.get("height", 0)),
                relative=geo_elem.get("relative") == "1",
                points=points,
            )

        cells[cell.id] = cell

    return cells


def parse_drawio_file(file_path: str) -> Dict[str, RawMxCell]:
    """Loads a Draw.io file and parses it into RawMxCell objects."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    xml_content = path.read_text(encoding="utf-8")
    return parse_drawio_xml(xml_content)


# -----------------------------
# Vertex / Edge Builder
# -----------------------------
def _vertex_from_raw(cell: RawMxCell) -> DiagramBase:
    """Create a drawpyo DiagramBase object from a RawMxCell vertex."""
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
    elements = {}
    for cell in raw_cells.values():
        if cell.is_vertex:
            element = _vertex_from_raw(cell)
            elements[cell.id] = element
    return elements


def _edge_from_raw(cell: RawMxCell, elements: Dict[str, DiagramBase]) -> Edge:
    """Create a drawpyo Edge object from a RawMxCell edge."""
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
    for cell in raw_cells.values():
        if cell.is_edge:
            edge = _edge_from_raw(cell, elements)
            elements[cell.id] = edge


# -----------------------------
# Public API
# -----------------------------
def build_drawpyo_elements(raw_cells: Dict[str, RawMxCell]) -> Dict[str, DiagramBase]:
    """Convert RawMxCell dictionary into fully linked drawpyo diagram elements."""
    elements = _build_vertices(raw_cells)
    _build_edges(raw_cells, elements)
    return elements


def parse_drawio_to_drawpyo(file_path: str) -> Dict[str, DiagramBase]:
    """Convenience function: Load Draw.io file and convert to drawpyo elements."""
    raw_cells = parse_drawio_file(file_path)
    return build_drawpyo_elements(raw_cells)
