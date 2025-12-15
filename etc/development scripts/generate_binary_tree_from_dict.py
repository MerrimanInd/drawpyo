from drawpyo.diagram_types.binary_tree import BinaryTreeDiagram
import drawpyo
from os import path

data = {
    "Appliances for Grinding Coffee": {
        "Burr Grinders": {
            "Conical Burrs": {
                "Manual": [
                    "Comandante",
                    "Weber HG-2",
                ],
                "Electric": ["Baratza Encore", "Niche Zero"],
            },
            "Flat Burrs": ["Turin DF64", "Lagom P64"],
        },
        "Blunt Objects": ["Mortar and Pestle"],
    }
}


color_schemes = [
    drawpyo.ColorScheme(
        font_color=drawpyo.StandardColor.GRAY1,
        stroke_color="#3C755E",
        fill_color="#5BA283",
    ),
    drawpyo.ColorScheme(
        font_color=drawpyo.StandardColor.GRAY1,
        stroke_color="#3C756E",
        fill_color="#5BA299",
    ),
    drawpyo.StandardColor.CRIMSON4,
    drawpyo.ColorScheme(
        font_color=drawpyo.StandardColor.GRAY1,
        stroke_color="#3C4F75",
        fill_color="#5B6EA2",
    ),
    "#A25B99",
]

tree = BinaryTreeDiagram.from_dict(
    data,
    file_path=path.join(path.expanduser("~"), "Test Drawpyo Charts"),
    file_name="Coffee Grinders Binary from Dict.drawio",
    direction="down",
    colors=color_schemes,
)

tree.write()
