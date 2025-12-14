from pathlib import Path
import drawpyo
from drawpyo import load_diagram

# Load Draw.io diagram
relative_path = Path("..") / "reference drawio charts" / "Pourover Flowchart.drawio"
file_path = (Path(__file__).parent / relative_path).resolve()

diagram = load_diagram(file_path)

# Create file & page
file = drawpyo.File()
file.file_path = str(Path.home() / "Test Drawpyo Charts")
file.file_name = "Converted From Draw.io.drawio"

page = drawpyo.Page(file=file)

# Add shapes to page
for shape in diagram.shapes:
    shape.page = page

# Add edges to page
for edge in diagram.edges:
    edge.page = page

# Write the file
file.write()
