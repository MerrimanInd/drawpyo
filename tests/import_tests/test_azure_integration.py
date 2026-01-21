#!/usr/bin/env python3
"""
Integration test for importing Azure icons from real XML mxlibrary file.
Tests the full workflow: load from URL, register, create objects, build diagram.
"""

import drawpyo


def main():
    print("\n" + "=" * 60)
    print("Azure mxLibrary Import Integration Test")
    print("=" * 60)

    # URL to Azure icons XML file
    azure_url = "https://raw.githubusercontent.com/dwarfered/azure-architecture-icons-for-drawio/refs/heads/main/azure-public-service-icons/004%20azure%20ecosystem.xml"

    print("\n1. Registering Azure library...")
    print(f"   Source: {azure_url[:60]}...")

    try:
        # Register the library
        drawpyo.register_mxlibrary("azure", azure_url)
        print("   ✓ Library registered successfully")
    except Exception as e:
        print(f"   ✗ Failed to register library: {e}")
        return

    # Verify library was registered
    print("\n2. Verifying library registration...")
    from drawpyo.diagram.objects import base_libraries

    if "azure" in base_libraries:
        azure_shapes = base_libraries["azure"]
        print(f"   ✓ Found {len(azure_shapes)} shapes in library")

        # Display first 10 shape names
        shape_names = list(azure_shapes.keys())[:10]
        print("\n   First 10 shapes:")
        for i, name in enumerate(shape_names, 1):
            print(f"   {i:2}. {name}")

        if len(base_libraries["azure"]) > 10:
            print(f"   ... and {len(base_libraries['azure']) - 10} more")
    else:
        print("   ✗ Azure library not found in base_libraries")
        return

    # Create a test diagram with imported shapes
    print("\n3. Creating test diagram...")
    try:
        # Create a new diagram file
        file = drawpyo.File()
        file.file_name = "azure_diagram_test"
        file.file_path = "./etc/reference drawio charts"

        # Create a page
        page = drawpyo.Page(file=file)
        page.name = "Azure Test"

        # Get the first two shape names
        shape_names = list(azure_shapes.keys())[:2]

        print(f"   Creating {len(shape_names)} objects...")

        # Create objects from the imported library
        obj1 = drawpyo.diagram.object_from_library(
            library="azure",
            obj_name=shape_names[0],
            page=page,
            position=(100, 100),
        )
        print(f"   ✓ Created: {shape_names[0]}")

        if len(shape_names) > 1:
            obj2 = drawpyo.diagram.object_from_library(
                library="azure",
                obj_name=shape_names[1],
                page=page,
                position=(300, 100),
            )
            print(f"   ✓ Created: {shape_names[1]}")

            # Create an edge between them
            edge = drawpyo.diagram.Edge(page=page, source=obj1, target=obj2)
            edge.label = "connects to"
            print("   ✓ Created edge between objects")

        # Save the diagram
        file.write()
        print(f"   ✓ Diagram saved to: {file.file_path}/{file.file_name}.drawio")

        # Verify the file was created
        import os

        file_path = os.path.join(file.file_path, f"{file.file_name}.drawio")
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"   ✓ File exists: {file_size} bytes")

            # Read and verify content
            with open(file_path, "r") as f:
                content = f.read()

            # Check for expected elements
            checks = [
                ("mxGraphModel" in content, "mxGraphModel element"),
                ("mxCell" in content, "mxCell elements"),
                ('value="' in content, "object values"),
            ]

            print("\n   Content verification:")
            for check, description in checks:
                status = "✓" if check else "✗"
                print(f"   {status} {description}")

            # Count important elements
            mx_cell_count = content.count("<mxCell")
            print(f"   ✓ Found {mx_cell_count} mxCell elements")

            # Check for SVG data in the style strings
            if "data:image/svg+xml" in content:
                svg_count = content.count("data:image/svg+xml")
                print(f"   ✓ Found {svg_count} embedded SVG images")
            else:
                print("   ✗ No SVG data found in diagram")

            print(f"   ✓ Diagram saved to: {file.file_path}/{file.file_name}.drawio")
            print("\n" + "=" * 60)
            print("✓ Test completed successfully!")
            print("=" * 60)
            print(f"\nYou can open the file in Draw.io:")
            print(f"  {file.file_path}/{file.file_name}.drawio")
        else:
            print(f"   ✗ File not found: {file_path}")
    except Exception as e:
        print(f"   ✗ Failed to create diagram: {e}")
        import traceback

        traceback.print_exc()
        return

    # Additional verification: check base_libraries still has the library
    print("\n4. Final verification...")
    if "azure" in base_libraries:
        print("   ✓ Azure library still registered in base_libraries")
        try:
            # Try to create one more object to verify library is still usable
            file2 = drawpyo.File()
            page2 = drawpyo.Page(file=file2)
            test_obj = drawpyo.diagram.object_from_library(
                library="azure", obj_name=shape_names[0], page=page2, position=(0, 0)
            )
            print(f"   ✓ Successfully created additional object: {shape_names[0]}")
        except Exception as e:
            print(f"   ✗ Failed to create additional object: {e}")
    else:
        print("   ✗ Azure library not found in base_libraries")


if __name__ == "__main__":
    main()
