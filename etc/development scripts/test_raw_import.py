from drawpyo import parse_drawio_file
from pathlib import Path

# File path
relative_path = Path("..") / "reference drawio charts" / "Text Object.drawio"
file_path = (Path(__file__).parent / relative_path).resolve()

# Parse
cells = parse_drawio_file(file_path)

# Output
for cell_id, cell in cells.items():
    print(cell)
