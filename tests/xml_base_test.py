import pytest
import drawpyo


class TestXMLBaseInit:
    def test_default_values(self) -> None:
        obj = drawpyo.XMLBase()
        assert obj.id == id(obj)
        assert obj.xml_class == "xml_tag"
        assert obj.xml_parent is None
        assert obj.tag is None
        assert obj.tooltip is None

    def test_custom_id(self) -> None:
        obj = drawpyo.XMLBase(id="custom_id")
        assert obj.id == "custom_id"

    def test_custom_xml_class(self) -> None:
        obj = drawpyo.XMLBase(xml_class="mxCell")
        assert obj.xml_class == "mxCell"


class TestXMLBaseAttributes:
    def test_attributes(self) -> None:
        obj = drawpyo.XMLBase()
        assert obj.attributes == {"id": obj.id, "parent": None}


class TestXMLBaseTags:
    def test_basic_open_tag(self) -> None:
        obj = drawpyo.XMLBase(xml_class="mxCell")
        assert obj.xml_open_tag == f'<mxCell id="{obj.id}">'

    def test_basic_close_tag(self) -> None:
        obj = drawpyo.XMLBase(xml_class="mxCell")
        assert obj.xml_close_tag == "</mxCell>"

    def test_basic_xml(self) -> None:
        obj = drawpyo.XMLBase(xml_class="mxCell")
        assert obj.xml == f'<mxCell id="{obj.id}" />'


class TestXmlIfy:
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
        ],
    )
    def test_xml_ify(self, input_str: str, expected: str) -> None:
        obj = drawpyo.XMLBase()
        assert obj.xml_ify(input_str) == expected


class TestTranslateTxt:
    def test_translate_txt(self) -> None:
        result = drawpyo.XMLBase.translate_txt("abc", {"a": "X", "c": "Z"})
        assert result == "XbZ"

    def test_translate_txt_no_replacements(self) -> None:
        result = drawpyo.XMLBase.translate_txt("hello", {})
        assert result == "hello"
