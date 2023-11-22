import drawpyo

file = drawpyo.File()
file.file_path = r"C:\drawpyo\Test Draw.io Charts"
file.file_name = "New Process Generation.drawio"
page = drawpyo.Page(file=file)


base_obj = drawpyo.diagram.BasicObject(page=page,
                                       rounded=1)


file.write()