from drawpyo import parse_drawio_file
from pathlib import Path
from drawpyo import build_drawpyo_elements
import drawpyo

# File path
relative_path = Path("..") / "reference drawio charts" / "Pourover Flowchart.drawio"
file_path = (Path(__file__).parent / relative_path).resolve()

# Parse Draw.io file into raw cells
cells = parse_drawio_file(file_path)

# Convert RawMxCells into drawpyo objects
elements = build_drawpyo_elements(cells)

# Create a new drawpyo File and Page
file = drawpyo.File()
file.file_path = str(Path.home() / "Test Drawpyo Charts")
file.file_name = "Converted From Draw.io.drawio"

page = drawpyo.Page(file=file)

# Add all elements to the page
for elem in elements.values():
    elem.page = page

# Write the file
file.write()

print(f"File created at: {file.file_path}/{file.file_name}")
