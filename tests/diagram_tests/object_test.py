import drawpyo


def parse_style(style: str) -> dict[str, str]:
    """Convert a style string into a dict for order-independent comparison."""
    if not style:
        return {}

    parts = style.split(";")
    parsed = {}

    for part in parts:
        if "=" in part:
            key, value = part.split("=", 1)
            parsed[key] = value

    return parsed


def test_obj_from_str() -> None:
    file = drawpyo.File()
    page = drawpyo.Page(file=file)

    # style string
    test_style_str = (
        "whiteSpace=wrap;rounded=1;fillColor=#6a00ff;strokeColor=#000000;"
        "dashed=0;html=1;fontColor=#ffffff;gradientColor=#FF33FF;strokeWidth=4;"
    )

    expected_style = parse_style(test_style_str)

    # Create a new object and apply the style string
    style_str_obj = drawpyo.diagram.Object(page=page)
    style_str_obj.apply_style_string(test_style_str)

    # Compare style dicts (order-independent)
    assert parse_style(style_str_obj.style) == expected_style

    # Create another object using the first as a template
    template_obj = drawpyo.diagram.Object(page=page, template_object=style_str_obj)
    assert parse_style(template_obj.style) == expected_style

    # Create an object from the template a different way
    template_obj2 = drawpyo.diagram.Object.create_from_template_object(
        page=page,
        template_object=template_obj,
    )
    assert parse_style(template_obj2.style) == expected_style
