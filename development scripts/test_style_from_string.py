import drawpyo
from os import path

file = drawpyo.File()
file.file_path = path.join(path.expanduser('~'), "Test Drawpyo Charts")
file.file_name = "Apply_Style_From_String.drawio"
page = drawpyo.Page(file=file)

style_str_obj = drawpyo.diagram.Object(page=page)

style_str_obj.apply_style_string("rounded=1;whiteSpace=wrap;html=1;fillColor=#6a00ff;fontColor=#ffffff;strokeColor=#000000;gradientColor=#FF33FF;strokeWidth=4;")
style_str_obj.position = (10, 10)

template_obj = drawpyo.diagram.Object(page=page, template_object=style_str_obj)
template_obj.position = (300,10)

template_obj2 = drawpyo.diagram.Object.create_from_template_object(
    page=page,
    template_object=template_obj,
    position = (600, 10),
    )

file.write()