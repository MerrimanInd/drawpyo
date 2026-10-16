from pathlib import Path

from drawpyo.diagram_types import DependencyDiagram


repository_root = Path(__file__).resolve().parents[2]
output_path = repository_root / "etc" / "reference drawio charts"

diagram = DependencyDiagram.create_from_path(
    repository_root / "src" / "drawpyo",
    granularity="package",
    include_external=True,
    include_standard_library=False,
    file_path=output_path,
    file_name="Drawpyo Package Dependencies.drawio",
    direction="right",
    link_style="orthogonal",
    show_metrics=True,
    show_edge_weights=True,
)

diagram.write()
