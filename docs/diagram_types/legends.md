# Legendy

A legend displays a color-to-label mapping, typically used to explain color coding in diagrams. The `Legend` class renders a vertical list of colored boxes with corresponding text labels.

## Create a simple Legend

Define your color mapping and initialize the legend:
```python
# Define the legend mapping
status_colors = {
    "Active": "#4CAF50",
    "Pending": "#FFC107",
    "Inactive": "#9E9E9E",
}

# Create the legend
legend = Legend(
    status_colors,
    title="Status",
    position=(50, 50),
)
```

The `Legend` constructor accepts keyword arguments to customize appearance and layout:

| Parameter             | Effect                                                  | Default        |
| --------------------- | ------------------------------------------------------- | -------------- |
| `position`            | Top-left position as `(x, y)`                           | `(0, 0)`       |
| `title`               | Optional title above the legend                         | `None`         |
| `title_text_format`   | Formatting for the title                                | `TextFormat()` |
| `label_text_format`   | Formatting for labels                                   | `TextFormat()` |
| `glass`               | Apply glass effect to color boxes                       | `False`        |
| `rounded`             | Apply rounded corners to color boxes                    | `False`        |
| `background_color`    | Optional background fill color                          | `None`         |

### Color Values

Colors can be strings (hex codes), `StandardColor` enums, or `ColorScheme` objects.

## Methods

**`update_mapping(mapping)`** — Replace the legend's color mapping and rebuild.

**`move(new_position)`** — Reposition the entire legend to `(x, y)`.

**`add_to_page(page)`** — Add all legend objects to a `Page`.

## Example with Styling
```python
legend = Legend(
    status_colors,
    position=(400, 100),
    title="Order Status",
    title_text_format=title_format,
    label_text_format=label_format,
    glass=True,
    rounded=True,
    background_color="#F5F5F5",
)

legend.add_to_page(page)
```

The legend automatically sizes itself based on label lengths and applies consistent spacing between rows.

![example\_pie\_chart](../img/pie_chart/coffee_orders_chart.png)