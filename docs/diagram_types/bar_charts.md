# Bar Charts

A bar chart is a visual graph that uses rectangular bars to compare the size of different categories. The `BarChart` module allows you to generate visualizations from dictionaries mapping strings to numerical values.

## Create a simple Bar Chart

Let's first prepare the data and label formatting before initializing a simple chart using it.

```python
# Define the chart title
chart_title = "Coffee Grinder Prices"

# Define the chart data
coffee_grinder_prices = {
    "Blade Grinder": 32,
    "Burr Grinder":  79,
}

# Custom formatters can override default label values
def custom_label_formatter(_category: str, value: int) -> str:
    return f"{value} $"

# Create the chart object
chart = BarChart(
    coffee_grinder_prices,
    title=chart_title,
    inside_label_formatter=custom_label_formatter,
)
```

There are a number of configuration parameters available to fine-tune the layout and appearance of the `BarChart`, which can be passed as keyword arguments.

| Parameter                | Effect                                                  | Default              |
| ------------------------ | ------------------------------------------------------- | -------------------- |
| `position`               | Top-left chart origin as `(x, y)`                       | `(0, 0)`             |
| `show_axis`              | Toggles axis and tick display                           | `False`              |
| `bar_width`              | Width of each bar                                       | `40`                 |
| `bar_spacing`            | Horizontal spacing between bars                         | `20`                 |
| `max_bar_height`         | Height of the tallest bar                               | `200`                |
| `bar_colors`             | Single color or list of colors applied to bars          | `"#66ccff"`          |
| `bar_fill_color`         | Overrides fill color for all bars                       | `None`               |
| `bar_stroke_color`       | Stroke color for bar outlines                           | `"#000000"`          |
| `title`                  | Optional chart title                                    | `None`               |
| `title_text_format`      | Text formatting for the title                           | `TextFormat()`       |
| `base_text_format`       | Formatting for labels below bars                        | `TextFormat()`       |
| `inside_text_format`     | Formatting for labels rendered inside bars              | `TextFormat()`       |
| `background_color`       | Optional background rectangle behind the chart          | `None`               |
| `axis_tick_count`        | Number of tick intervals on the chart axis              | `5`                  |
| `axis_text_format`       | Formatting for axis tick labels                         | `TextFormat()`       |
| `base_label_formatter`   | Callable that formats the category label below each bar | `lambda l,v: l`      |
| `inside_label_formatter` | Callable that formats values printed inside each bar    | `lambda l,v: str(v)` |
| `bar_object`             | Optional template `Object` used to generate each bar    | `None`               |

> **Note:** When you provide a bar template object, every bar in the chart will inherit its styling (such as rounded corners, glass or shadow). However, properties like the bar’s value, color and size are always controlled by the `BarChart` itself and will override the template’s values.

With a few visual adjustments, the resulting chart renders as:

![coffee\_grinders\_chart](../img/bar_chart/coffee_grinders_chart.png)