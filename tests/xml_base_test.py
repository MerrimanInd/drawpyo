"""
Tests for the XMLBase base class.

XMLBase is the base class for all exported objects in drawpyo.
It provides basic functionality for generating XML tags and escaping.
"""

import pytest
import drawpyo


class TestXMLBaseInit:
    """XMLBase object initialization tests"""

    def test_default_values(self, xml_base: drawpyo.XMLBase) -> None:
        """Checks default values when creating XMLBase"""
        assert xml_base.id == id(xml_base)
        assert xml_base.xml_class == "xml_tag"
        assert xml_base.xml_parent is None
        assert xml_base.tag is None
        assert xml_base.tooltip is None

    def test_custom_id(self) -> None:
        """Checks if an object with a user ID has been created"""
        obj = drawpyo.XMLBase(id="custom_id")
        assert obj.id == "custom_id"

    def test_custom_xml_class(self, xml_base_with_class: drawpyo.XMLBase) -> None:
        """Checks if an object with a custom XML class is created"""
        assert xml_base_with_class.xml_class == "mxCell"

    def test_custom_xml_parent(self) -> None:
        """Checks the setting of the parent XML element"""
        parent_obj = drawpyo.XMLBase(id="parent")
        child_obj = drawpyo.XMLBase(xml_parent=parent_obj.id)
        assert child_obj.xml_parent == parent_obj.id

    def test_with_tag(self) -> None:
        """Checks if an object with a tag has been created"""
        obj = drawpyo.XMLBase(tag="important")
        assert obj.tag == "important"

    def test_with_tooltip(self) -> None:
        """Checks the creation of an object with a hint"""
        obj = drawpyo.XMLBase(tooltip="This is a tooltip")
        assert obj.tooltip == "This is a tooltip"


class TestXMLBaseAttributes:
    """Tests for XMLBase object attributes"""

    def test_attributes_default(self, xml_base: drawpyo.XMLBase) -> None:
        """Checks default attributes"""
        assert xml_base.attributes == {"id": xml_base.id, "parent": None}

    def test_attributes_with_parent(self) -> None:
        """Checks attributes with a set parent"""
        obj = drawpyo.XMLBase(xml_parent="parent_id")
        assert obj.attributes["parent"] == "parent_id"


class TestXMLBaseTags:
    """XML tag generation tests"""

    def test_basic_open_tag(self, xml_base_with_class: drawpyo.XMLBase) -> None:
        """Checks the generation of the opening tag"""
        assert (
            xml_base_with_class.xml_open_tag
            == f'<mxCell id="{xml_base_with_class.id}">'
        )

    def test_basic_close_tag(self, xml_base_with_class: drawpyo.XMLBase) -> None:
        """Checks the generation of the closing tag"""
        assert xml_base_with_class.xml_close_tag == "</mxCell>"

    def test_basic_xml(self, xml_base_with_class: drawpyo.XMLBase) -> None:
        """Checks the generation of a self-closing XML tag"""
        assert xml_base_with_class.xml == f'<mxCell id="{xml_base_with_class.id}" />'

    def test_open_tag_with_multiple_attributes(self) -> None:
        """Checks the generation of a tag with multiple attributes"""
        obj = drawpyo.XMLBase(id="test_id", xml_class="mxCell", xml_parent="parent_id")
        assert 'id="test_id"' in obj.xml_open_tag
        assert 'parent="parent_id"' in obj.xml_open_tag


class TestXmlIfy:
    """XML special character escaping tests"""

    @pytest.mark.parametrize(
        "input_str,expected",
        [
            (">", "&gt;"),
            ("<", "&lt;"),
            ("&", "&amp;"),
            ('"', "&quot;"),
            ("'", "&apos;"),
            ("", ""),
            ("hello", "hello"),
            ("<div>&test</div>", "&lt;div&gt;&amp;test&lt;/div&gt;"),
            ("5 > 3 & 3 < 5", "5 &gt; 3 &amp; 3 &lt; 5"),
            ('Say "hello"', "Say &quot;hello&quot;"),
        ],
    )
    def test_xml_ify(
        self, xml_base: drawpyo.XMLBase, input_str: str, expected: str
    ) -> None:
        """Checks that various special characters are escaped correctly"""
        assert xml_base.xml_ify(input_str) == expected

    def test_xml_ify_preserves_normal_text(self, xml_base: drawpyo.XMLBase) -> None:
        """Checks that the plain text is not modified"""
        normal_text = "This is normal text without special chars"
        assert xml_base.xml_ify(normal_text) == normal_text


class TestTranslateTxt:
    """Tests of the function of replacing characters in text"""

    def test_translate_txt_basic(self) -> None:
        """Tests basic character replacement"""
        result = drawpyo.XMLBase.translate_txt("abc", {"a": "X", "c": "Z"})
        assert result == "XbZ"

    def test_translate_txt_no_replacements(self) -> None:
        """Checks operation without replacements"""
        result = drawpyo.XMLBase.translate_txt("hello", {})
        assert result == "hello"

    def test_translate_txt_multiple_occurrences(self) -> None:
        """Checks for multiple occurrences of a replacement"""
        result = drawpyo.XMLBase.translate_txt("aaa", {"a": "b"})
        assert result == "bbb"

    def test_translate_txt_empty_string(self) -> None:
        """Tests for handling empty strings"""
        result = drawpyo.XMLBase.translate_txt("", {"a": "b"})
        assert result == ""

    def test_translate_txt_complex_replacement(self) -> None:
        """Checks for complex character replacement"""
        replacements = {"h": "H", "o": "0", " ": "_"}
        result = drawpyo.XMLBase.translate_txt("hello world", replacements)
        assert result == "Hell0_w0rld"
