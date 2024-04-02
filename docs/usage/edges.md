# Edges

Edges are the lines and arrows that connect objects in Draw.io. There's quite a bit of variabiability in how they're created and styled so there's a bit more complexity than with objects.

## Creating a basic edge

Like objects, there's a Edge object that can be easily created:

```python
link = drawpyo.diagram.Edge(
    page=page,
    source=item_1,
    target=item_2,
    )
```

## Edge Labels

The value of an edge is the label that appears on it. It can be set using the `label` value.

The position of the label can be fine tuned with two parameters:

| Parameter        | Effect                                                                                                                                                                     |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `label_position` | The position along the edge's axis where the label appears. This is float value between -1 and 1. 0 is neutral/in the center, -1 is at the source, and 1 is at the target. |
| `label_offset`   | The offset in pixels perpendicular to the axis of the edge.                                                                                                                |

#### Label Positions Rendered

![label_positions.png](../img/edge_styles/label_positions.png)    

## Edge Geometry

Besides the source and target, the edge geometry can be very finely tuned. There are eight parameters that control where and how the edge meets the source and target objects:

| Parameter                | Definition                                                                        |
| ------------------------ | --------------------------------------------------------------------------------- |
| `entryX`                 | From where along the X axis on the source object the edge originates (0-1)        |
| `entryY`                 | From where along the Y axis on the source object the edge originates (0-1)        |
| `entryDx`                | Applies an offset in pixels to the X axis entry point                             |
| `entryDy`                | Applies an offset in pixels to the Y axis entry point                             |
| `exitX`                  | From where along the X axis on the target object the edge originates (0-1)        |
| `exitY`                  | From where along the Y axis on the target object the edge originates (0-1)        |
| `exitDx`                 | Applies an offset in pixels to the X axis exit point                              |
| `exitDy`                 | Applies an offset in pixels to the Y axis exit point                              |
| `targetPerimeterSpacing` | The negative or positive spacing between the target and end of the edge in points |
| `sourcePerimeterSpacing` | The negative or positive spacing between the source and end of the edge in points |

If these parameters are set to `None` then the Draw.io rendering engine will place the origination and direction of the edge wherever makes the most sense based on the layout of the objects. This is the same as the behavior in the app when an edge is dragged to the center of a shape (highlighting the whole object green) instead of to a specific node on the border (and seeing just that node highlighted in green).

They can also be set to X and Y coordinates designating where on the source and target objects the edge will meet it. The rest of the routing will be handled automatically.

![coords_legend.png](../img/edge_styles/coords_legend.png)

Some examples of different coordinate settings:

![coords_examples.png](../img/edge_styles/coords_examples.png)

Other attributes for controlling the general shape of the object are:

| Parameter   | Definition                                                                                                   |
| ----------- | ------------------------------------------------------------------------------------------------------------ |
| `jettySize` | Defines the length of the straight line coming out of or into an object before the edge makes its first turn |

## Points

You can also add points to Edges to further fine tune their routing. This isn't always necessary, usually setting the entry/exit parameters handles the auto routing correctly. However this is an option, using the `Edge.add_point()` and `Edge.add_point_pos()` functions. The edge will then route through those points but auto layout otherwise.

## Styling edges

Just about every edge styling option from the Draw.io app is implemented in Drawpyo. It's easiest to just play with all of the different line styling options in Draw.io to understand how they render but the major options are listed here.

### Text Styling

The styling within an an edge label is contained inside of a `TextFormat` object. All styling parameters can be accessed at the attribute `Edge.text_format`, which contains a `TextFormat` object.

For more information about styling text, see [Formatting Text](/drawpyo/usage/text_format) for more information.

### Color and Shading

Edge coloring can be set with a stroke and fill color, though only the stroke applies to a simple edge.

| Parameter     | Effect                                                                                             |
| ------------- | -------------------------------------------------------------------------------------------------- |
| `opacity`     | The opacity of the edge (0-100)                                                                    |
| `strokeColor` | The color of the edge or the stroke around the edge shape ('default', 'none', or a hex color code) |
| `fillColor`   | The fill color of the edge shape ('default', 'none', or a hex color code)                          |

### Effects

Draw.io has four effects that can be set on an edge. They're all boolean valuable that can be enabled.

| Paramater        | Rendered                                                                    |
| ---------------- | --------------------------------------------------------------------------- |
| default (None)   | ![effects_default](../img/edge_styles/effects_default.png)               |
| `rounded`        | ![effects_rounded](../img/edge_styles/effects_rounded.png)               |
| `shadow`         | ![effects_shadow](../img/edge_styles/effects_shadow.png)                 |
| `sketch`         | ![effects_sketch](../img/edge_styles/effects_sketch.png)                 |
| `flowAnimation`* | ![effects_flow_animation](../img/edge_styles/effects_flow_animation.png) |

> *(this animates in Draw.io)

### Jumps

By default, when an edge crosses another edge they'll just be rendered as a cross. You can also enable line jumps; the top edge will 'jump' over the bottom edge. There are different styles of line jumps and they can have variable sizes as well.

| Parameter   | Effect                                                               |
| ----------- | -------------------------------------------------------------------- |
| `jumpStyle` | The style of the line jump. Can be 'arc', 'gap', 'sharp', or 'line'. |
| `jumpSize`  | The size of the rendered line jumps in points.                       |

The different rendered jump styles are:

| Parameter      | Rendered                                                          |
| -------------- | ----------------------------------------------------------------- |
| default (None) | ![line_jump_default](../img/edge_styles/line_jump_default.png) |
| `arc`          | ![line_jump_arc](../img/edge_styles/line_jump_arc.png)         |
| `gap`          | ![line_jump_gap](../img/edge_styles/line_jump_gap.png)         |
| `sharp`        | ![line_jump_sharp](../img/edge_styles/line_jump_sharp.png)     |
| `line`         | ![line_jump_line](../img/edge_styles/line_jump_line.png)       |

### Waypoints

The `waypoint` parameter controls how the line is routed from the source to the target. For example, a straight line is just point to point. A curved line tries to maintain gentle curves and perpendicularity to the source and target objects. Options are:

| Parameter            | Rendered                                                                                |
| -------------------- | --------------------------------------------------------------------------------------- |
| default (None)       | ![waypoints_default](../img/edge_styles/waypoints_default.png)                       |
| `straight`           | ![waypoints_straight](../img/edge_styles/waypoints_straight.png)                     |
| `orthogonal`         | ![waypoints_orthogonal](../img/edge_styles/waypoints_orthogonal.png)                 |
| `vertical`           | ![waypoints_vertical](../img/edge_styles/waypoints_vertical.png)                     |
| `horizontal`         | ![waypoints_horizontal](../img/edge_styles/waypoints_horizontal.png)                 |
| `isometric`          | ![waypoints_isometric](../img/edge_styles/waypoints_isometric.png)                   |
| `isometric_vertical` | ![waypoints_isometric_vertical](../img/edge_styles/waypoints_isometric_vertical.png) |
| `curved`             | ![waypoints_curved](../img/edge_styles/waypoints_curved.png)                         |
| `entity_relation`    | ![waypoints_entity_relation](../img/edge_styles/waypoints_entity_relation.png)       |

### Connections

The `connection` parameter is abstractly named but it controls what type of edge this is. Most edges are lines but other types are available.

| Parameter      | Rendered                                                                        |
| -------------- | ------------------------------------------------------------------------------- |
| default (None) | ![connections_default](../img/edge_styles/connections_default.png)           |
| `line`         | ![connections_line](../img/edge_styles/connections_line.png)                 |
| `link`         | ![connections_link](../img/edge_styles/connections_link.png)                 |
| `arrow`        | ![connections_arrow](../img/edge_styles/connections_arrow.png)               |
| `simple_arrow` | ![connections_simple_arrow](../img/edge_styles/connections_simple_arrow.png) |

### Patterns

The `pattern` parameter controls how the line stroke is rendered. Options are:

| Parameter       | Rendered                                                                    |
| --------------- | --------------------------------------------------------------------------- |
| default (None)  | ![patterns_default](../img/edge_styles/patterns_default.png)             |
| `solid`         | ![patterns_solid](../img/edge_styles/patterns_solid.png)                 |
| `dashed_small`  | ![patterns_dashed_small](../img/edge_styles/patterns_dashed_small.png)   |
| `dashed_medium` | ![patterns_dashed_medium](../img/edge_styles/patterns_dashed_medium.png) |
| `dashed_large`  | ![patterns_dashed_large](../img/edge_styles/patterns_dashed_large.png)   |
| `dotted_small`  | ![patterns_dotted_small](../img/edge_styles/patterns_dotted_small.png)   |
| `dotted_medium` | ![patterns_dotted_medium](../img/edge_styles/patterns_dotted_medium.png) |
| `dotted_large`  | ![patterns_dotted_large](../img/edge_styles/patterns_dotted_large.png)   |

### Line Ends

The `line_end_target` and `line_end_source` parameter sets whatever is rendered where the edge meets the objects. There are secondary boolean parameters for the fill of the ends (`endFill_target` and `endFill_source`) but not all ends can be filled.

The line end size can also be adjusted with `endSize` and `startSize` parameters, both set in points.

| Parameter      | Rendered Unfilled                                                         | Rendered Filled                                                                       |
| -------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| default (None) | ![line_end_default](../img/edge_styles/line_end_default.png)           | *na*                                                                                  |
| `classic`      | ![line_end_classic](../img/edge_styles/line_end_classic.png)           | ![line_end_classic_filled](../img/edge_styles/line_end_classic_filled.png)         |
| `classicThin`  | ![line_end_classicThin](../img/edge_styles/line_end_classicThin.png)   | ![line_end_classicThin_filled](../img/edge_styles/line_end_classicThin_filled.png) |
| `open`         | ![line_end_open](../img/edge_styles/line_end_open.png)                 | *na*                                                                                  |
| `openThin`     | ![line_end_openThin](../img/edge_styles/line_end_openThin.png)         | *na*                                                                                  |
| `openAsync`    | ![line_end_openAsync](../img/edge_styles/line_end_openAsync.png)       | *na*                                                                                  |
| `block`        | ![line_end_block](../img/edge_styles/line_end_block.png)               | ![line_end_block_filled](../img/edge_styles/line_end_block_filled.png)             |
| `blockThin`    | ![line_end_blockThin](../img/edge_styles/line_end_blockThin.png)       | ![line_end_blockThin_filled](../img/edge_styles/line_end_blockThin_filled.png)     |
| `async`        | ![line_end_async](../img/edge_styles/line_end_async.png)               | ![line_end_async_filled](../img/edge_styles/line_end_async_filled.png)             |
| `oval`         | ![line_end_oval](../img/edge_styles/line_end_oval.png)                 | ![line_end_oval_filled](../img/edge_styles/line_end_oval_filled.png)               |
| `diamond`      | ![line_end_diamond](../img/edge_styles/line_end_diamond.png)           | ![line_end_diamond_filled](../img/edge_styles/line_end_diamond_filled.png)         |
| `diamondThin`  | ![line_end_diamondThin](../img/edge_styles/line_end_diamondThin.png)   | ![line_end_diamondThin_filled](../img/edge_styles/line_end_diamondThin_filled.png) |
| `dash`         | ![line_end_dash](../img/edge_styles/line_end_dash.png)                 | *na*                                                                                  |
| `halfCircle`   | ![line_end_halfCircle](../img/edge_styles/line_end_halfCircle.png)     | *na*                                                                                  |
| `cross`        | ![line_end_cross](../img/edge_styles/line_end_cross.png)               | *na*                                                                                  |
| `circlePlus`   | ![line_end_circlePlus](../img/edge_styles/line_end_circlePlus.png)     | *na*                                                                                  |
| `circle`       | ![line_end_circle](../img/edge_styles/line_end_circle.png)             | *na*                                                                                  |
| `baseDash`     | ![line_end_baseDash](../img/edge_styles/line_end_baseDash.png)         | *na*                                                                                  |
| `ERone`        | ![line_end_ERone](../img/edge_styles/line_end_ERone.png)               | *na*                                                                                  |
| `ERmandOne`    | ![line_end_ERmandOne](../img/edge_styles/line_end_ERmandOne.png)       | *na*                                                                                  |
| `ERmany`       | ![line_end_ERmany](../img/edge_styles/line_end_ERmany.png)             | *na*                                                                                  |
| `ERoneToMany`  | ![line_end_ERoneToMany](../img/edge_styles/line_end_ERoneToMany.png)   | *na*                                                                                  |
| `ERzeroToOne`  | ![line_end_ERzeroToOne](../img/edge_styles/line_end_ERzeroToOne.png)   | *na*                                                                                  |
| `ERzeroToMany` | ![line_end_ERzeroToMany](../img/edge_styles/line_end_ERzeroToMany.png) | *na*                                                                                  |
| `doubleBlock`  | ![line_end_doubleBlock](../img/edge_styles/line_end_doubleBlock.png)   | ![line_end_doubleBlock_filled](../img/edge_styles/line_end_doubleBlock_filled.png) |
