import drawpyo

file = drawpyo.File()
file.file_path = r"C:\drawpyo\Test Draw.io Charts"
file.file_name = "Test Generated Edges.drawio"
page = drawpyo.Page(file=file)

line_shapes = [None, "straight", "orthogonal", "vertical", "horizontal", "isometric", "isometric_vertical", "curved", "entity_relation"]

line_types = [None, "line", "link", "arrow", "simple_arrow"]

line_styles = [None, "solid", "dashed_small", "dashed_medium", "dashed_large", "dotted_small", "dotted_medium", "dotted_large"]

line_ends = [
    None,
    "classic",
    "classicThin",
    "open",
    "openThin",
    "openAsync",
    "block",
    "blockThin",
    "async",
    "oval",
    "diamond",
    "diamondThin",
    "dash",
    "halfCircle",
    "cross",
    "circlePlus",
    "circle",
    "baseDash",
    "ERone",
    "ERmandOne",
    "ERmany",
    "ERoneToMany",
    "ERzeroToOne",
    "ERzeroToMany",
    "doubleBlock"]

origin = (0,0)
for shape in line_shapes:
    item_1 = drawpyo.diagram.BasicObject(page=page, value="line_shapes")
    item_1.position = origin
    item_2 = drawpyo.diagram.BasicObject(page=page, value=shape)
    item_2.position = (origin[0]+100, origin[1]+100)
    
    link = drawpyo.diagram.BasicEdge(page=page, source=item_1, target=item_2, line_shape=shape)
    
    origin = (origin[0], origin[1]+200)

origin = (300, 0)
for typ in line_types:
    item_1 = drawpyo.diagram.BasicObject(page=page, value="line_types")
    item_1.position = origin
    item_2 = drawpyo.diagram.BasicObject(page=page, value=typ)
    item_2.position = (origin[0]+100, origin[1]+100)
    
    link = drawpyo.diagram.BasicEdge(page=page, source=item_1, target=item_2, line_type=typ)
    
    origin = (origin[0], origin[1]+200)
    

origin = (600, 0)
for style in line_styles:
    item_1 = drawpyo.diagram.BasicObject(page=page, value="line_styles")
    item_1.position = origin
    item_2 = drawpyo.diagram.BasicObject(page=page, value=style)
    item_2.position = (origin[0]+100, origin[1]+100)
    
    link = drawpyo.diagram.BasicEdge(page=page, source=item_1, target=item_2, line_style=style)
    
    origin = (origin[0], origin[1]+200)
    

origin = (900, 0)
for end in line_ends:
    item_1 = drawpyo.diagram.BasicObject(page=page, value="line_ends")
    item_1.position = origin
    item_2 = drawpyo.diagram.BasicObject(page=page, value=end)
    item_2.position = (origin[0]+100, origin[1]+100)
    
    link = drawpyo.diagram.BasicEdge(page=page, source=item_1, target=item_2, line_end_target=end, line_end_source=end)
    
    origin = (origin[0], origin[1]+200)
file.write()
