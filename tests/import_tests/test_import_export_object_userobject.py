import re

import pytest

from drawpyo import File, Page, load_diagram
from drawpyo.diagram import Edge, Object

SAMPLE_XML = """<mxfile host="Drawpyo">
<diagram name="Page-1">
  <mxGraphModel dx="2037" dy="830" grid="1">
    <root>
      <mxCell id="0"/>
      <mxCell id="1" parent="0"/>
      <object label="" test="test" id="2xg5nJA0Zl71o69cM8dW-4">
        <mxCell edge="1" parent="1" source="2xg5nJA0Zl71o69cM8dW-1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=0;exitY=0.5;exitDx=0;exitDy=0;entryX=0.5;entryY=1;entryDx=0;entryDy=0;" target="2xg5nJA0Zl71o69cM8dW-2">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
      </object>
      <object label="" test="test" id="2xg5nJA0Zl71o69cM8dW-1">
        <mxCell parent="1" style="rounded=0;whiteSpace=wrap;html=1;" vertex="1">
          <mxGeometry height="60" width="120" x="350" y="370" as="geometry" />
        </mxCell>
      </object>
      <mxCell id="2xg5nJA0Zl71o69cM8dW-5" edge="1" parent="1" source="2xg5nJA0Zl71o69cM8dW-2" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;exitX=1;exitY=0.5;exitDx=0;exitDy=0;" target="2xg5nJA0Zl71o69cM8dW-1">
        <mxGeometry relative="1" as="geometry" />
      </mxCell>
      <UserObject label="%name%" name="Name" link="data:page/id,hyHWzmBswkbCvm2kR1NW" id="2xg5nJA0Zl71o69cM8dW-2">
        <mxCell parent="1" style="rounded=0;whiteSpace=wrap;html=1;" vertex="1">
          <mxGeometry height="60" width="120" x="150" y="280" as="geometry" />
        </mxCell>
      </UserObject>
    </root>
  </mxGraphModel>
</diagram>
</mxfile>"""


@pytest.fixture
def diagram(tmp_path):
    file_path = tmp_path / "object_userobject.drawio"
    file_path.write_text(SAMPLE_XML)
    return load_diagram(str(file_path))


def test_object_userobject_import(diagram):
    assert diagram is not None
    assert len(diagram.shapes) == 2
    assert len(diagram.edges) == 2

    wrapped_edge = diagram.get_by_id("2xg5nJA0Zl71o69cM8dW-4")
    wrapped_obj = diagram.get_by_id("2xg5nJA0Zl71o69cM8dW-1")
    user_obj = diagram.get_by_id("2xg5nJA0Zl71o69cM8dW-2")

    assert isinstance(wrapped_edge, Edge)
    assert isinstance(wrapped_obj, Object)
    assert isinstance(user_obj, Object)

    assert wrapped_edge.object_attributes.get("test") == "test"
    assert wrapped_obj.object_attributes.get("test") == "test"
    assert (
        user_obj.user_object_attributes.get("link")
        == "data:page/id,hyHWzmBswkbCvm2kR1NW"
    )


def test_object_userobject_export(diagram):
    file = File(file_name="test.drawio", file_path=".")
    page = Page(file=file)

    diagram.add_to(page)

    xml = file.xml

    assert re.search(
        r'<object(?=[^>]*\bid="2xg5nJA0Zl71o69cM8dW-4")(?=[^>]*\btest="test")[^>]*>',
        xml,
    )
    assert re.search(
        rf'<UserObject(?=[^>]*\bid="2xg5nJA0Zl71o69cM8dW-2")(?=[^>]*\blink=\"data:page/id,{page.diagram.id}\")[^>]*>',
        xml,
    )
    assert "data:page/id,hyHWzmBswkbCvm2kR1NW" not in xml
    assert re.search(
        rf'<diagram[^>]*\bid="{page.diagram.id}"',
        xml,
    )
    assert re.search(
        r'<object[^>]*\bid="2xg5nJA0Zl71o69cM8dW-4"[^>]*>\s*<mxCell(?![^>]*\bid=)',
        xml,
    )
    assert re.search(
        r'<object[^>]*\bid="2xg5nJA0Zl71o69cM8dW-1"[^>]*>\s*<mxCell(?![^>]*\bid=)',
        xml,
    )
    assert re.search(
        r'<UserObject[^>]*\bid="2xg5nJA0Zl71o69cM8dW-2"[^>]*>\s*<mxCell(?![^>]*\bid=)',
        xml,
    )
    assert re.search(
        r'<object[^>]*\bid="2xg5nJA0Zl71o69cM8dW-4"[^>]*>\s*<mxCell(?![^>]*\bvalue=)',
        xml,
    )
    assert re.search(
        r'<UserObject[^>]*\bid="2xg5nJA0Zl71o69cM8dW-2"[^>]*>\s*<mxCell(?![^>]*\bvalue=)',
        xml,
    )


def test_parsed_diagram_add_to_offset(diagram):
    file = File(file_name="test.drawio", file_path=".")
    page = Page(file=file)

    diagram.add_to(page, offset=(10, 20))

    obj_1 = diagram.get_by_id("2xg5nJA0Zl71o69cM8dW-1")
    obj_2 = diagram.get_by_id("2xg5nJA0Zl71o69cM8dW-2")

    assert obj_1 is not None
    assert obj_2 is not None
    assert obj_1.position == (360, 390)
    assert obj_2.position == (160, 300)
