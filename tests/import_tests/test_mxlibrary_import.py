from unittest.mock import patch, mock_open
import pytest
from drawpyo.drawio_import.mxlibrary_parser import parse_mxlibrary, load_mxlibrary

def test_parse_mxlibrary_parsed_correctly():
    # Using raw string to preserve backslashes for JSON escaping
    xml_content = r"""<mxlibrary>[
  {"h":48,"xml":"&lt;mxGraphModel&gt;&lt;root&gt;&lt;mxCell id=\"0\"/&gt;&lt;mxCell id=\"1\" parent=\"0\"/&gt;&lt;mxCell id=\"2\" value=\"\" style=\"shape=image;verticalLabelPosition=bottom;verticalAlign=top;imageAspect=0;aspect=fixed;image=data:image/svg+xml,PHN2ZyB4...\" vertex=\"1\" parent=\"1\"&gt;&lt;mxGeometry width=\"48\" height=\"48\" as=\"geometry\"/&gt;&lt;/mxCell&gt;&lt;/root&gt;&lt;/mxGraphModel&gt;","w":48,"title":"Test Icon"}
]</mxlibrary>"""
    
    shapes = parse_mxlibrary(xml_content)
    
    assert "Test Icon" in shapes
    icon = shapes["Test Icon"]
    assert icon["width"] == 48
    assert icon["height"] == 48
    
    # Check style presence
    assert "shape=image" in icon["baseStyle"]
    assert "verticalLabelPosition=bottom" in icon["baseStyle"]
    assert icon["xml_class"] == "mxCell"

def test_load_mxlibrary_file():
    content = r"""<mxlibrary>[{"h":10,"xml":"&lt;mxCell vertex=\"1\" style=\"s1\" /&gt;","w":10,"title":"FileIcon"}]</mxlibrary>"""
    with patch("builtins.open", mock_open(read_data=content)) as mocked_file:
        shapes = load_mxlibrary("fake_path.xml")
        assert "FileIcon" in shapes
        assert shapes["FileIcon"]["baseStyle"] == "s1"
        assert shapes["FileIcon"]["width"] == 10
        mocked_file.assert_called_with("fake_path.xml", "r", encoding="utf-8")

def test_load_mxlibrary_url():
    content = r"""<mxlibrary>[{"h":10,"xml":"&lt;mxCell vertex=\"1\" style=\"s2\" /&gt;","w":10,"title":"UrlIcon"}]</mxlibrary>"""
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_response = mock_urlopen.return_value.__enter__.return_value
        mock_response.read.return_value = content.encode("utf-8")
        
        shapes = load_mxlibrary("http://example.com/lib.xml")
        assert "UrlIcon" in shapes
        assert shapes["UrlIcon"]["baseStyle"] == "s2"
