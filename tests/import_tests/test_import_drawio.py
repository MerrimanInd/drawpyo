import pytest
from drawpyo import load_diagram
from drawpyo.diagram import Object, Edge

# Sample Draw.io XML string for testing
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


# -----------------------------
# Pytest Suite
# -----------------------------
class TestDrawpyoParsing:
    """Class-based tests for Drawpyo diagram parsing"""

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
