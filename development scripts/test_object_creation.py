
import drawpyo

file = drawpyo.File()
file.file_path = r"C:\drawpyo\Test Draw.io Charts"
file.file_name = "Test Generated Diagram.drawio"
page = drawpyo.Page(file=file)

top_level = drawpyo.diagram.ObjectBase(page = page, value="top level item")
top_level.position = (page.page_width/2, 15)

mid_level = drawpyo.diagram.ObjectBase(page = page, value="mid level item")
mid_level.position = (page.page_width/2, 115)

link = drawpyo.diagram.EdgeBase(page=page, source=top_level, target=mid_level)

file.write()