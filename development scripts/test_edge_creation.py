import drawpyo

file = drawpyo.File()
file.file_path = r"C:\drawpyo\Test Draw.io Charts"
file.file_name = "Test Generated Edges.drawio"
page = drawpyo.Page(file=file)

waypoints = [None, "straight", "orthogonal", "vertical", "horizontal", "isometric", "isometric_vertical", "curved", "entity_relation"]

connections = [None, "line", "link", "arrow", "simple_arrow"]

patterns = [None, "solid", "dashed_small", "dashed_medium", "dashed_large", "dotted_small", "dotted_medium", "dotted_large"]

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

spacing = 200

origin = (0,0)
for waypoint in waypoints:
    item_1 = drawpyo.diagram.BasicObject(page=page, value="wapyoints")
    item_1.position = origin
    item_2 = drawpyo.diagram.BasicObject(page=page, value=waypoint)
    item_2.position = (origin[0]+spacing, origin[1]+spacing)

    link = drawpyo.diagram.BasicEdge(page=page, source=item_1, target=item_2, waypoints=waypoint)

    origin = (origin[0], origin[1]+spacing*2)

origin = (spacing*3, 0)
for connection in connections:
    item_1 = drawpyo.diagram.BasicObject(page=page, value="connections")
    item_1.position = origin
    item_2 = drawpyo.diagram.BasicObject(page=page, value=connection)
    item_2.position = (origin[0]+spacing, origin[1]+spacing)

    link = drawpyo.diagram.BasicEdge(page=page, source=item_1, target=item_2, connection=connection)

    origin = (origin[0], origin[1]+spacing*2)


origin = (spacing*6, 0)
for pattern in patterns:
    item_1 = drawpyo.diagram.BasicObject(page=page, value="patterns")
    item_1.position = origin
    item_2 = drawpyo.diagram.BasicObject(page=page, value=pattern)
    item_2.position = (origin[0]+spacing, origin[1]+spacing)

    link = drawpyo.diagram.BasicEdge(page=page, source=item_1, target=item_2, pattern=pattern)

    origin = (origin[0], origin[1]+spacing*2)


origin = (spacing*9, 0)
for end in line_ends:
    item_1 = drawpyo.diagram.BasicObject(page=page, value="line_ends")
    item_1.position = origin
    item_2 = drawpyo.diagram.BasicObject(page=page, value=end)
    item_2.position = (origin[0]+spacing, origin[1]+spacing)

    link = drawpyo.diagram.BasicEdge(page=page, source=item_1, target=item_2, line_end_target=end, line_end_source=end)

    origin = (origin[0], origin[1]+spacing*2)
file.write()
