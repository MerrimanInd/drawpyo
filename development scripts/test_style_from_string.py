import drawpyo

file = drawpyo.File()
file.file_path = r"C:\drawpyo\Test Draw.io Charts"
file.file_name = "Apply_Style_From_String.drawio"
page = drawpyo.Page(file=file)

style_str_obj = drawpyo.diagram.BasicObject(page=page)

style_str_obj.apply_style_string("rounded=1;whiteSpace=wrap;html=1;fillColor=#6a00ff;fontColor=#ffffff;strokeColor=#000000;gradientColor=#FF33FF;strokeWidth=4;")

template_obj = drawpyo.diagram.BasicObject(page=page, template_object=style_str_obj)
template_obj.position = (300,0)

file.write()