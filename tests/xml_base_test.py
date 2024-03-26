import drawpyo

# content of test_sample.py
def inc(x):
    return x + 1


def test_answer():
    assert inc(3) == 4


def test_XMLBase_init():
    test_obj = drawpyo.XMLBase()
    assert test_obj.id == id(test_obj)
    assert test_obj.xml_class == "xml_tag"
    assert test_obj.attributes == {"id": id(test_obj),
                                   "parent": None}
    
def test_XMLBase_tags():
    test_obj = drawpyo.XMLBase(xml_class="mxCell")
    expected_xml_open_tag = f'<mxCell id="{test_obj.id}">'
    expected_xml_close_tag = f"</mxCell>"
    expected_xml = f'<mxCell id="{test_obj.id}" />'
    assert test_obj.xml_open_tag == expected_xml_open_tag
    assert test_obj.xml_close_tag == expected_xml_close_tag
    assert test_obj.xml == expected_xml
    
def test_XMLBase_xml_ify():
    test_obj = drawpyo.XMLBase(xml_class="mxCell")
    
    assert test_obj.xml_ify('>') == "&gt;"
    assert test_obj.xml_ify('<') == "&lt;"
    assert test_obj.xml_ify('&') == "&amp;"
    assert test_obj.xml_ify('"') == "&quot;"
    assert test_obj.xml_ify("'") == "&#39;"