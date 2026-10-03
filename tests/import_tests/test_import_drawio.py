import base64
import xml.etree.ElementTree as ET
import zlib
from urllib.parse import quote

import drawpyo
import pytest
from drawpyo import File, Page, load_diagram
from drawpyo.diagram import Object, Edge

# Sample XML string for testing
SAMPLE_XML = """<mxfile host="Drawpyo">
<diagram name="Page-1">
  <mxGraphModel dx="2037" dy="830" grid="1">
    <root>
      <mxCell id="0"/>
      <mxCell id="1" parent="0"/>
      <mxCell id="100" value="List" style="swimlane" parent="1" vertex="1">
        <mxGeometry x="150" y="100" width="140" height="120" as="geometry"/>
      </mxCell>
      <mxCell id="101" value="Item 1" parent="100" vertex="1">
        <mxGeometry y="30" width="140" height="30" as="geometry"/>
      </mxCell>
      <mxCell id="102" value="Item 2" parent="100" vertex="1">
        <mxGeometry y="60" width="140" height="30" as="geometry"/>
      </mxCell>
    </root>
  </mxGraphModel>
</diagram>
</mxfile>"""


class TestDrawpyoParsing:
    @pytest.fixture
    def diagram(self, tmp_path):
        """Fixture that writes XML to a temp file and loads it"""
        file_path = tmp_path / "test.drawio"
        file_path.write_text(SAMPLE_XML)
        return load_diagram(str(file_path))

    def test_diagram_loads(self, diagram):
        """Test that the diagram loads and has correct element counts"""
        assert diagram is not None
        assert diagram.element_count == 3  # 1 list + 2 items

    def test_shapes_are_objects(self, diagram):
        """Test that all shapes are instances of Object"""
        for shape in diagram.shapes:
            assert isinstance(shape, Object)

    def test_get_by_id(self, diagram):
        """Test retrieval of elements by ID"""
        list_obj = diagram.get_by_id("100")
        item1_obj = diagram.get_by_id("101")
        item2_obj = diagram.get_by_id("102")

        assert list_obj is not None
        assert item1_obj is not None
        assert item2_obj is not None
        assert item1_obj in list_obj.children
        assert item2_obj in list_obj.children

    def test_geometry_parsing(self, diagram):
        """Test geometry values are parsed correctly"""
        list_obj = diagram.get_by_id("100")
        item1_obj = diagram.get_by_id("101")
        item2_obj = diagram.get_by_id("102")

        assert list_obj.geometry.x == 150
        assert list_obj.geometry.y == 100
        assert list_obj.geometry.width == 140
        assert list_obj.geometry.height == 120

        # Relative y-coordinates of children
        assert item1_obj.geometry.y == 30
        assert item2_obj.geometry.y == 60

    def test_children_hierarchy(self, diagram):
        """Test that children are correctly attached to parent"""
        list_obj = diagram.get_by_id("100")
        item1_obj = diagram.get_by_id("101")
        item2_obj = diagram.get_by_id("102")

        assert item1_obj in list_obj.children
        assert item2_obj in list_obj.children

    def test_no_edges(self, diagram):
        """Test that edges list is empty when no edges exist"""
        assert len(diagram.edges) == 0

    def test_shape_values(self, diagram):
        assert diagram.get_by_id("100").value == "List"
        assert diagram.get_by_id("101").value == "Item 1"
        assert diagram.get_by_id("102").value == "Item 2"


@pytest.mark.parametrize(
    "value",
    ["Hello", "A & B <C> \"quoted\" 'apostrophe'", "Grüße 世界\nsecond line", ""],
)
def test_shape_text_survives_import_export(tmp_path, value):
    root = ET.fromstring(SAMPLE_XML)
    root.find(".//mxCell[@id='101']").set("value", value)
    source_path = tmp_path / "source.drawio"
    ET.ElementTree(root).write(source_path, encoding="utf-8")

    diagram = load_diagram(str(source_path))
    assert diagram.get_by_id("101").value == value

    output = File(file_path=str(tmp_path), file_name="exported.drawio")
    diagram.add_to(Page(file=output))
    output_path = output.write()

    exported = ET.parse(output_path)
    assert exported.find(".//mxCell[@id='101']").get("value") == value
    reloaded = load_diagram(output_path)
    assert reloaded.get_by_id("101").value == value


def _page_model(value, layer="1"):
    model = ET.Element("mxGraphModel")
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id=layer, parent="0")
    shape = ET.SubElement(
        root, "mxCell", id="shape", vertex="1", parent=layer, value=value
    )
    ET.SubElement(shape, "mxGeometry", x="45", y="90", width="50", height="60")
    child = ET.SubElement(
        root, "mxCell", id="child", vertex="1", parent="shape", value="child"
    )
    ET.SubElement(child, "mxGeometry", x="5", y="10", width="0", height="20")
    ET.SubElement(
        root,
        "mxCell",
        id="edge",
        edge="1",
        parent=layer,
        source="shape",
        target="child",
    )
    return model


def _add_page(mxfile, page_id, name, value, compressed=False, layer="1"):
    diagram = ET.SubElement(mxfile, "diagram", id=page_id, name=name)
    model = _page_model(value, layer)
    if compressed:
        compressor = zlib.compressobj(wbits=-15)
        encoded = quote(ET.tostring(model, encoding="unicode"), safe="").encode("utf-8")
        payload = base64.b64encode(
            compressor.compress(encoded) + compressor.flush()
        ).decode("ascii")
        # Draw.io payloads can be wrapped in whitespace.
        diagram.text = "\n" + payload[:20] + "\n" + payload[20:] + "\n"
    else:
        diagram.append(model)


@pytest.mark.parametrize("compressed", [False, True])
def test_single_page_formats_preserve_text_hierarchy_and_geometry(tmp_path, compressed):
    source = ET.Element("mxfile")
    value = 'Grüße 世界 & <tag> "quoted"\nsecond line'
    _add_page(source, "page-a", "First page", value, compressed, layer="custom-layer")
    path = tmp_path / "source.drawio"
    ET.ElementTree(source).write(path, encoding="utf-8")

    diagram = load_diagram(str(path))

    assert diagram.page_id == "page-a"
    assert diagram.name == "First page"
    shape = diagram.get_by_id("shape")
    child = diagram.get_by_id("child")
    assert shape.value == value
    assert shape.position == (45, 90)
    assert (shape.width, shape.height) == (50, 60)
    assert child.parent is shape
    assert child.position_rel_to_parent == (5, 10)
    assert (child.width, child.height) == (0, 20)
    assert diagram.get_by_id("edge").source is shape
    assert diagram.get_by_id("edge").target is child


def test_mixed_pages_with_reused_ids_remain_independent_after_export(tmp_path):
    source = ET.Element("mxfile")
    _add_page(source, "page-a", "First page", "first")
    _add_page(
        source, "page-b", "Second page", "second", compressed=True, layer="custom-layer"
    )
    path = tmp_path / "source.drawio"
    ET.ElementTree(source).write(path, encoding="utf-8")

    diagrams = drawpyo.load_diagrams(str(path))

    assert [d.page_id for d in diagrams] == ["page-a", "page-b"]
    assert [d.name for d in diagrams] == ["First page", "Second page"]
    assert [d.get_by_id("shape").value for d in diagrams] == ["first", "second"]
    assert diagrams[0].get_by_id("shape") is not diagrams[1].get_by_id("shape")
    for diagram in diagrams:
        assert diagram.element_count == 3
        assert diagram.get_by_id("child").parent is diagram.get_by_id("shape")
        assert diagram.get_by_id("edge").source is diagram.get_by_id("shape")
        assert diagram.get_by_id("edge").target is diagram.get_by_id("child")

    output = File(file_path=str(tmp_path), file_name="exported.drawio")
    for diagram in diagrams:
        diagram.add_to(Page(file=output, name=diagram.name))
    exported = drawpyo.load_diagrams(output.write())
    assert [d.name for d in exported] == ["First page", "Second page"]
    assert [d.get_by_id("shape").value for d in exported] == ["first", "second"]
    assert [d.get_by_id("shape").position for d in exported] == [(45, 90), (45, 90)]


def test_multipage_load_requires_explicit_selection(tmp_path):
    source = ET.Element("mxfile")
    _add_page(source, "a", "First", "first")
    _add_page(source, "b", "Second", "second")
    path = tmp_path / "source.drawio"
    ET.ElementTree(source).write(path, encoding="utf-8")

    with pytest.raises(ValueError, match="multiple pages"):
        load_diagram(str(path))
    assert load_diagram(str(path), page_index=0).get_by_id("shape").value == "first"
    assert load_diagram(str(path), page_index=1).get_by_id("shape").value == "second"
    for invalid_index in (-1, 2, "1"):
        with pytest.raises(ValueError, match="page_index"):
            load_diagram(str(path), page_index=invalid_index)


@pytest.mark.parametrize("wrap_diagram", [False, True])
def test_standalone_graph_and_diagram_are_supported(tmp_path, wrap_diagram):
    source = _page_model("standalone")
    if wrap_diagram:
        diagram = ET.Element("diagram", id="standalone", name="Standalone")
        diagram.append(source)
        source = diagram
    path = tmp_path / "source.xml"
    ET.ElementTree(source).write(path, encoding="utf-8")

    assert load_diagram(str(path)).get_by_id("shape").value == "standalone"


def test_empty_pages_are_retained_in_order(tmp_path):
    source = ET.Element("mxfile")
    empty = ET.SubElement(source, "diagram", id="empty", name="Empty")
    model = ET.SubElement(empty, "mxGraphModel")
    ET.SubElement(model, "root")
    _add_page(source, "full", "Full", "shape")
    path = tmp_path / "source.drawio"
    ET.ElementTree(source).write(path, encoding="utf-8")

    diagrams = drawpyo.load_diagrams(str(path))

    assert [d.page_id for d in diagrams] == ["empty", "full"]
    assert diagrams[0].element_count == 0
    assert diagrams[1].element_count == 3


@pytest.mark.parametrize("payload", ["not base64!", "YWJj", ""])
def test_invalid_compressed_page_raises_clear_error(tmp_path, payload):
    source = ET.Element("mxfile")
    ET.SubElement(source, "diagram", name="Broken").text = payload
    path = tmp_path / "broken.drawio"
    ET.ElementTree(source).write(path, encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid compressed Draw.io page 'Broken'"):
        load_diagram(str(path))


@pytest.mark.parametrize("xml", ["<unrelated/>", "<mxfile/>", "<mxfile>"])
def test_invalid_document_raises_value_error(tmp_path, xml):
    path = tmp_path / "invalid.xml"
    path.write_text(xml, encoding="utf-8")

    with pytest.raises(ValueError):
        load_diagram(str(path))
