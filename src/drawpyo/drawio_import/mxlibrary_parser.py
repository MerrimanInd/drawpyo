import json
import html
import urllib.request
import xml.etree.ElementTree as ET
from typing import Dict, Any

def parse_mxlibrary(content: str) -> Dict[str, Dict[str, Any]]:
    """
    Parses an mxlibrary file content and extracts shape definitions.
    
    Args:
        content: The string content of the mxlibrary file.
        
    Returns:
        A dictionary where keys are titles and values are dicts containing 
        properties like baseStyle, width, height, and xml_class.
    """
    clean_content = content.replace("<mxlibrary>", "").replace("</mxlibrary>", "").strip()
    
    try:
        data = json.loads(clean_content)
    except json.JSONDecodeError:
        start = content.find("[")
        end = content.rfind("]")
        if start != -1 and end != -1:
            try:
                data = json.loads(content[start:end+1])
            except json.JSONDecodeError:
                return {}
        else:
            return {}

    shapes: Dict[str, Dict[str, Any]] = {}
    
    if not isinstance(data, list):
        return {}

    for item in data:
        if not isinstance(item, dict):
            continue
            
        title = item.get("title", "Untitled")
        w = item.get("w", 0)
        h = item.get("h", 0)
        xml_encoded = item.get("xml")
        
        if not xml_encoded:
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
                    "xml_class": "mxCell"
                }

        except Exception:
            continue

    return shapes

def load_mxlibrary(file_path_or_url: str) -> Dict[str, Dict[str, Any]]:
    """
    Loads an mxlibrary from a file path or URL and parses it.
    
    Args:
        file_path_or_url: Local file path or HTTP/HTTPS URL.
        
    Returns:
        Dictionary of shapes.
    """
    content = ""
    if file_path_or_url.lower().startswith(("http://", "https://")):
        with urllib.request.urlopen(file_path_or_url) as response:
            content = response.read().decode("utf-8")
    else:
        with open(file_path_or_url, "r", encoding="utf-8") as f:
            content = f.read()
            
    return parse_mxlibrary(content)
