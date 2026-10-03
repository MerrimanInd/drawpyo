from pathlib import Path

import drawpyo
from drawpyo import load_diagram

# Load Draw.io diagram
relative_path = Path("..") / "reference drawio charts" / "object.drawio"
file_path = (Path(__file__).parent / relative_path).resolve()

diagram = load_diagram(file_path)

# Create file & page
file = drawpyo.File()
file.file_path = str(Path.home() / "Test Drawpyo Charts")
file.file_name = "Test_object.drawio"

page = drawpyo.Page(file=file)

diagram.add_to(page)
# Write the file
file.write()
