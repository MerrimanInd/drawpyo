import os
import drawpyo
from drawpyo.file import File
from drawpyo.page import Page
from drawpyo.diagram_types.legend import Legend
from drawpyo.diagram.text_format import TextFormat
from drawpyo.utils.standard_colors import StandardColor
from drawpyo.utils.color_scheme import ColorScheme

# Chart title and legend color mapping
chart_title = "Coffee Legend"

medium_roast_scheme = ColorScheme(
    fill_color="#494239",
    stroke_color="#3B322E",
    font_color=StandardColor.WHITE,
)

mapping = {
    "Light Roast": "#7A6F59",
    "Medium Roast": medium_roast_scheme,
    "Dark Roast": "#2E2826",
}

# Create .drawio file at output path
output_path = os.path.join(
    os.path.expanduser("~"), "Test Drawpyo Charts", "Coffee Legend.drawio"
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

label_format = TextFormat(
    fontColor=StandardColor.GRAY5,
    fontSize=12,
    align="left",
    verticalAlign="bottom",
)

# Create the legend and add it to the page
legend = Legend(
    mapping=mapping,
    title="Roast Levels",
    position=(50, 50),
    title_text_format=title_format,
    label_text_format=label_format,
    background_color="#f2d0c9",
)

legend.add_to_page(page)

# Add the page to the file and save it
file.add_page(page)
file.write()
