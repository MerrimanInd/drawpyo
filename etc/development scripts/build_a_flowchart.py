import drawpyo
from os import path

# Create file and start a flowchart
file = drawpyo.File()
file.file_path = path.join(path.expanduser("~"), "Test Drawpyo Charts")
file.file_name = "How to Make Coffee.drawio"
page = drawpyo.Page(file=file)

# Initial Setup
## Set up some variables and create template objects
main_column_pos = page.width / 2
left_column_pos = main_column_pos - 200
right_column_pos = main_column_pos + 200
row_h = 120
row_margin = 60
row_n = 0

### Note that the template objects aren't placed on a page so they aren't printed
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
    width=120,
    height=70,
)

# Create and place objects

start = drawpyo.diagram.object_from_library(
    library="flowchart", obj_name="start_1", value="Start", page=page
)
start.center_position = (main_column_pos, row_margin + row_h * row_n)

## Recipe
recipe = drawpyo.diagram.object_from_library(
    library="flowchart", obj_name="document", value="Brewing recipe", page=page
)
recipe.position = (20, row_margin + row_h * row_n)

## Create the kettle and turn it on
row_n = row_n + 1
kettle = drawpyo.diagram.object_from_library(
    library="flowchart",
    obj_name="preparation",
    value="Turn on kettle",
    page=page,
    width=150,
    height=80,
    verticalLabelPosition="middle",  # This sets the label object to the middle of the object
    verticalAlign="middle",  # This sets the text to align to the middle within the label object
)

kettle.center_position = (main_column_pos, row_margin + row_h * row_n)
## Pull in a data block from the recipe to get the water temperature
temp = drawpyo.diagram.Object(
    template_object=data, value="Water temperature", page=page
)
temp.center_position = (left_column_pos, row_margin + row_h * row_n)

## Retrieve the beans
row_n = row_n + 1
beans = drawpyo.diagram.object_from_library(
    library="flowchart",
    obj_name="stored_data",
    value="Retrieve beans",
    page=page,
    width=140,
    height=70,
)
beans.center_position = (main_column_pos, row_margin + row_h * row_n)

## Weigh the beans
row_n = row_n + 1
weigh = drawpyo.diagram.Object(
    template_object=process,
    value="Weigh beans",
    page=page,
)
weigh.center_position = (main_column_pos, row_margin + row_h * row_n)

bean_mass = drawpyo.diagram.Object(
    template_object=data, value="Mass of beans (g)", page=page
)
bean_mass.center_position = (left_column_pos, row_margin + row_h * row_n)

## Grind the beans
row_n = row_n + 1
grind = drawpyo.diagram.Object(
    template_object=process,
    value="Grind beans",
    page=page,
)
grind.center_position = (main_column_pos, row_margin + row_h * row_n)
grind_size = drawpyo.diagram.Object(
    template_object=data, value="Grind size", page=page
)
grind_size.center_position = (left_column_pos, row_margin + row_h * row_n)

## Setup the brewer
row_n = row_n + 1
setup = drawpyo.diagram.Object(
    template_object=process,
    value="Setup cone and filter on mug",
    page=page,
)
setup.center_position = (main_column_pos, row_margin + row_h * row_n)

## Preheat
row_n = row_n + 1
preheat_opt = drawpyo.diagram.Object(
    template_object=decision, value="Preheat cone?", page=page
)
preheat_opt.center_position = (main_column_pos, row_margin + row_h * row_n)

row_n = row_n + 1
preheat = drawpyo.diagram.Object(
    template_object=process,
    value="Pour hot water through filter",
    page=page,
)
preheat.center_position = (right_column_pos, row_margin + row_h * row_n)

add_coffee = drawpyo.diagram.Object(
    template_object=process,
    value="Add coffee to filter",
    page=page,
)
add_coffee.center_position = (main_column_pos, row_margin + row_h * row_n)

## Bloom
row_n = row_n + 1
bloom_opt = drawpyo.diagram.Object(
    template_object=decision, value="Bloom?", page=page
)
bloom_opt.center_position = (main_column_pos, row_margin + row_h * row_n)

row_n = row_n + 1
bloom = drawpyo.diagram.Object(
    template_object=process,
    value="Pour ~2x coffee weight in water",
    page=page,
)
bloom.center_position = (right_column_pos, row_margin + row_h * row_n)

## Start Pouring
pour_quant = drawpyo.diagram.Object(
    template_object=data, value="Pour quantity/count", page=page
)
pour_quant.center_position = (left_column_pos, row_margin + row_h * row_n)

pour = drawpyo.diagram.object_from_library(
    library="flowchart",
    obj_name="manual_input",
    value="Add pour quantity of hot water",
    verticalAlign="bottom",
    page=page,
)
pour.center_position = (main_column_pos, row_margin + row_h * row_n)

## Wait for pour time
row_n = row_n + 1
wait = drawpyo.diagram.object_from_library(
    library="flowchart",
    obj_name="delay",
    value="Wait for Brew Time",
    page=page,
)
wait.center_position = (main_column_pos, row_margin + row_h * row_n)

## Check if done
row_n = row_n + 1
done_opt = drawpyo.diagram.Object(
    template_object=decision,
    value="All water poured?",
    page=page,
)
done_opt.center_position = (main_column_pos, row_margin + row_h * row_n)

## Wait for drawdown
row_n = row_n + 1
drawdown = drawpyo.diagram.Object(
    template_object=process, value="Wait for drawdown", page=page
)
drawdown.center_position = (main_column_pos, row_margin + row_h * row_n)


## Cleanup
row_n = row_n + 1
cleanup = drawpyo.diagram.Object(
    template_object=process,
    value="Remove filter and discard coffee",
    page=page,
)
cleanup.center_position = (main_column_pos, row_margin + row_h * row_n)

## Done
row_n = row_n + 1
end = drawpyo.diagram.object_from_library(
    library="flowchart",
    obj_name="terminator",
    value="Enjoy!",
    page=page,
)
end.center_position = (main_column_pos, row_margin + row_h * row_n)

# Create edges
## Recipe edges
recipe_1 = drawpyo.diagram.Edge(
    source=recipe,
    target=temp,
    page=page,
    exitX=0.5,
    exitY=1,
    entryX=0,
    entryY=0.5,
)
recipe_1_a = drawpyo.diagram.Edge(
    source=temp,
    target=kettle,
    page=page,
    )
recipe_2 = drawpyo.diagram.Edge(
    source=recipe,
    target=grind_size,
    page=page,
    exitX=0.5,
    exitY=1,
    entryX=0,
    entryY=0.5,
)
recipe_2_a = drawpyo.diagram.Edge(
    source=grind_size,
    target=grind,
    page=page,
    )
recipe_3 = drawpyo.diagram.Edge(
    source=recipe,
    target=bean_mass,
    page=page,
    exitX=0.5,
    exitY=1,
    entryX=0,
    entryY=0.5,
)
recipe_3_a = drawpyo.diagram.Edge(
    source=bean_mass,
    target=weigh,
    page=page,)
recipe_4 = drawpyo.diagram.Edge(
    source=recipe,
    target=pour_quant,
    page=page,
    exitX=0.5,
    exitY=1,
    entryX=0,
    entryY=0.5,
)
recipe_4_a = drawpyo.diagram.Edge(
    source=pour_quant,
    target=pour,
    page=page,
)

## Main flow edges
edge_1 = drawpyo.diagram.Edge(
    source=start,
    target=kettle,
    page=page,
    )
edge_2 = drawpyo.diagram.Edge(
    source=kettle,
    target=beans,
    page=page,
    )
edge_3 = drawpyo.diagram.Edge(
    source=beans,
    target=weigh,
    page=page,
    )
edge_4 = drawpyo.diagram.Edge(
    source=weigh,
    target=grind,
    page=page,
    )
edge_5 = drawpyo.diagram.Edge(
    source=grind,
    target=setup,
    page=page,
    )
edge_6 = drawpyo.diagram.Edge(
    source=setup,
    target=preheat_opt,
    page=page,
    )
preheat_yes = drawpyo.diagram.Edge(
    source=preheat_opt,
    target=preheat,
    value="Yes",
    page=page,
    )
preheat_no = drawpyo.diagram.Edge(
    source=preheat_opt,
    target=add_coffee,
    value="No",
    page=page,
    )
preheat_end = drawpyo.diagram.Edge(
    source=preheat,
    target=add_coffee,
    page=page,
    )
edge_7 = drawpyo.diagram.Edge(
    source=add_coffee,
    target=bloom_opt,
    page=page,
    )
bloom_no = drawpyo.diagram.Edge(
    source=bloom_opt,
    target=pour,
    value="No",
    page=page,
    )
bloom_yes = drawpyo.diagram.Edge(
    source=bloom_opt,
    target=bloom,
    value="Yes",
    page=page,
    )
edge_8 = drawpyo.diagram.Edge(
    source=bloom,
    target=pour,
    page=page,
    )
edge_9 = drawpyo.diagram.Edge(
    source=pour,
    target=wait,
    page=page,
    )
edge_10 = drawpyo.diagram.Edge(
    source=wait,
    target=done_opt,
    page=page,
    )
done_yes = drawpyo.diagram.Edge(
    source=done_opt,
    target=drawdown,
    value="Yes",
    page=page,
    )
done_no = drawpyo.diagram.Edge(
    source=done_opt,
    target=pour,
    value="No",
    exitX=0,
    exitY=0.5,
    entryX=0,
    entryY=0.75,
    page=page,
    )
edge_11 = drawpyo.diagram.Edge(
    source=drawdown,
    target=cleanup,
    page=page,
    )
edge_12 = drawpyo.diagram.Edge(
    source=cleanup,
    target=end,
    page=page,
    )

# Write the file
file.write()
