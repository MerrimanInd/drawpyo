import json
import html
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


def parse_mxlibrary(content: str) -> Tuple[Dict[str, Dict[str, Any]], List[str]]:
    """
    Parses an mxlibrary file content and extracts shape definitions.

    Args:
        content: The string content of the mxlibrary file.

    Returns:
        A tuple of (shapes_dict, errors_list) where:
        - shapes_dict: Dictionary with keys as titles and values as dicts containing
          properties like baseStyle, width, height, and xml_class.
        - errors_list: List of error messages for shapes that couldn't be parsed.
    """
    errors: List[str] = []
    clean_content = (
        content.replace("<mxlibrary>", "").replace("</mxlibrary>", "").strip()
    )

    try:
        data = json.loads(clean_content)
    except json.JSONDecodeError as e:
        # Try to extract JSON array from content
        start = content.find("[")
        end = content.rfind("]")
        if start != -1 and end != -1:
            try:
                data = json.loads(content[start : end + 1])
            except json.JSONDecodeError:
                errors.append(f"Failed to parse JSON content: {str(e)}")
                return {}, errors
        else:
            errors.append(f"No valid JSON array found in content: {str(e)}")
            return {}, errors

    shapes: Dict[str, Dict[str, Any]] = {}

    if not isinstance(data, list):
        errors.append(f"Expected JSON array, got {type(data).__name__}")
        return {}, errors

    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            errors.append(f"Item {idx}: Expected dict, got {type(item).__name__}")
            continue

        title = item.get("title", "Untitled")
        w = item.get("w", 0)
        h = item.get("h", 0)
        xml_encoded = item.get("xml")

        if not xml_encoded:
            errors.append(f"Item {idx} ({title}): Missing 'xml' field")
            continue

        xml_str = html.unescape(xml_encoded)

        try:
            try:
                root_element = ET.fromstring(xml_str)
            except ET.ParseError:
                root_element = ET.fromstring(f"<root>{xml_str}</root>")

            main_cell = None
            cells = []

            if root_element.tag == "mxCell":
                cells.append(root_element)

            for cell in root_element.iter("mxCell"):
                cells.append(cell)

            for cell in cells:
                if cell.get("vertex") == "1":
                    main_cell = cell
                    break

            if main_cell is None and cells:
                main_cell = cells[0]

            if main_cell is not None:
                style = main_cell.get("style", "")

                shapes[title] = {
                    "baseStyle": style,
                    "width": w,
                    "height": h,
                    "xml_class": "mxCell",
                }
            else:
                errors.append(f"Item {idx} ({title}): No valid mxCell found in XML")

        except ET.ParseError as e:
            errors.append(f"Item {idx} ({title}): XML parse error - {str(e)}")
        except Exception as e:
            errors.append(f"Item {idx} ({title}): Unexpected error - {str(e)}")

    return shapes, errors


def load_mxlibrary(file_path_or_url: str) -> Dict[str, Dict[str, Any]]:
    """
    Loads an mxlibrary from a file path or URL and parses it.

    Args:
        file_path_or_url: Local file path or HTTP/HTTPS URL.

    Returns:
        Dictionary of shapes.

    Raises:
        ValueError: If the file/URL cannot be loaded or parsed.
        FileNotFoundError: If the local file doesn't exist.
        urllib.error.URLError: If the URL cannot be accessed.
    """
    content = ""

    try:
        if file_path_or_url.lower().startswith(("http://", "https://")):
            try:
                with urllib.request.urlopen(file_path_or_url, timeout=30) as response:
                    content = response.read().decode("utf-8")
            except urllib.error.HTTPError as e:
                raise ValueError(
                    f"Failed to fetch mxlibrary from URL '{file_path_or_url}': "
                    f"HTTP {e.code} - {e.reason}"
                ) from e
            except urllib.error.URLError as e:
                raise ValueError(
                    f"Failed to access URL '{file_path_or_url}': {str(e.reason)}"
                ) from e
            except Exception as e:
                raise ValueError(
                    f"Unexpected error fetching URL '{file_path_or_url}': {str(e)}"
                ) from e
        else:
            try:
                with open(file_path_or_url, "r", encoding="utf-8") as f:
                    content = f.read()
            except FileNotFoundError:
                raise FileNotFoundError(
                    f"mxlibrary file not found: '{file_path_or_url}'"
                )
            except PermissionError:
                raise ValueError(
                    f"Permission denied reading file: '{file_path_or_url}'"
                )
            except Exception as e:
                raise ValueError(
                    f"Error reading file '{file_path_or_url}': {str(e)}"
                ) from e

        shapes, errors = parse_mxlibrary(content)

        if errors:
            logger.warning(
                f"Encountered {len(errors)} error(s) while parsing mxlibrary "
                f"from '{file_path_or_url}': {'; '.join(errors[:5])}"
                + (" ..." if len(errors) > 5 else "")
            )

        if not shapes:
            logger.warning(
                f"No valid shapes found in mxlibrary '{file_path_or_url}'. "
                f"Errors: {'; '.join(errors)}"
            )
            return {}

        return shapes

    except (ValueError, FileNotFoundError) as e:
        # Re-raise our custom errors
        raise
    except Exception as e:
        # Catch any unexpected errors
        raise ValueError(
            f"Unexpected error loading mxlibrary from '{file_path_or_url}': {str(e)}"
        ) from e
