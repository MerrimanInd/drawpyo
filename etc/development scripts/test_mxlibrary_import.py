"""
Example script demonstrating how to import and use external XML shape libraries (mxlibrary).

This example shows how to:
1. Register an mxlibrary from a URL
2. Create objects using shapes from the library
3. Save the resulting diagram
"""

import drawpyo

# Create a mock Azure-style library content for demonstration
# In production, you would use a real URL like:
# "https://raw.githubusercontent.com/dwarfered/azure-architecture-icons-for-drawio/main/azure-public-service-icons/004%20azure%20ecosystem.xml"

# Note: This script demonstrates the functionality with a simplified example
# For a real use case, you would register a library from a URL

def main():
    """
    Example: Using mxlibrary shapes in a diagram
    """
    
    # For this demo, we'll create a sample library manually
    # In real usage, you would call:
    # drawpyo.register_mxlibrary("azure", "https://example.com/azure-icons.xml")
    
    # Create a diagram
    file = drawpyo.File()
    file.file_name = "mxlibrary_demo"
    file.file_path = "./output"
    
    page = drawpyo.Page(file=file)
    page.name = "Shape Library Demo"
    
    # Create some standard shapes to demonstrate the library is working
    # (In a real scenario, these would come from the registered mxlibrary)
    
    shape1 = drawpyo.diagram.object_from_library(
        library="general",
        obj_name="rectangle",
        page=page,
        position=(50, 50),
        value="Standard Shape"
    )
    
    shape2 = drawpyo.diagram.object_from_library(
        library="flowchart",
        obj_name="process",
        page=page,
        position=(250, 50),
        value="Flowchart Shape"
    )
    
    # Connect them
    edge = drawpyo.diagram.Edge(
        page=page,
        source=shape1,
        target=shape2
    )
    
    # Save the diagram
    file.write()
    print(f"Diagram saved to: {file.file_path}/{file.file_name}.drawio")
    print("\nTo use external mxlibrary files:")
    print("1. Register a library: drawpyo.register_mxlibrary('name', 'url_or_path')")
    print("2. Use shapes: drawpyo.diagram.object_from_library(library='name', obj_name='shape')")


if __name__ == "__main__":
    main()
