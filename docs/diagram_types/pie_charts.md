# Pie Charts

A pie chart is a circular visualization that divides a whole into proportional slices. The `PieChart` module provides a configurable way to render labeled pie slices from a dictionary mapping strings to numerical values.

## Create a simple Pie Chart

Start by preparing the data and any optional formatting before initializing a chart.

```python
# Define the chart title
chart_title = "Coffee Orders"

# Define the pie chart data
coffee_orders = {
    "Americano": 64,
    "Espresso": 21,
    "Latte": 15,
}

# Custom formatter to override slice labels
def label_formatter(category: str, value: float, total: float) -> str:
    return f"{category}: {value/total*100:.1f}%"

# Create the chart object
chart = PieChart(
    coffee_orders,
    title=chart_title,
    size=250,
    label_formatter=label_formatter,
)
```

Just like with the Bar Chart module, the `PieChart` constructor accepts a variety of keyword arguments to adjust appearance, layout, and textual formatting.

| Parameter           | Effect                                                            | Default                   |
| ------------------- | ----------------------------------------------------------------- | ------------------------- |
| `position`          | Top-left position where the chart is placed as `(x, y)`           | `(0, 0)`                  |
| `size`              | Diameter of the pie                                               | `200`                     |
| `slice_colors`      | List of colors or ColorSchemes for slice fills                    | `["#66ccff"]`             |
| `title`             | Optional chart title                                              | `None`                    |
| `title_text_format` | Formatting for the title (alignment, font, size, etc.)            | `TextFormat()`            |
| `label_text_format` | Formatting applied to slice labels                                | `TextFormat()`            |
| `background_color`  | Optional background rectangle behind the pie                      | `None`                    |
| `label_formatter`   | Callable formatting each slice’s label as `(label, value, total)` | `default_label_formatter` |

### Label Formatting

Each slice automatically receives a label positioned along its radius. The default format produces percentage values:

```python
"{label}: {percentage:.1f}%"
```

You may fully override this via the `label_formatter` callback.

### Slice Colors

The list passed to `slice_colors` is cycled if fewer entries are provided than slices.
Colors may be strings, `StandardColor`, or `ColorScheme` objects.

## Example Chart

With additional formatting and color schemes, you can create a custom-styled chart:

```python
chart = PieChart(
    coffee_orders,
    position=(100, 0),
    size=350,
    slice_colors=slice_colors,  # list of custom ColorScheme objects
    title=chart_title,
    title_text_format=title_format,
    label_formatter=label_formatter,
    background_color="#DBC5AF",
)
```

After optional customization, add the chart to a `Page` and save the `.drawio` file.

![example\_legend](../img/legend/legend.png)