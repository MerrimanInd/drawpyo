from hypothesis import given, strategies as st

from drawpyo import Page
from drawpyo.diagram import Edge, DiagramBase, TextFormat, EdgeGeometry, EdgeLabel

# Reusable strategies
diagram_base_strategy = st.just(DiagramBase())
text_strategy = st.text(min_size=1, max_size=20)
bool_strategy = st.booleans()
int_strategy = st.integers(min_value=0, max_value=1000)
opacity_strategy = st.integers(min_value=0, max_value=100)
label_position_strategy = st.floats(min_value=-1.0, max_value=1.0)
stroke_width_strategy = st.integers(min_value=1, max_value=999)
jetty_size_strategy = st.one_of(st.integers(min_value=0, max_value=100), st.just("auto"))
color_strategy = st.one_of(
    st.just("none"),
    st.just("default"),
    st.from_regex(r"^#[0-9a-fA-F]{6}$", fullmatch=True).map(str.strip)
)
connection_strategy = st.sampled_from(["line", "link", "arrow", "simple_arrow"])
waypoints_strategy = st.sampled_from([
    "straight", "orthogonal", "vertical", "horizontal", "isometric",
    "isometric_vertical", "curved", "entity_relation"
])
pattern_strategy = st.sampled_from([
    "solid",
    "dashed_small", "dashed_medium", "dashed_large",
    "dotted_small", "dotted_medium", "dotted_large"
])
line_ends_strategy = st.sampled_from([
    "classic", "classicThin", "open", "openThin", "openAsync",
    "block", "blockThin", "async", "oval", "diamond", "diamondThin",
    "dash", "halfCircle", "cross", "circlePlus", "circle", "baseDash",
    "ERone", "ERmandOne", "ERmany", "ERoneToMany", "ERzeroToOne",
    "ERzeroToMany", "doubleBlock"
])
jump_style_strategy = st.sampled_from(["arc", "gap", "sharp", "line"])

edge_kwargs_strategy = st.fixed_dictionaries(
    mapping={},  # No required keys
    optional={
        "source": st.one_of(st.none(), diagram_base_strategy),
        "target": st.one_of(st.none(), diagram_base_strategy),
        "label": st.one_of(st.none(), text_strategy),
        "label_position": st.one_of(st.none(), label_position_strategy),
        "label_offset": st.one_of(st.none(), int_strategy),
        "waypoints": waypoints_strategy,
        "connection": st.one_of(st.none(), connection_strategy),
        "pattern": st.one_of(st.none(), pattern_strategy),
        "shadow": st.one_of(st.none(), bool_strategy),
        "rounded": bool_strategy,
        "flowAnimation": st.one_of(st.none(), bool_strategy),
        "sketch": st.one_of(st.none(), bool_strategy),
        "line_end_target": st.one_of(st.none(), line_ends_strategy),
        "line_end_source": st.one_of(st.none(), line_ends_strategy),
        "endFill_target": bool_strategy,
        "endFill_source": bool_strategy,
        "endSize": st.one_of(st.none(), int_strategy),
        "startSize": st.one_of(st.none(), int_strategy),
        "jettySize": jetty_size_strategy,
        "targetPerimeterSpacing": st.one_of(st.none(), int_strategy),
        "sourcePerimeterSpacing": st.one_of(st.none(), int_strategy),
        "entryX": st.one_of(st.none(), st.integers(min_value=0, max_value=1)),
        "entryY": st.one_of(st.none(), st.integers(min_value=0, max_value=1)),
        "entryDx": st.one_of(st.none(), int_strategy),
        "entryDy": st.one_of(st.none(), int_strategy),
        "exitX": st.one_of(st.none(), st.integers(min_value=0, max_value=1)),
        "exitY": st.one_of(st.none(), st.integers(min_value=0, max_value=1)),
        "exitDx": st.one_of(st.none(), int_strategy),
        "exitDy": st.one_of(st.none(), int_strategy),
        "strokeColor": color_strategy,
        "strokeWidth": stroke_width_strategy,
        "fillColor": color_strategy,
        "jumpStyle": st.one_of(st.none(), jump_style_strategy),
        "jumpSize": st.one_of(st.none(), int_strategy),
        "opacity": st.one_of(st.none(), opacity_strategy),
    }
)

@given(kwargs=edge_kwargs_strategy)
def test_edge(kwargs):
    edge = Edge(**kwargs)

    assert edge.xml_class == "mxCell"
    assert isinstance(edge.text_format, TextFormat)
    assert isinstance(edge.geometry, EdgeGeometry)
    assert edge.edge == 1
    assert edge.rounded in [0, 1]

    # Spot-check that some passed values are preserved
    if "source" in kwargs:
        assert edge.source == kwargs["source"]
    if "target" in kwargs:
        assert edge.target == kwargs["target"]
    if "waypoints" in kwargs:
        assert edge.waypoints == kwargs["waypoints"]
    if "connection" in kwargs:
        assert edge.connection == kwargs["connection"]
    if "pattern" in kwargs:
        assert edge.pattern == kwargs["pattern"]
    if "strokeColor" in kwargs:
        assert edge.strokeColor == kwargs["strokeColor"]


edge_geometry_kwargs_strategy = st.fixed_dictionaries(
    mapping={},  # No required keys
    optional={
        "relative": st.booleans(),
        "points": st.lists(
            st.tuples(
                st.floats(allow_nan=False, allow_infinity=False),
                st.floats(allow_nan=False, allow_infinity=False)
            ),
            max_size=10
        ),
        "as_attribute": st.text(min_size=1, max_size=20),
        "xml_parent": st.one_of(st.none(), st.just(Page())),
        "page": st.one_of(st.none(), st.just(Page())),
    }
)

@given(edge_kwargs=edge_geometry_kwargs_strategy)
def test_edge_geometry(edge_kwargs):
    obj = EdgeGeometry(**edge_kwargs)

    # Check hardcoded xml_class
    assert obj.xml_class == "mxGeometry"

    # Check defaults or passed values
    assert obj.relative == edge_kwargs.get("relative", 1)
    assert obj.points == edge_kwargs.get("points", [])
    assert obj.as_attribute == edge_kwargs.get("as_attribute", "geometry")
    assert obj.page == edge_kwargs.get("page", None)
    assert obj.xml_parent == edge_kwargs.get("xml_parent", None)


# Optional inherited base class values
page_strategy = st.one_of(st.none(), st.just(Page()))
xml_parent_strategy = st.one_of(st.none(), st.just(Page()))

# Strategy for EdgeLabel-specific kwargs
edge_label_kwargs_strategy = st.fixed_dictionaries(
    mapping={},  # No required keys
    optional={
        "value": st.text(min_size=0, max_size=50),
        "style": st.text(min_size=5, max_size=200),
        "vertex": st.integers(min_value=0, max_value=1),
        "connectable": st.integers(min_value=0, max_value=1),
        "tag": st.one_of(st.none(), st.text(min_size=1, max_size=10)),
        "xml_class": st.one_of(st.none(), st.text(min_size=1, max_size=10)),
        "page": page_strategy,
        "xml_parent": xml_parent_strategy,
    }
)

@given(kwargs=edge_label_kwargs_strategy)
def test_edge_label(kwargs):
    obj = EdgeLabel(**kwargs)

    # xml_class should always be overridden to "mxCell"
    assert obj.xml_class == "mxCell"

    # Check default or provided values
    assert obj.value == kwargs.get("value", "")
    assert obj.style == kwargs.get("style", obj.default_style)
    assert obj.vertex == kwargs.get("vertex", 1)
    assert obj.connectable == kwargs.get("connectable", 1)

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

    # Style attribute is fixed
    assert obj._style_attributes == ["html"]

    # attributes property
    assert obj.attributes == []