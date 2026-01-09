from pathlib import Path
import drawpyo
from drawpyo import load_diagram

# --------------------------------------------------
# Paths
# --------------------------------------------------

base_dir = Path.home() / "Test Drawpyo Charts"
base_dir.mkdir(parents=True, exist_ok=True)

drawio_input_path = (
    Path(__file__).parent
    / ".."
    / "reference drawio charts"
    / "Pourover Flowchart.drawio"
).resolve()

redaction_map_path = base_dir / "redaction_map.json"
drawio_output_path = base_dir / "Redacted Drawio File.drawio"

# --------------------------------------------------
# Load diagram
# --------------------------------------------------

diagram = load_diagram(drawio_input_path)

# --------------------------------------------------
# Redact diagram + write map
# --------------------------------------------------

redacted_diagram = drawpyo.utils.redact_values(
    diagram,
    map_file_path=redaction_map_path,
)

# --------------------------------------------------
# Create output file
# --------------------------------------------------

file = drawpyo.File()
file.file_path = str(base_dir)
file.file_name = drawio_output_path.name

page = drawpyo.Page(file=file)

# Add shapes
for shape in redacted_diagram.shapes:
    shape.page = page

# Add edges
for edge in redacted_diagram.edges:
    edge.page = page

# Write draw.io file
file.write()
