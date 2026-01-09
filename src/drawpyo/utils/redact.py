from __future__ import annotations

from drawpyo.diagram import Object, Edge
from drawpyo.drawio_import import ParsedDiagram
from drawpyo.utils import logger
from pathlib import Path
import json


def _redact_text(text: str | None) -> str:
    """
    Redact a text string by replacing all non-whitespace characters with 'X'.

    Args:
        text: The input text to redact, or None.

    Returns:
        The redacted text with non-whitespace characters replaced by 'X',
        or None if the input was None.
    """
    if text is None:
        return ""
    return "".join(ch if ch.isspace() else "X" for ch in text)


def redact_values(diagram: ParsedDiagram, map_file_path: Path) -> ParsedDiagram:
    """
    Redact all textual values in a diagram.

    Original values are stored in a JSON file, keyed by element ID, so they
    can later be restored.

    Args:
        diagram: A diagram instance containing shapes and edges.
        map_file_path: File path where the ID-to-original-value mapping
            will be written as JSON.

    Returns:
        The modified diagram with all applicable text fields redacted.
    """
    id_value_map: dict[str, str] = {}

    for node in diagram.shapes + diagram.edges:
        if isinstance(node, Object):
            if node.value is None:
                continue
            id_value_map[node.id] = node.value
            node.value = _redact_text(node.value)

        elif isinstance(node, Edge):
            if node.label is None:
                continue
            id_value_map[node.id] = node.label
            node.label = _redact_text(node.label)

    with open(map_file_path, "w", encoding="utf-8") as f:
        json.dump(
            id_value_map,
            f,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )

    logger.info(f"👤 Reaction map saved to: '{map_file_path}'")
    return diagram


def restore_values(diagram: ParsedDiagram, map_file_path: Path) -> ParsedDiagram:
    """
    Restore redacted diagram values from a JSON mapping file.

    Args:
        diagram: A diagram instance containing shapes and edges.
        map_file_path: Path to the JSON file created by `redact_values`.

    Returns:
        The modified diagram with restored text values.
    """
    if not map_file_path.exists():
        raise FileNotFoundError(f"Restore map not found: {map_file_path}")

    with map_file_path.open("r", encoding="utf-8") as f:
        id_value_map: dict[str, str] = json.load(f)

    restored = 0
    missing = 0

    for cell_id, original_value in id_value_map.items():
        matched_element = None

        for element in diagram.shapes + diagram.edges:
            if str(element.id) == str(cell_id):
                matched_element = element
                break

        if matched_element is None:
            missing += 1
            logger.warning(f" No matching object/edge found: '{cell_id}'")
            continue

        if isinstance(matched_element, Object):
            matched_element.value = original_value
            restored += 1

        elif isinstance(matched_element, Edge):
            matched_element.label = original_value
            restored += 1

    logger.info(f"🔄 Restore complete: restored={restored}, missing={missing}")

    return diagram
