import os
import drawpyo
from drawpyo.file import File
from drawpyo.page import Page
from drawpyo.diagram_types.bar_chart import BarChart
from drawpyo.diagram.text_format import TextFormat
from drawpyo.diagram.objects import Object
from drawpyo.utils.standard_colors import StandardColor

drawpyo.logger.setLevel("DEBUG")

# Chart title and data
chart_title = "Coffee Grinder Prices"
coffee_grinder_prices = {
    "Manual": 29,
    "Blade": 45,
    "Burr": 120,
}

# Create .drawio file at output path
output_path = os.path.join(
    os.path.expanduser("~"), "Test Drawpyo Charts", "coffee_grinder_chart.drawio"
)
file = File(output_path)

# Create a page
page = Page()

# Create TextFormat objects to style labels
title_format = TextFormat(
    fontColor=StandardColor.BLACK,
    fontSize=16,
    align="center",
    verticalAlign="bottom",
    bold=True,
)
base_text_format = TextFormat(
    fontColor=StandardColor.GRAY5, fontSize=14, align="center", verticalAlign="bottom"
)
inside_text_format = TextFormat(
    fontColor="#000000", fontSize=16, align="center", verticalAlign="bottom", bold=True
)

# Style bar appearance
bar_template = Object(rounded=True, glass=True)
bar_colors = ["#A4B86F", "#C47EA7", "#344E77"]
bar_stroke_color = "#A0A8AB"


# Create custom label formatter
def inside_formatter(_key, value):
    return f"{value} $"


# Create the chart and add it to the page
chart = BarChart(
    coffee_grinder_prices,
    show_axis=True,
    axis_tick_count=10,
    bar_template=bar_template,
    position=(100, 0),
    bar_width=60,
    bar_spacing=25,
    max_bar_height=250,
    bar_colors=bar_colors,
    title=chart_title,
    title_text_format=title_format,
    base_text_format=base_text_format,
    inside_label_formatter=inside_formatter,
    bar_stroke_color=bar_stroke_color,
    background_color=StandardColor.GRAY2,
)

chart.add_to_page(page)

# Add the page to the file and save it
file.add_page(page)
file.write()
