import drawpyo

def test_page_init():
    test_page = drawpyo.Page()
    assert test_page.id == id(test_page)
    assert len(test_page.objects) == 2
    
    assert test_page.dx == 2037
    assert test_page.dy == 830
    assert test_page.grid == 1
    assert test_page.grid_size == 10
    assert test_page.guides == 1
    assert test_page.tooltips == 1
    assert test_page.connect == 1
    assert test_page.arrows == 1
    assert test_page.fold == 1
    assert test_page.scale == 1
    assert test_page.width == 850
    assert test_page.height == 1100
    assert test_page.math == 0
    assert test_page.shadow == 0
    
    assert test_page.diagram.xml_class == "diagram"
    assert test_page.mxGraph.xml_class == "mxGraphModel"
    assert test_page.root.xml_class == "root"
    
def test_page_xml():
    test_page = drawpyo.Page()
    
    open_tag_1 = f'<diagram name="Page-1" id="{test_page.diagram.id}">'
    open_tag_2 = f'    <mxGraphModel dx="{test_page.dx}" dy="{test_page.dy}" grid="{test_page.grid}" gridSize="{test_page.grid_size}" guides="{test_page.guides}" toolTips="{test_page.tooltips}" connect="{test_page.connect}" arrows="{test_page.arrows}" fold="{test_page.fold}" page="1" pageScale="{test_page.scale}" pageWidth="{test_page.width}" pageHeight="{test_page.height}" math="{test_page.math}" shadow="{test_page.shadow}">'
    open_tag_3 = f'      <root>'
    
    assert test_page.xml_open_tag.split("\n")[0] == open_tag_1
    assert test_page.xml_open_tag.split("\n")[1] == open_tag_2
    assert test_page.xml_open_tag.split("\n")[2] == open_tag_3
    
    close_tag_1 = "      </root>"
    close_tag_2 = "    </mxGraphModel>"
    close_tag_3 = "  </diagram>"
    
    assert test_page.xml_close_tag.split("\n")[0] == close_tag_1
    assert test_page.xml_close_tag.split("\n")[1] == close_tag_2
    assert test_page.xml_close_tag.split("\n")[2] == close_tag_3
    
    obj_tag_1 = '        <mxCell id="0" />'
    obj_tag_2 = '        <mxCell id="1" parent="0" />'
    
    assert test_page.xml == "\n".join([open_tag_1, open_tag_2, open_tag_3,
                                       obj_tag_1, obj_tag_2,
                                       close_tag_1, close_tag_2, close_tag_3])