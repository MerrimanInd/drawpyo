from unittest.mock import patch, mock_open
import pytest
import os
import tempfile
from drawpyo.drawio_import.mxlibrary_parser import parse_mxlibrary, load_mxlibrary
import drawpyo

def test_parse_mxlibrary_parsed_correctly():
    # Using raw string to preserve backslashes for JSON escaping
    xml_content = r"""<mxlibrary>[
  {"h":48,"xml":"&lt;mxGraphModel&gt;&lt;root&gt;&lt;mxCell id=\"0\"/&gt;&lt;mxCell id=\"1\" parent=\"0\"/&gt;&lt;mxCell id=\"2\" value=\"\" style=\"shape=image;verticalLabelPosition=bottom;verticalAlign=top;imageAspect=0;aspect=fixed;image=data:image/svg+xml,PHN2ZyB4...\" vertex=\"1\" parent=\"1\"&gt;&lt;mxGeometry width=\"48\" height=\"48\" as=\"geometry\"/&gt;&lt;/mxCell&gt;&lt;/root&gt;&lt;/mxGraphModel&gt;","w":48,"title":"Test Icon"}
]</mxlibrary>"""
    
    shapes, errors = parse_mxlibrary(xml_content)
    
    assert "Test Icon" in shapes
    icon = shapes["Test Icon"]
    assert icon["width"] == 48
    assert icon["height"] == 48
    
    # Check style presence
    assert "shape=image" in icon["baseStyle"]
    assert "verticalLabelPosition=bottom" in icon["baseStyle"]
    assert icon["xml_class"] == "mxCell"
    assert len(errors) == 0

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


# Error handling tests
def test_parse_mxlibrary_invalid_json():
    xml_content = "<mxlibrary>not valid json</mxlibrary>"
    shapes, errors = parse_mxlibrary(xml_content)
    
    assert len(shapes) == 0
    assert len(errors) > 0
    assert "Failed to parse JSON" in errors[0] or "No valid JSON array" in errors[0]

def test_parse_mxlibrary_missing_xml_field():
    xml_content = r"""<mxlibrary>[{"h":10,"w":10,"title":"NoXML"}]</mxlibrary>"""
    shapes, errors = parse_mxlibrary(xml_content)
    
    assert "NoXML" not in shapes
    assert len(errors) == 1
    assert "Missing 'xml' field" in errors[0]

def test_load_mxlibrary_file_not_found():
    with pytest.raises(FileNotFoundError) as exc_info:
        load_mxlibrary("/nonexistent/path/file.xml")
    assert "not found" in str(exc_info.value)

def test_load_mxlibrary_url_http_error():
    with patch("urllib.request.urlopen") as mock_urlopen:
        from urllib.error import HTTPError
        mock_urlopen.side_effect = HTTPError(
            "http://example.com/lib.xml", 404, "Not Found", {}, None
        )
        
        with pytest.raises(ValueError) as exc_info:
            load_mxlibrary("http://example.com/lib.xml")
        assert "HTTP 404" in str(exc_info.value)

def test_load_mxlibrary_empty_library():
    content = r"""<mxlibrary>[]</mxlibrary>"""
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_response = mock_urlopen.return_value.__enter__.return_value
        mock_response.read.return_value = content.encode("utf-8")
        
        with pytest.raises(ValueError) as exc_info:
            load_mxlibrary("http://example.com/empty.xml")
        assert "No valid shapes found" in str(exc_info.value)


# Integration tests with register_mxlibrary
def test_register_mxlibrary_url():
    """Test registering an mxlibrary from a mocked URL"""
    # Realistic Azure-style icon library content
    content = r"""<mxlibrary>[
  {"h":50,"xml":"&lt;mxGraphModel&gt;&lt;root&gt;&lt;mxCell id=\"0\"/&gt;&lt;mxCell id=\"1\" parent=\"0\"/&gt;&lt;mxCell id=\"2\" value=\"\" style=\"shape=image;verticalLabelPosition=bottom;verticalAlign=top;imageAspect=0;aspect=fixed;image=data:image/svg+xml,PHN2ZyB3aWR0aD0iNTAiIGhlaWdodD0iNTAiIHZpZXdCb3g9IjAgMCA1MCA1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iNTAiIGhlaWdodD0iNTAiIGZpbGw9IiMwMDc4ZDQiLz48L3N2Zz4=\" vertex=\"1\" parent=\"1\"&gt;&lt;mxGeometry width=\"50\" height=\"50\" as=\"geometry\"/&gt;&lt;/mxCell&gt;&lt;/root&gt;&lt;/mxGraphModel&gt;","w":50,"title":"Azure-VM"},
  {"h":50,"xml":"&lt;mxGraphModel&gt;&lt;root&gt;&lt;mxCell id=\"0\"/&gt;&lt;mxCell id=\"1\" parent=\"0\"/&gt;&lt;mxCell id=\"2\" value=\"\" style=\"shape=image;verticalLabelPosition=bottom;verticalAlign=top;imageAspect=0;aspect=fixed;image=data:image/svg+xml,PHN2ZyB3aWR0aD0iNTAiIGhlaWdodD0iNTAiIHZpZXdCb3g9IjAgMCA1MCA1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSIyNSIgY3k9IjI1IiByPSIyNSIgZmlsbD0iI2ZmYjkwMCIvPjwvc3ZnPg==\" vertex=\"1\" parent=\"1\"&gt;&lt;mxGeometry width=\"50\" height=\"50\" as=\"geometry\"/&gt;&lt;/mxCell&gt;&lt;/root&gt;&lt;/mxGraphModel&gt;","w":50,"title":"Azure-Storage"}
]</mxlibrary>"""
    
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_response = mock_urlopen.return_value.__enter__.return_value
        mock_response.read.return_value = content.encode("utf-8")
        
        # Register the library
        drawpyo.register_mxlibrary("azure", "https://example.com/azure-icons.xml")
        
        # Verify it was registered
        from drawpyo.diagram.objects import base_libraries
        assert "azure" in base_libraries
        assert "Azure-VM" in base_libraries["azure"]
        assert "Azure-Storage" in base_libraries["azure"]

def test_register_mxlibrary_and_create_object():
    """Test the full workflow: register library, create object, save diagram"""
    content = r"""<mxlibrary>[
  {"h":60,"xml":"&lt;mxGraphModel&gt;&lt;root&gt;&lt;mxCell id=\"0\"/&gt;&lt;mxCell id=\"1\" parent=\"0\"/&gt;&lt;mxCell id=\"2\" value=\"\" style=\"shape=image;verticalLabelPosition=bottom;verticalAlign=top;imageAspect=0;aspect=fixed;image=data:image/svg+xml,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIGZpbGw9IiNmZjY2MDAiLz48L3N2Zz4=\" vertex=\"1\" parent=\"1\"&gt;&lt;mxGeometry width=\"60\" height=\"60\" as=\"geometry\"/&gt;&lt;/mxCell&gt;&lt;/root&gt;&lt;/mxGraphModel&gt;","w":60,"title":"Custom-Icon"}
]</mxlibrary>"""
    
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_response = mock_urlopen.return_value.__enter__.return_value
        mock_response.read.return_value = content.encode("utf-8")
        
        # Register the library
        drawpyo.register_mxlibrary("custom", "https://example.com/custom.xml")
        
        # Create a diagram with the imported shape
        file = drawpyo.File()
        page = drawpyo.Page(file=file)
        
        # Create object from the registered library
        icon = drawpyo.diagram.object_from_library(
            library="custom",
            obj_name="Custom-Icon",
            page=page,
            position=(100, 100)
        )
        
        # Verify the object was created with correct properties
        assert icon is not None
        assert icon.width == 60
        assert icon.height == 60
        assert "shape=image" in icon.baseStyle
        assert "image=data:image/svg+xml" in icon.baseStyle
        
        # Save to a temporary file
        with tempfile.TemporaryDirectory() as tmpdir:
            file.file_path = tmpdir
            file.file_name = "test_diagram.drawio"
            file.write()
            
            # Verify file was created
            output_path = os.path.join(tmpdir, "test_diagram.drawio")
            assert os.path.exists(output_path)
            
            # Verify the file contains our object
            with open(output_path, "r") as f:
                content = f.read()
                assert "shape=image" in content
                assert "image=data:image/svg+xml" in content

def test_register_mxlibrary_invalid_library():
    """Test that registering an empty library raises an error"""
    content = r"""<mxlibrary>[]</mxlibrary>"""
    
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_response = mock_urlopen.return_value.__enter__.return_value
        mock_response.read.return_value = content.encode("utf-8")
        
        with pytest.raises(ValueError) as exc_info:
            drawpyo.register_mxlibrary("empty", "https://example.com/empty.xml")
        # The error comes from load_mxlibrary, not register_mxlibrary
        assert "No valid shapes found" in str(exc_info.value)

def test_object_from_library_dict_with_mxlibrary():
    """Test creating an object from an mxlibrary dict directly (without registering)"""
    content = r"""<mxlibrary>[
  {"h":40,"xml":"&lt;mxCell vertex=\"1\" style=\"shape=ellipse;fillColor=#ff0000;strokeColor=#000000\" /&gt;","w":40,"title":"Red-Circle"}
]</mxlibrary>"""
    
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_response = mock_urlopen.return_value.__enter__.return_value
        mock_response.read.return_value = content.encode("utf-8")
        
        # Load library without registering
        shapes = drawpyo.load_mxlibrary("https://example.com/lib.xml")
        
        # Create a diagram
        file = drawpyo.File()
        page = drawpyo.Page(file=file)
        
        # Create object from the dict directly
        obj = drawpyo.diagram.object_from_library(
            library=shapes,  # Pass dict directly
            obj_name="Red-Circle",
            page=page,
            position=(50, 50)
        )
        
        assert obj is not None
        assert obj.width == 40
        assert obj.height == 40
        assert "shape=ellipse" in obj.baseStyle
        assert "fillColor=#ff0000" in obj.baseStyle

