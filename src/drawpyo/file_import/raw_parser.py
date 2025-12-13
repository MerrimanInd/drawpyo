import xml.etree.ElementTree as ET
from typing import Dict
from .raw import RawMxCell, RawGeometry
from pathlib import Path
from typing import Dict
from .raw import RawMxCell


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

        # Geometry
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
    """
    Loads a Draw.io file from a given path and parses it into RawMxCell objects.

    Args:
        file_path (str): Path to the Draw.io XML file (.drawio, .xml, etc.)

    Returns:
        Dict[str, RawMxCell]: Dictionary of all mxCells, keyed by their ID
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    xml_content = path.read_text(encoding="utf-8")
    cells = parse_drawio_xml(xml_content)
    return cells
