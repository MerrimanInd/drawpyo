import os
import drawpyo
from drawpyo.file import File
from drawpyo.page import Page
from drawpyo.diagram_types.pie_chart import PieChart
from drawpyo.diagram.text_format import TextFormat
from drawpyo.utils.standard_colors import StandardColor
from drawpyo.utils.color_scheme import ColorScheme

# Chart title and data
chart_title = "Coffee Orders"
coffee_orders = {
    "Americano": 64,
    "Espresso": 21,
    "Latte": 15,
}

# Create .drawio file at output path
output_path = os.path.join(
    os.path.expanduser("~"), "Test Drawpyo Charts", "Coffee Orders Chart.drawio"
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

# Style slice appearance
color_scheme_a = ColorScheme(
    fill_color="#403025",
    stroke_color="#403025",
    font_color=StandardColor.GRAY1,
)
color_scheme_b = ColorScheme(
    fill_color="#16100B",
    stroke_color="#16100B",
    font_color=StandardColor.GRAY3,
)
color_scheme_c = ColorScheme(
    fill_color="#A98A72",
    stroke_color="#A98A72",
    font_color=StandardColor.GRAY7,
)
slice_colors = [color_scheme_a, color_scheme_b, color_scheme_c]


# Create custom label formatter
def label_formatter(key, value, total):
    return f"{key.upper()} {value/total*100:.1f}%"


# Create the chart and add it to the page
chart = PieChart(
    coffee_orders,
    position=(100, 0),
    size=350,
    slice_colors=slice_colors,
    title=chart_title,
    title_text_format=title_format,
    label_formatter=label_formatter,
    background_color="#DBC5AF",
)

chart.add_to_page(page)

# Add the page to the file and save it
file.add_page(page)
file.write()
