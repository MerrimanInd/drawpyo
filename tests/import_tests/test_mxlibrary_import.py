from unittest.mock import patch, mock_open
import pytest
import os
from pathlib import Path
from drawpyo.drawio_import.mxlibrary_parser import parse_mxlibrary, load_mxlibrary
import drawpyo

# Path to test fixtures
FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_LIBRARY_PATH = FIXTURES_DIR / "sample_library.xml"

# Path to test output directory
OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


class TestParseMxlibrary:
    """Tests for parse_mxlibrary function"""

    def test_parse_mxlibrary_parsed_correctly(self):
        """Test parsing a valid mxlibrary XML content"""
        xml_content = r"""<mxlibrary>[
  {"h":48,"xml":"&lt;mxGraphModel&gt;&lt;root&gt;&lt;mxCell id=\"0\"/&gt;&lt;mxCell id=\"1\" parent=\"0\"/&gt;&lt;mxCell id=\"2\" value=\"\" style=\"shape=image;verticalLabelPosition=bottom;verticalAlign=top;imageAspect=0;aspect=fixed;image=data:image/svg+xml,PHN2ZyB4...\" vertex=\"1\" parent=\"1\"&gt;&lt;mxGeometry width=\"48\" height=\"48\" as=\"geometry\"/&gt;&lt;/mxCell&gt;&lt;/root&gt;&lt;/mxGraphModel&gt;","w":48,"title":"Test Icon"}
]</mxlibrary>"""

        shapes, errors = parse_mxlibrary(xml_content)

        assert "Test Icon" in shapes
        icon = shapes["Test Icon"]
        assert icon["width"] == 48
        assert icon["height"] == 48
        assert "shape=image" in icon["baseStyle"]
        assert "verticalLabelPosition=bottom" in icon["baseStyle"]
        assert icon["xml_class"] == "mxCell"
        assert len(errors) == 0

    def test_parse_mxlibrary_invalid_json(self):
        """Test parsing mxlibrary with invalid JSON"""
        xml_content = "<mxlibrary>not valid json</mxlibrary>"
        shapes, errors = parse_mxlibrary(xml_content)

        assert len(shapes) == 0
        assert len(errors) > 0
        assert "Failed to parse JSON" in errors[0] or "No valid JSON array" in errors[0]

    def test_parse_mxlibrary_missing_xml_field(self):
        """Test parsing mxlibrary with missing xml field"""
        xml_content = r"""<mxlibrary>[{"h":10,"w":10,"title":"NoXML"}]</mxlibrary>"""
        shapes, errors = parse_mxlibrary(xml_content)

        assert "NoXML" not in shapes
        assert len(errors) == 1
        assert "Missing 'xml' field" in errors[0]


class TestLoadMxlibrary:
    """Tests for load_mxlibrary function"""

    def test_load_mxlibrary_from_local_file(self):
        """Test loading mxlibrary from an actual local file"""
        shapes = load_mxlibrary(str(SAMPLE_LIBRARY_PATH))

        assert len(shapes) == 4
        assert "Test-Icon-1" in shapes
        assert "Test-Icon-2" in shapes
        assert "Simple-Box" in shapes
        assert "firewall" in shapes

        # Verify Test-Icon-1
        icon1 = shapes["Test-Icon-1"]
        assert icon1["width"] == 50
        assert icon1["height"] == 50
        assert "shape=image" in icon1["baseStyle"]

        # Verify Test-Icon-2
        icon2 = shapes["Test-Icon-2"]
        assert icon2["width"] == 60
        assert icon2["height"] == 60

        # Verify Simple-Box
        box = shapes["Simple-Box"]
        assert box["width"] == 120
        assert box["height"] == 60
        assert "rounded=1" in box["baseStyle"]
        assert "fillColor=#dae8fc" in box["baseStyle"]

        firewall = shapes["firewall"]
        assert firewall["width"] == 48
        assert firewall["height"] == 48
        assert "shape=image" in firewall["baseStyle"]

    def test_load_mxlibrary_file(self):
        """Test loading mxlibrary from a file path"""
        content = r"""<mxlibrary>[{"h":10,"xml":"&lt;mxCell vertex=\"1\" style=\"s1\" /&gt;","w":10,"title":"FileIcon"}]</mxlibrary>"""
        with patch("builtins.open", mock_open(read_data=content)) as mocked_file:
            shapes = load_mxlibrary("fake_path.xml")
            assert "FileIcon" in shapes
            assert shapes["FileIcon"]["baseStyle"] == "s1"
            assert shapes["FileIcon"]["width"] == 10
            mocked_file.assert_called_with("fake_path.xml", "r", encoding="utf-8")

    def test_load_mxlibrary_url(self):
        """Test loading mxlibrary from a URL"""
        content = r"""<mxlibrary>[{"h":10,"xml":"&lt;mxCell vertex=\"1\" style=\"s2\" /&gt;","w":10,"title":"UrlIcon"}]</mxlibrary>"""
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_response = mock_urlopen.return_value.__enter__.return_value
            mock_response.read.return_value = content.encode("utf-8")

            shapes = load_mxlibrary("http://example.com/lib.xml")
            assert "UrlIcon" in shapes
            assert shapes["UrlIcon"]["baseStyle"] == "s2"

    def test_load_mxlibrary_file_not_found(self):
        """Test loading from a non-existent file"""
        with pytest.raises(FileNotFoundError) as exc_info:
            load_mxlibrary("/nonexistent/path/file.xml")
        assert "not found" in str(exc_info.value)

    def test_load_mxlibrary_url_http_error(self):
        """Test loading from a URL that returns HTTP error"""
        with patch("urllib.request.urlopen") as mock_urlopen:
            from urllib.error import HTTPError

            mock_urlopen.side_effect = HTTPError(
                "http://example.com/lib.xml", 404, "Not Found", {}, None
            )

            with pytest.raises(ValueError) as exc_info:
                load_mxlibrary("http://example.com/lib.xml")
            assert "HTTP 404" in str(exc_info.value)

    def test_load_mxlibrary_empty_library(self):
        """Test loading an empty library returns empty dict with warning logged"""
        content = r"""<mxlibrary>[]</mxlibrary>"""
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_response = mock_urlopen.return_value.__enter__.return_value
            mock_response.read.return_value = content.encode("utf-8")

            shapes = load_mxlibrary("http://example.com/empty.xml")
            assert shapes == {}
            assert len(shapes) == 0


class TestRegisterMxlibrary:
    """Integration tests for register_mxlibrary function"""

    def test_register_mxlibrary_from_local_file(self):
        """Test registering an mxlibrary from a local file"""
        drawpyo.register_mxlibrary("test_lib", str(SAMPLE_LIBRARY_PATH))

        from drawpyo.diagram.objects import base_libraries

        assert "test_lib" in base_libraries
        assert "Test-Icon-1" in base_libraries["test_lib"]
        assert "Test-Icon-2" in base_libraries["test_lib"]
        assert "Simple-Box" in base_libraries["test_lib"]

        # Verify the shapes were loaded correctly
        icon1 = base_libraries["test_lib"]["Test-Icon-1"]
        assert icon1["width"] == 50
        assert icon1["height"] == 50

    def test_register_mxlibrary_url(self):
        """Test registering an mxlibrary from a mocked URL"""
        content = r"""<mxlibrary>[
  {"h":50,"xml":"&lt;mxGraphModel&gt;&lt;root&gt;&lt;mxCell id=\"0\"/&gt;&lt;mxCell id=\"1\" parent=\"0\"/&gt;&lt;mxCell id=\"2\" value=\"\" style=\"shape=image;verticalLabelPosition=bottom;verticalAlign=top;imageAspect=0;aspect=fixed;image=data:image/svg+xml,PHN2ZyB3aWR0aD0iNTAiIGhlaWdodD0iNTAiIHZpZXdCb3g9IjAgMCA1MCA1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iNTAiIGhlaWdodD0iNTAiIGZpbGw9IiMwMDc4ZDQiLz48L3N2Zz4=\" vertex=\"1\" parent=\"1\"&gt;&lt;mxGeometry width=\"50\" height=\"50\" as=\"geometry\"/&gt;&lt;/mxCell&gt;&lt;/root&gt;&lt;/mxGraphModel&gt;","w":50,"title":"Azure-VM"},
  {"h":50,"xml":"&lt;mxGraphModel&gt;&lt;root&gt;&lt;mxCell id=\"0\"/&gt;&lt;mxCell id=\"1\" parent=\"0\"/&gt;&lt;mxCell id=\"2\" value=\"\" style=\"shape=image;verticalLabelPosition=bottom;verticalAlign=top;imageAspect=0;aspect=fixed;image=data:image/svg+xml,PHN2ZyB3aWR0aD0iNTAiIGhlaWdodD0iNTAiIHZpZXdCb3g9IjAgMCA1MCA1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSIyNSIgY3k9IjI1IiByPSIyNSIgZmlsbD0iI2ZmYjkwMCIvPjwvc3ZnPg==\" vertex=\"1\" parent=\"1\"&gt;&lt;mxGeometry width=\"50\" height=\"50\" as=\"geometry\"/&gt;&lt;/mxCell&gt;&lt;/root&gt;&lt;/mxGraphModel&gt;","w":50,"title":"Azure-Storage"}
]</mxlibrary>"""

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_response = mock_urlopen.return_value.__enter__.return_value
            mock_response.read.return_value = content.encode("utf-8")

            drawpyo.register_mxlibrary("azure", "https://example.com/azure-icons.xml")

            from drawpyo.diagram.objects import base_libraries

            assert "azure" in base_libraries
            assert "Azure-VM" in base_libraries["azure"]
            assert "Azure-Storage" in base_libraries["azure"]

    def test_register_mxlibrary_and_create_object(self):
        """Test the full workflow: register library, create object, save diagram"""
        content = r"""<mxlibrary>[
  {"h":60,"xml":"&lt;mxGraphModel&gt;&lt;root&gt;&lt;mxCell id=\"0\"/&gt;&lt;mxCell id=\"1\" parent=\"0\"/&gt;&lt;mxCell id=\"2\" value=\"\" style=\"shape=image;verticalLabelPosition=bottom;verticalAlign=top;imageAspect=0;aspect=fixed;image=data:image/svg+xml,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIGZpbGw9IiNmZjY2MDAiLz48L3N2Zz4=\" vertex=\"1\" parent=\"1\"&gt;&lt;mxGeometry width=\"60\" height=\"60\" as=\"geometry\"/&gt;&lt;/mxCell&gt;&lt;/root&gt;&lt;/mxGraphModel&gt;","w":60,"title":"Custom-Icon"}
]</mxlibrary>"""

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_response = mock_urlopen.return_value.__enter__.return_value
            mock_response.read.return_value = content.encode("utf-8")

            drawpyo.register_mxlibrary("custom", "https://example.com/custom.xml")

            file = drawpyo.File()
            page = drawpyo.Page(file=file)

            icon = drawpyo.diagram.object_from_library(
                library="custom",
                obj_name="Custom-Icon",
                page=page,
                position=(100, 100),
            )

            assert icon is not None
            assert icon.width == 60
            assert icon.height == 60
            assert "shape=image" in icon.baseStyle
            assert "image=data:image/svg+xml" in icon.baseStyle

            file.file_path = str(OUTPUT_DIR)
            file.file_name = "test_diagram.drawio"
            file.write()

            output_path = OUTPUT_DIR / "test_diagram.drawio"
            assert output_path.exists()

            with open(output_path, "r") as f:
                content = f.read()
                assert "shape=image" in content
                assert "image=data:image/svg+xml" in content

    def test_register_mxlibrary_invalid_library(self):
        """Test that registering an empty library logs warning but doesn't raise"""
        content = r"""<mxlibrary>[]</mxlibrary>"""

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_response = mock_urlopen.return_value.__enter__.return_value
            mock_response.read.return_value = content.encode("utf-8")

            # Should not raise an exception, just log warning
            drawpyo.register_mxlibrary("empty", "https://example.com/empty.xml")

            from drawpyo.diagram.objects import base_libraries

            # Empty library should not be registered
            assert "empty" not in base_libraries


class TestObjectFromLibraryDict:
    """Tests for creating objects from library dictionaries"""

    def test_object_from_library_dict_with_mxlibrary(self):
        """Test creating an object from an mxlibrary dict directly (without registering)"""
        content = r"""<mxlibrary>[
  {"h":40,"xml":"&lt;mxCell vertex=\"1\" style=\"shape=ellipse;fillColor=#ff0000;strokeColor=#000000\" /&gt;","w":40,"title":"Red-Circle"}
]</mxlibrary>"""

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_response = mock_urlopen.return_value.__enter__.return_value
            mock_response.read.return_value = content.encode("utf-8")

            shapes = drawpyo.load_mxlibrary("https://example.com/lib.xml")

            file = drawpyo.File()
            page = drawpyo.Page(file=file)

            obj = drawpyo.diagram.object_from_library(
                library=shapes, obj_name="Red-Circle", page=page, position=(50, 50)
            )

            assert obj is not None
            assert obj.width == 40
            assert obj.height == 40
            assert "shape=ellipse" in obj.baseStyle
            assert "fillColor=#ff0000" in obj.baseStyle


class TestLocalFileIntegration:
    """Integration tests using real local fixture files"""

    def test_full_workflow_with_local_file(self):
        """Test complete workflow: register local file, create objects, save diagram"""
        # Register library from local file
        drawpyo.register_mxlibrary("local_test", str(SAMPLE_LIBRARY_PATH))

        # Create diagram
        file = drawpyo.File()
        page = drawpyo.Page(file=file)

        # Create objects from the registered library
        icon1 = drawpyo.diagram.object_from_library(
            library="local_test",
            obj_name="Test-Icon-1",
            page=page,
            position=(50, 50),
        )

        icon2 = drawpyo.diagram.object_from_library(
            library="local_test",
            obj_name="Test-Icon-2",
            page=page,
            position=(150, 50),
        )

        box = drawpyo.diagram.object_from_library(
            library="local_test",
            obj_name="Simple-Box",
            page=page,
            position=(50, 150),
        )
        firewall = drawpyo.diagram.object_from_library(
            library="local_test",
            obj_name="firewall",
            page=page,
            position=(250, 100),
        )
        # Verify objects were created correctly
        assert icon1 is not None
        assert icon1.width == 50
        assert icon1.height == 50
        assert "shape=image" in icon1.baseStyle

        assert icon2 is not None
        assert icon2.width == 60
        assert icon2.height == 60

        assert box is not None
        assert box.width == 120
        assert box.height == 60
        assert "rounded=1" in box.baseStyle

        assert firewall is not None
        assert firewall.width == 48
        assert firewall.height == 48
        assert "shape=image" in firewall.baseStyle

        # Save and verify the diagram
        file.file_path = str(OUTPUT_DIR)
        file.file_name = "test_local_diagram.drawio"
        file.write()

        output_path = OUTPUT_DIR / "test_local_diagram.drawio"
        assert output_path.exists()

        with open(output_path, "r") as f:
            content = f.read()
            assert "shape=image" in content
            assert "rounded=1" in content
            assert "fillColor=#dae8fc" in content

    def test_load_library_dict_from_local_file(self):
        """Test loading library as dict from local file and using directly"""
        shapes = drawpyo.load_mxlibrary(str(SAMPLE_LIBRARY_PATH))

        file = drawpyo.File()
        page = drawpyo.Page(file=file)

        # Use the shapes dict directly without registering
        obj = drawpyo.diagram.object_from_library(
            library=shapes, obj_name="Simple-Box", page=page, position=(100, 100)
        )

        assert obj is not None
        assert obj.width == 120
        assert obj.height == 60
        assert "fillColor=#dae8fc" in obj.baseStyle
