from hypothesis import given, strategies as st

from drawpyo import XMLBase, Page
from drawpyo.diagram import DiagramBase, Geometry


def test_diagram_base_init():
    test_page = Page()
    test_dbase = DiagramBase(page=test_page)

    assert test_dbase.xml_class == "xml_tag"
    assert test_dbase.page == test_page
    assert test_dbase.style_attributes == ["html"]


# Strategy for valid XMLBase-like values
xml_parent_strategy = st.one_of(st.none(), st.just(Page()))
page_strategy = st.one_of(st.none(), st.just(Page()))

diagram_base_kwargs_strategy = st.fixed_dictionaries(
    mapping={},  # No required keys
    optional={
        "id": st.just(st.integers()),
        "xml_class": st.one_of(st.none(), st.text()),
        "xml_parent": xml_parent_strategy,
        "tag": st.one_of(st.none(), st.text()),
        "page": page_strategy,
    }
)


@given(kwargs=diagram_base_kwargs_strategy)
def test_diagram_base(kwargs):
    obj = DiagramBase(**kwargs)

    # _id logic from XMLBase
    if "id" in kwargs:
        assert obj._id == kwargs["id"]
    else:
        assert isinstance(obj._id, int)

    # xml_class
    assert obj.xml_class == kwargs.get("xml_class", "xml_tag")

    # tag
    assert obj.tag == kwargs.get("tag", None)

    # page
    if "page" in kwargs:
        assert obj.page == kwargs["page"]
        if kwargs["page"] is not None:
            assert isinstance(kwargs["page"], Page)
    else:
        assert obj.page is None

    # _style_attributes
    assert obj._style_attributes == ["html"]

    # xml_parent override from DiagramBase
    if "xml_parent" in kwargs:
        assert obj.xml_parent == kwargs["xml_parent"]
        if kwargs["xml_parent"] is not None:
            assert isinstance(kwargs["xml_parent"], Page)
    else:
        assert obj.xml_parent is None


# Strategy for optional dependencies
xml_parent_strategy = st.one_of(st.none(), st.just(Page()))
page_strategy = st.one_of(st.none(), st.just(Page()))
parent_object_strategy = st.one_of(st.none(), st.just(Page()))

geometry_kwargs_strategy = st.fixed_dictionaries(
    mapping={},
    optional={
        "x": st.one_of(st.none(), st.integers(), st.floats(allow_nan=False, allow_infinity=False)),
        "y": st.one_of(st.none(), st.integers(), st.floats(allow_nan=False, allow_infinity=False)),
        "width": st.one_of(st.none(), st.integers(min_value=0, max_value=500)),
        "height": st.one_of(st.none(), st.integers(min_value=0, max_value=500)),
        "as_attribute": st.one_of(st.none(), st.text(min_size=1, max_size=10)),
        "xml_class": st.one_of(st.none(), st.text(min_size=1, max_size=10)),
        "tag": st.one_of(st.none(), st.text(min_size=1, max_size=10)),
        "page": page_strategy,
        "xml_parent": xml_parent_strategy,
        "parent_object": parent_object_strategy,
    }
)


@given(kwargs=geometry_kwargs_strategy)
def test_geometry(kwargs):
    obj = Geometry(**kwargs)

    # xml_class is overridden
    assert obj.xml_class == "mxGeometry"

    # Inherited: tag
    assert obj.tag == kwargs.get("tag", None)

    # Inherited: page
    if "page" in kwargs:
        assert obj.page == kwargs["page"]
        if kwargs["page"] is not None:
            assert isinstance(obj.page, Page)
    else:
        assert obj.page is None

    # Inherited: xml_parent
    if "xml_parent" in kwargs:
        assert obj.xml_parent == kwargs["xml_parent"]
        if kwargs["xml_parent"] is not None:
            assert isinstance(obj.xml_parent, Page)
    else:
        assert obj.xml_parent is None

    # Geometry-specific
    assert obj.parent_object == kwargs.get("parent_object", None)
    assert obj.x == kwargs.get("x", 0)
    assert obj.y == kwargs.get("y", 0)
    assert obj.width == kwargs.get("width", 120)
    assert obj.height == kwargs.get("height", 60)
    assert obj.as_attribute == kwargs.get("as_attribute", "geometry")

    # Derived properties
    assert obj.size == (obj.width, obj.height)
    assert obj.attributes == {
        "x": obj.x,
        "y": obj.y,
        "width": obj.width,
        "height": obj.height,
        "as": obj.as_attribute,
    }

    # Check setter for size
    obj.size = (200, 100)
    assert obj.width == 200
    assert obj.height == 100
