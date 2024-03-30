import drawpyo
from os import path

# Create file and start a flowchart
file = drawpyo.File()
file.file_path = path.join(path.expanduser("~"), "Test Drawpyo Charts")
file.file_name = "How to Make Coffee.drawio"
page = drawpyo.Page(file=file)


# Set up some variables and create template objects
main_column_pos = page.width/2
left_column_pos = main_column_pos-200
right_column_pos = main_column_pos+200
row_h = 120
row_margin = 60
row_n = 0

# Note that the template objects aren't placed on a page so they aren't printed
process = drawpyo.diagram.object_from_library(
    library="flowchart",
    obj_name="process",
    width=140,
    height=70,
)
data = drawpyo.diagram.object_from_library(
    library="flowchart",
    obj_name="data",
    width=140,
    height=70,
)
decision = drawpyo.diagram.object_from_library(
    library="flowchart",
    obj_name="decision",
    width = 120,
    height = 70,
)

start = drawpyo.diagram.object_from_library(
    library="flowchart", obj_name="start_1", value="Start", page=page
)
start.center_position = (main_column_pos, row_margin+row_h*row_n)

# Recipe
recipe = drawpyo.diagram.object_from_library(
    library="flowchart", obj_name="document", value="Brewing recipe", page=page
)
recipe.position = (20, row_margin+row_h*row_n)

# Create the kettle and turn it on
row_n = row_n+1
kettle = drawpyo.diagram.object_from_library(
    library="flowchart",
    obj_name="preparation",
    value="Turn on kettle",
    page=page,
    width = 150,
    height = 80,
    verticalLabelPosition = "middle", # This sets the label object to the middle of the object
    verticalAlign = "middle", # This sets the text to align to the middle within the label object
)

kettle.center_position = (main_column_pos, row_margin+row_h*row_n)
# Pull in a data block from the recipe to get the water temperature
temp = drawpyo.diagram.Object(
    template_object=data, value="Water temperature", page=page
)
temp.center_position = (left_column_pos, row_margin+row_h*row_n)

# Retrieve the beans
row_n = row_n+1
beans = drawpyo.diagram.object_from_library(
    library="flowchart",
    obj_name="stored_data",
    value="Retrieve beans",
    page=page,
    width=140,
    height=70,
)
beans.center_position = (main_column_pos, row_margin+row_h*row_n)

# Weigh the beans
row_n = row_n+1
weigh = drawpyo.diagram.Object(
    template_object=process,
    value="Weigh beans",
    page=page,
)
weigh.center_position = (main_column_pos, row_margin+row_h*row_n)

bean_mass = drawpyo.diagram.Object(
    template_object=data, value="Mass of beans (g)", page=page
)
bean_mass.center_position = (left_column_pos, row_margin+row_h*row_n)

# Grind the beans
row_n = row_n+1
grind = drawpyo.diagram.Object(
    template_object=process,
    value="Grind beans",
    page=page,
)
grind.center_position = (main_column_pos, row_margin+row_h*row_n)
grind_size = drawpyo.diagram.Object(
    template_object=data, value="Grind size", page=page
)
grind_size.center_position = (left_column_pos, row_margin+row_h*row_n)

# Setup the brewer
row_n = row_n+1
setup = drawpyo.diagram.Object(
    template_object=process,
    value="Setup cone and filter on mug",
    page=page,
)
setup.center_position = (main_column_pos, row_margin+row_h*row_n)

# Preheat
row_n = row_n+1
preheat_opt = drawpyo.diagram.Object(
    template_object = decision,
    value = "Preheat cone?",
    page=page
)
preheat_opt.center_position = (main_column_pos, row_margin+row_h*row_n)

row_n = row_n+1
preheat = drawpyo.diagram.Object(
    template_object=process,
    value="Pour hot water through filter",
    page=page,
)
preheat.center_position = (right_column_pos, row_margin+row_h*row_n)

add_coffee = drawpyo.diagram.Object(
    template_object=process,
    value="Add coffee to filter",
    page=page,
)
add_coffee.center_position = (main_column_pos, row_margin+row_h*row_n)

# Bloom
row_n = row_n+1
bloom_opt = drawpyo.diagram.Object(
    template_object = decision,
    value = "Bloom?",
    page=page
)
bloom_opt.center_position = (main_column_pos, row_margin+row_h*row_n)

row_n = row_n+0.5
bloom = drawpyo.diagram.Object(
    template_object=process,
    value="Pour ~2x coffee weight in water",
    page=page,
)
bloom.center_position = (right_column_pos, row_margin+row_h*row_n)
row_n = row_n+0.5

# Start Pouring
pour_quant = drawpyo.diagram.Object(
    template_object=data, value="Pour quantity/count", page=page
)
pour_quant.center_position = (left_column_pos, row_margin+row_h*row_n)

pour = drawpyo.diagram.object_from_library(
    library="flowchart",
    obj_name="manual_input",
    value="Add pour quantity of hot water",
    verticalAlign="bottom",
)
pour.center_position = (main_column_pos, row_margin+row_h*row_n)

# Write the file
file.write()
