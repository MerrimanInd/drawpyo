from drawpyo.diagram_types.tree import TreeDiagram
from os import path

data = {
    "Appliances for Grinding Coffee": {
        "Blade Grinders": ["Electric Blade Grinder"],
        "Burr Grinders": {
            "Conical Burrs": {
                "Manual": [
                    "Hario Skerton",
                    "Comandante",
                    "ZJpresso JX-Pro",
                    "Weber HG-2",
                ],
                "Electric": ["Baratza Encore", "Niche Zero", "Weber Key"],
            },
            "Flat Burrs": ["Turin DF64", "Fellow Ode", "Lagom P64"],
        },
        "Blunt Objects": ["Mortar and Pestle"],
    }
}


tree = TreeDiagram.from_dict(
    data,
    file_path=path.join(path.expanduser("~"), "Test Drawpyo Charts"),
    file_name="Coffee Grinders from Dict.drawio",
    direction="down",
)

tree.write()
