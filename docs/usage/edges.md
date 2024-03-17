# Edges

Edges are the lines and arrows that connect objects in Draw.io. There's quite a bit of variabiability in how they're created and styled so there's a bit more complexity than with objects.

## Creating a basic edge

Like objects, there's a BasicEdge object that can be easily created:

```python
link = drawpyo.diagram.BasicEdge(
    page=page,
    source=item_1,
    target=item_2,
    )
```

## Edge Geometry

Besides the source and target, the edge geometry can be very finely tuned. There are eight parameters that control where and how the edge meets the source and target objects:

| Parameter | Definition                                                                 |
| --------- | -------------------------------------------------------------------------- |
| `entryX`  | From where along the X axis on the source object the edge originates (0-1) |
| `entryY`  | From where along the Y axis on the source object the edge originates (0-1) |
| `entryDx` | Applies an offset in pixels to the X axis entry point                      |
| `entryDy` | Applies an offset in pixels to the Y axis entry point                      |
| `exitX`   | From where along the X axis on the target object the edge originates (0-1) |
| `exitY`   | From where along the Y axis on the target object the edge originates (0-1) |
| `exitDx`  | Applies an offset in pixels to the X axis exit point                       |
| `exitDy`  | Applies an offset in pixels to the Y axis exit point                       |

If these parameters are set to `None` then the Draw.io rendering engine will place the origination and direction of the edge wherever makes the most sense based on the layout of the objects. This is the same as the behavior in the app when an edge is dragged to the center of a shape (highlighting the whole object green) instead of to a specific node on the border (and seeing just that node highlighted in green).

Other attributes for controlling the general shape of the object are:

| Parameter   | Definition                                                                                                   |
| ----------- | ------------------------------------------------------------------------------------------------------------ |
| `rounded`   | Sets whether the corners of a line are set to sharp or rounded off (0-1)                                     |
| `jettySize` | Defines the length of the straight line coming out of or into an object before the edge makes its first turn |

## Styling edges

Just about every edge styling option from the Draw.io app is implemented in Drawpyo. It's easiest to just play with all of the different line styling options in Draw.io to understand how they render but the major options are listed here.

### Waypoints

The `waypoint` parameter controls how the line is routed from the source to the target. For example, a straight line is just point to point. A curved line tries to maintain gentle curves and perpendicularity to the source and target objects. Options are:

| Parameter            | Rendered |
| -------------------- | -------- |
| `straight`           |          |
| `orthogonal`         |          |
| `vertical`           |          |
| `horizontal`         |          |
| `isometric`          |          |
| `isometric_vertical` |          |
| `curved`             |          |
| `entity_relation`    |          |

### Connections

The `connection` parameter is abstractly named but it controls what type of edge this is. Most edges are lines but other types are available.

| Parameter      | Rendered |
| -------------- | -------- |
| `line`         |          |
| `link`         |          |
| `arrow`        |          |
| `simple_arrow` |          |

### Patterns

The `pattern` parameter controls how the line stroke is rendered. Options are:

| Parameter       | Rendered |
| --------------- | -------- |
| `solid`         |          |
| `dashed_small`  |          |
| `dashed_medium` |          |
| `dashed_large`  |          |
| `dotted_small`  |          |
| `dotted_medium` |          |
| `dotted_large`  |          |

### Line Ends

The `line_end_target` and `line_end_source` parameter sets whatever is rendered where the edge meets the objects. There are secondary boolean parameters for the fill of the ends (`endFill_target` and `endFill_source`) but not all ends can be filled.

| Parameter      | Rendered Unfilled | Rendered Filled |
| -------------- | ----------------- | --------------- |
| `classic`      |                   |                 |
| `classicThin`  |                   |                 |
| `open`         |                   | na              |
| `openThin`     |                   | na              |
| `openAsync`    |                   | na              |
| `block`        |                   |                 |
| `blockThin`    |                   |                 |
| `async`        |                   |                 |
| `oval`         |                   |                 |
| `diamond`      |                   |                 |
| `diamondThin`  |                   |                 |
| `dash`         |                   | na              |
| `halfCircle`   |                   | na              |
| `cross`        |                   | na              |
| `circlePlus`   |                   | na              |
| `circle`       |                   | na              |
| `baseDash`     |                   | na              |
| `ERone`        |                   | na              |
| `ERmandOne`    |                   | na              |
| `ERmany`       |                   | na              |
| `ERoneToMany`  |                   | na              |
| `ERzeroToOne`  |                   | na              |
| `ERzeroToMany` |                   | na              |
| `doubleBlock`  |                   |                 |
