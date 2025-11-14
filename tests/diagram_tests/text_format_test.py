from hypothesis import given, strategies as st
from drawpyo.diagram import TextFormat

# Strategies
hex_color_strategy = st.from_regex(r"^#[0-9a-fA-F]{6}$", fullmatch=True)
font_family_strategy = st.text(min_size=1, max_size=20)
font_size_strategy = st.integers(min_value=1, max_value=200)
align_strategy = st.sampled_from(["left", "center", "right"])
vertical_align_strategy = st.sampled_from(["top", "middle", "bottom"])
direction_strategy = st.sampled_from(["horizontal", "vertical"])
bool_strategy = st.booleans()
text_opacity_strategy = st.integers(min_value=0, max_value=100)
spacing_strategy = st.integers(min_value=0, max_value=100)
label_position_strategy = align_strategy

text_format_strategy = st.fixed_dictionaries(
    mapping={},
    optional={
        "fontColor": hex_color_strategy,
        "fontFamily": font_family_strategy,
        "fontSize": font_size_strategy,
        "align": align_strategy,
        "verticalAlign": vertical_align_strategy,
        "direction": direction_strategy,
        "formattedText": bool_strategy,
        "bold": bool_strategy,
        "italic": bool_strategy,
        "underline": bool_strategy,
        "labelPosition": label_position_strategy,
        "labelBackgroundColor": hex_color_strategy,
        "labelBorderColor": hex_color_strategy,
        "textShadow": st.one_of(st.none(), bool_strategy),
        "textOpacity": text_opacity_strategy,
        "spacingTop": spacing_strategy,
        "spacingLeft": spacing_strategy,
        "spacingBottom": spacing_strategy,
        "spacingRight": spacing_strategy,
        "spacing": spacing_strategy,
    }
)


@given(kwargs=text_format_strategy)
def test_text_format(kwargs):
    fmt = TextFormat(**kwargs)

    # Verify that passed values are retained
    for key, value in kwargs.items():
        assert getattr(fmt, key) == value

    # Always present attributes
    assert isinstance(fmt._style_attributes, list)
    assert "html" in fmt._style_attributes