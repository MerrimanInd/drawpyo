import drawpyo
from os import path

file = drawpyo.File()
file.file_path = path.join(path.expanduser("~"), "Test Drawpyo Charts")
file.file_name = "Test Generated Edges.drawio"
page = drawpyo.Page(file=file)

waypoints = [
    None,
    "straight",
    "orthogonal",
    "vertical",
    "horizontal",
    "isometric",
    "isometric_vertical",
    "curved",
    "entity_relation",
]

connections = [None, "line", "link", "arrow", "simple_arrow"]

patterns = [
    None,
    "solid",
    "dashed_small",
    "dashed_medium",
    "dashed_large",
    "dotted_small",
    "dotted_medium",
    "dotted_large",
]

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
    "doubleBlock",
]

h_spacing = 150
v_spacing = 80
obj = drawpyo.diagram.Object(width=100, height=60)

origin = (10, 10)
for waypoint in waypoints:
    item_1 = drawpyo.diagram.Object(page=page, template_object=obj, value="wapyoints")
    item_1.position = origin
    item_2 = drawpyo.diagram.Object(page=page, template_object=obj, value=waypoint)
    item_2.position = (origin[0] + h_spacing, origin[1] + v_spacing)

    link = drawpyo.diagram.Edge(
        page=page, source=item_1, target=item_2, waypoints=waypoint
    )

    origin = (origin[0], origin[1] + v_spacing * 2)

origin = (h_spacing * 3, 0)
for connection in connections:
    item_1 = drawpyo.diagram.Object(page=page, template_object=obj, value="connections")
    item_1.position = origin
    item_2 = drawpyo.diagram.Object(page=page, template_object=obj, value=connection)
    item_2.position = (origin[0] + h_spacing, origin[1] + v_spacing)

    link = drawpyo.diagram.Edge(
        page=page, source=item_1, target=item_2, connection=connection
    )

    origin = (origin[0], origin[1] + v_spacing * 2)


origin = (h_spacing * 6, 0)
for pattern in patterns:
    item_1 = drawpyo.diagram.Object(page=page, template_object=obj, value="patterns")
    item_1.position = origin
    item_2 = drawpyo.diagram.Object(page=page, template_object=obj, value=pattern)
    item_2.position = (origin[0] + h_spacing, origin[1] + v_spacing)

    link = drawpyo.diagram.Edge(
        page=page, source=item_1, target=item_2, pattern=pattern
    )

    origin = (origin[0], origin[1] + v_spacing * 2)


origin = (h_spacing * 9, 0)
for end in line_ends:
    item_1 = drawpyo.diagram.Object(page=page, template_object=obj, value="line_ends")
    item_1.position = origin
    item_2 = drawpyo.diagram.Object(page=page, template_object=obj, value=end)
    item_2.position = (origin[0] + h_spacing, origin[1] + v_spacing)

    link = drawpyo.diagram.Edge(
        page=page,
        source=item_1,
        target=item_2,
        line_end_target=end,
        line_end_source=end,
        endSize=12,
        startSize=12,
    )

    origin = (origin[0], origin[1] + v_spacing * 2)

origin = (h_spacing * 12, 0)
for end in line_ends:
    item_1 = drawpyo.diagram.Object(page=page, template_object=obj, value="line_ends")
    item_1.position = origin
    item_2 = drawpyo.diagram.Object(page=page, template_object=obj, value=end)
    item_2.position = (origin[0] + h_spacing, origin[1] + v_spacing)

    link = drawpyo.diagram.Edge(
        page=page,
        source=item_1,
        target=item_2,
        line_end_target=end,
        line_end_source=end,
        endFill_target=True,
        endFill_source=True,
        endSize=12,
        startSize=12,
    )

    origin = (origin[0], origin[1] + v_spacing * 2)

file.write()
