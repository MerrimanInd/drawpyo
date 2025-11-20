import drawpyo


# TODO rewrite this test so it's independent of the order of the style attributes
def test_obj_from_str():
    file = drawpyo.File()
    page = drawpyo.Page(file=file)

    # style string
    test_style_str = "whiteSpace=wrap;rounded=1;fillColor=#6a00ff;strokeColor=#000000;dashed=0;html=1;fontColor=#ffffff;gradientColor=#FF33FF;strokeWidth=4;"

    # Create a new object and apply the style string
    style_str_obj = drawpyo.diagram.Object(page=page)
    style_str_obj.apply_style_string(test_style_str)
    # Check that the exported style string matches
    assert style_str_obj.style == test_style_str

    # Create another object using that as a template
    template_obj = drawpyo.diagram.Object(page=page, template_object=style_str_obj)
    # Check that it has the same style
    assert template_obj.style == test_style_str

    # Create an object from the template a different way
    template_obj2 = drawpyo.diagram.Object.create_from_template_object(
        page=page, template_object=template_obj
    )
    # Check that it has the same style
    assert template_obj2.style == test_style_str
