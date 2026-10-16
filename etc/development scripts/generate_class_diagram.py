from pathlib import Path

import drawpyo
from drawpyo.diagram_types import ClassDiagram


output_path = Path(__file__).resolve().parents[1] / "reference drawio charts"

diagram = ClassDiagram.create_from_module(
    drawpyo,
    file_path=str(output_path),
    file_name="Drawpyo Class Inheritance.drawio",
    direction="down",
    link_style="orthogonal",
    level_spacing=100,
    item_spacing=30,
)

diagram.write()
