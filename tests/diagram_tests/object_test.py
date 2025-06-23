from hypothesis import given, strategies as st

from drawpyo import Page, XMLBase, File
from drawpyo.diagram import Object, Geometry, TextFormat


# TODO rewrite this test so it's independent of the order of the style attributes
def test_obj_from_str():
    file = File()
    page = Page(file=file)

    # style string
    test_style_str = "whiteSpace=wrap;rounded=1;fillColor=#6a00ff;strokeColor=#000000;dashed=0;html=1;fontColor=#ffffff;gradientColor=#FF33FF;strokeWidth=4;"

    # Create a new object and apply the style string
    style_str_obj = Object(page=page)
    style_str_obj.apply_style_string(test_style_str)
    # Check that the exported style string matches
    assert style_str_obj.style == test_style_str

    # Create another object using that as a template
    template_obj = Object(page=page, template_object=style_str_obj)
    # Check that it has the same style
    assert template_obj.style == test_style_str

    # Create an object from the template a different way
    template_obj2 = Object.create_from_template_object(
        page=page, template_object=template_obj
    )
    # Check that it has the same style
    assert template_obj2.style == test_style_str


position_strategy = st.tuples(st.integers(0, 1000), st.integers(0, 1000))
text_strategy = st.text(min_size=0, max_size=50)
int_strategy = st.integers(min_value=0, max_value=500)
bool_strategy = st.booleans()
opacity_strategy = st.integers(min_value=0, max_value=100)
color_strategy = st.from_regex(r"^#[0-9a-fA-F]{6}$", fullmatch=True)
line_pattern_strategy = st.sampled_from([
    "solid",
    "small_dash",
    "medium_dash",
    "large_dash",
    "small_dot",
    "medium_dot",
    "large_dot",
])
object_strategy = st.builds(Object)

@given(
    kwargs=st.fixed_dictionaries(
        mapping={
            "value": text_strategy,
            "position": position_strategy,
        },
        optional={
            "position_rel_to_parent": position_strategy,
            "width": int_strategy,
            "height": int_strategy,
            "vertex": st.integers(0, 1),
            "aspect": st.one_of(st.none(), text_strategy),
            "rounded": st.integers(0, 1),
            "whiteSpace": text_strategy,
            "fillColor": st.one_of(st.none(), color_strategy),
            "opacity": st.one_of(st.none(), opacity_strategy),
            "strokeColor": st.one_of(st.none(), color_strategy),
            "glass": st.one_of(st.none(), bool_strategy),
            "shadow": st.one_of(st.none(), bool_strategy),
            "sketch": st.one_of(st.none(), bool_strategy),
            "comic": st.one_of(st.none(), bool_strategy),
            "autosize_to_children": bool_strategy,
            "autocontract": bool_strategy,
            "autosize_margin": int_strategy,
            "children": st.lists(object_strategy, max_size=3),
            "in_edges": st.lists(st.just(XMLBase())),
            "out_edges": st.lists(st.just(XMLBase())),
            "line_pattern": line_pattern_strategy,
            "baseStyle": st.one_of(st.none(), text_strategy),
            "text_format": st.just(TextFormat()),
            "page": st.just(Page()),
            "tag": st.one_of(st.none(), text_strategy),
        }
    )
)
def test_object(kwargs):
    obj = Object(**kwargs)

    assert isinstance(obj, Object)
    assert isinstance(obj.geometry, Geometry)
    assert isinstance(obj.text_format, TextFormat)
    assert obj.xml_class == "mxCell"
    assert isinstance(obj._style_attributes, list)
    assert isinstance(obj.position, tuple)
    assert isinstance(obj.width, int)
    assert isinstance(obj.height, int)
    assert isinstance(obj.value, str)
    assert isinstance(obj.line_pattern, str)
    assert obj.vertex in [0, 1]
