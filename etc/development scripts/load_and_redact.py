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
drawio_redacted_output_path = base_dir / "Redacted Drawio File.drawio"
drawio_restored_output_path = base_dir / "Restored Drawio File.drawio"

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
# Write redacted draw.io file
# --------------------------------------------------

redacted_file = drawpyo.File()
redacted_file.file_path = str(base_dir)
redacted_file.file_name = drawio_redacted_output_path.name

redacted_page = drawpyo.Page(file=redacted_file)

# Add shapes
for shape in redacted_diagram.shapes:
    shape.page = redacted_page

# Add edges
for edge in redacted_diagram.edges:
    edge.page = redacted_page

redacted_file.write()

# --------------------------------------------------
# Restore diagram from map
# --------------------------------------------------

restored_diagram = drawpyo.utils.restore_values(
    redacted_diagram,
    map_file_path=redaction_map_path,
)

# --------------------------------------------------
# Write restored (unredacted) draw.io file
# --------------------------------------------------

restored_file = drawpyo.File()
restored_file.file_path = str(base_dir)
restored_file.file_name = drawio_restored_output_path.name

restored_page = drawpyo.Page(file=restored_file)

# Add shapes
for shape in restored_diagram.shapes:
    shape.page = restored_page

# Add edges
for edge in restored_diagram.edges:
    edge.page = restored_page

restored_file.write()
