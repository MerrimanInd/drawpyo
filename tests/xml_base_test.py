from hypothesis import given, strategies as st

import drawpyo


def test_XMLBase_init():
    test_obj = drawpyo.XMLBase()
    assert test_obj.id == id(test_obj)
    assert test_obj.xml_class == "xml_tag"
    assert test_obj.attributes == {"id": id(test_obj), "parent": None}


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

    assert test_obj.xml_ify(">") == "&gt;"
    assert test_obj.xml_ify("<") == "&lt;"
    assert test_obj.xml_ify("&") == "&amp;"
    assert test_obj.xml_ify('"') == "&quot;"
    assert test_obj.xml_ify("'") == "&apos;"



xmlbase_kwargs_strategy = st.fixed_dictionaries(
    mapping={},  # No required keys
    optional={
        "id": st.just(st.integers()),
        "xml_class": st.one_of(st.text(), st.none()),
        "xml_parent": st.one_of(st.integers(), st.text(), st.none()),
        "tag": st.one_of(st.text(), st.none()),
    }
)


@given(kwargs=xmlbase_kwargs_strategy)
def test_xmlbase(kwargs):
    obj = drawpyo.XMLBase(**kwargs)

    # 'id' default is generated from id(self)
    if "id" in kwargs:
        assert obj._id == kwargs["id"]
    else:
        assert isinstance(obj._id, int)

    assert obj.xml_class == kwargs.get("xml_class", "xml_tag")
    assert obj.xml_parent == kwargs.get("xml_parent", None)
    assert obj.tag == kwargs.get("tag", None)
