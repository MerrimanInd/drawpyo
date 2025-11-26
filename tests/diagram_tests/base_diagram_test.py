import drawpyo


def test_diagram_base_init() -> None:
    test_page = drawpyo.Page()
    test_dbase = drawpyo.diagram.DiagramBase(page=test_page)

    assert test_dbase.xml_class == "xml_tag"
    assert test_dbase.page == test_page
    assert test_dbase.style_attributes == ["html"]
