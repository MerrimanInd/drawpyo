import pytest
from drawpyo import ColorScheme, StandardColor


# ============================================================
#  HEX VALIDATION
# ============================================================


@pytest.mark.parametrize(
    "value",
    [
        "#000000",
        "#FFFFFF",
        "#abcdef",
        "#A1B2C3",
        "#123abc",
    ],
)
def test_is_valid_hex_accepts_valid_hex(value):
    assert ColorScheme.is_valid_hex(value) is True


@pytest.mark.parametrize(
    "value",
    [
        "000000",  # missing '#'
        "#FFFFF",  # 5 chars
        "#FFFFFFF",  # 7 chars
        "#ZZZZZZ",  # non-hex
        "#12G45F",  # invalid character
        "#12345",  # short
        "#12345G",  # wrong char
    ],
)
def test_is_valid_hex_rejects_invalid_hex_strings(value):
    assert ColorScheme.is_valid_hex(value) is False


@pytest.mark.parametrize("value", [123, None])
def test_is_valid_hex_raises_for_non_string(value):
    with pytest.raises(TypeError):
        ColorScheme.is_valid_hex(value)


def test_regex_pattern_correctness():
    regex = ColorScheme.HEX_PATTERN
    assert regex.match("#A1B2C3")
    assert not regex.match("A1B2C3")
    assert not regex.match("#A1B2C")
    assert not regex.match("#A1B2C3D")


# ============================================================
#  ENUM HANDLING
# ============================================================


def test_enum_resolves_to_hex_value():
    scheme = ColorScheme(fill_color=StandardColor.BLACK)
    assert scheme.fill_color == "#000000"


def test_enum_allowed_in_setters():
    scheme = ColorScheme()
    scheme.set_stroke_color(StandardColor.WHITE)
    assert scheme.stroke_color == "#FFFFFF"


# ============================================================
#  HEX NORMALIZATION
# ============================================================


def test_hex_strings_normalize_to_uppercase():
    scheme = ColorScheme(fill_color="#a1b2c3")
    assert scheme.fill_color == "#A1B2C3"


# ============================================================
#  INVALID TYPES
# ============================================================


@pytest.mark.parametrize(
    "value",
    [
        123,
        5.5,
        ["#FFEEAA"],
        {"color": "#FFEEAA"},
        (1, 2),
    ],
)
def test_invalid_type_for_color_raises_type_error(value):
    with pytest.raises(TypeError):
        ColorScheme(fill_color=value)


# ============================================================
#  INVALID HEX STRING
# ============================================================


def test_invalid_hex_raises_value_error():
    with pytest.raises(ValueError):
        ColorScheme(fill_color="#GGGGGG")


# ============================================================
#  SETTERS WITH INVALID VALUES
# ============================================================


def test_setter_with_invalid_hex_raises():
    scheme = ColorScheme()
    with pytest.raises(ValueError):
        scheme.set_fill_color("#XYZ123")


def test_setter_with_invalid_type_raises():
    scheme = ColorScheme()
    with pytest.raises(TypeError):
        scheme.set_font_color(42)


# ============================================================
#  ALLOW NONE
# ============================================================


def test_none_values_allowed():
    scheme = ColorScheme(fill_color=None, stroke_color=None, font_color=None)
    assert scheme.fill_color is None
    assert scheme.stroke_color is None
    assert scheme.font_color is None


# ============================================================
#  COLOR HIERARCHY
#  object-specific > scheme > default
# ============================================================


class DummyTextFormat:
    """Minimal mock to simulate text format color."""

    def __init__(self, font_color=None):
        self.font_color = font_color


class DummyObject:
    """Mock object used only to test color resolution hierarchy."""

    DEFAULT_FILL = "#DAE8FC"
    DEFAULT_STROKE = "#6C8EBF"
    DEFAULT_FONT = "#000000"

    def __init__(
        self, fill_color=None, stroke_color=None, text_format=None, color_scheme=None
    ):
        self.fill_color = fill_color
        self.stroke_color = stroke_color
        self.text_format = text_format
        self.color_scheme = color_scheme

    def resolved_fill(self):
        if self.fill_color is not None:
            return self.fill_color
        if self.color_scheme and self.color_scheme.fill_color is not None:
            return self.color_scheme.fill_color
        return self.DEFAULT_FILL

    def resolved_stroke(self):
        if self.stroke_color is not None:
            return self.stroke_color
        if self.color_scheme and self.color_scheme.stroke_color is not None:
            return self.color_scheme.stroke_color
        return self.DEFAULT_STROKE

    def resolved_font(self):
        if self.text_format and self.text_format.font_color is not None:
            return self.text_format.font_color
        if self.color_scheme and self.color_scheme.font_color is not None:
            return self.color_scheme.font_color
        return self.DEFAULT_FONT


def test_hierarchy_object_specific_over_scheme():
    scheme = ColorScheme(fill_color="#111111")
    obj = DummyObject(fill_color="#222222", color_scheme=scheme)

    assert obj.resolved_fill() == "#222222"


def test_hierarchy_scheme_used_when_object_specific_missing():
    scheme = ColorScheme(stroke_color="#333333")
    obj = DummyObject(color_scheme=scheme)

    assert obj.resolved_stroke() == "#333333"


def test_hierarchy_defaults_used_when_both_missing():
    obj = DummyObject()

    assert obj.resolved_fill() == DummyObject.DEFAULT_FILL
    assert obj.resolved_stroke() == DummyObject.DEFAULT_STROKE
    assert obj.resolved_font() == DummyObject.DEFAULT_FONT


def test_hierarchy_font_object_specific_override():
    scheme = ColorScheme(font_color="#444444")
    tf = DummyTextFormat(font_color="#555555")
    obj = DummyObject(text_format=tf, color_scheme=scheme)

    assert obj.resolved_font() == "#555555"


def test_hierarchy_scheme_used_if_no_object_specific_font():
    scheme = ColorScheme(font_color="#444444")
    obj = DummyObject(color_scheme=scheme)

    assert obj.resolved_font() == "#444444"
