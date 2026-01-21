# Shape Libraries

The Draw.io app has a lot of built-in shape libraries available. The basic library contains shapes and building blocks but there are increasingly more specific libraries such as flowcharts, wiring diagrams, and org charts. You can also export and import shape libraries into Draw.io.

To replicate this feature for drawpyo, we provide two options for shape libraries:

1. **TOML format** - A custom human-readable library format we created for drawpyo, which is simpler and more accessible than XML for defining custom shapes.
2. **Draw.io's native XML format (mxlibrary)** - Direct support for Draw.io's XML shape libraries, which is useful for using third-party icon libraries like Azure, AWS, or Google Cloud icons.

## Built-In Shape Libraries

Drawpyo uses these TOML shape libraries to store the default libraries. The default libraries are in /drawpyo/shape_libraries. These are the libraries that are available in the Draw.io app.

Implemented default libraries:

- General
- Flowchart

There is also a set of TOML databases for other formats, like all of the various combinations of edge styles and the line styles. These are stored in /drawpyo/formatting_database.

## Custom Shape Libraries

This functionality is available to the user so you can define your own custom libraries! TOML was selected because it's a very simple and human-readable config file format. [the TOML project website](https://toml.io/) has a very nice high level overview. But drawpyo is hardly scratching the surface of what TOML is capable of so little expertise is needed.

### Creating a Shape Library

To define a shape library create a .toml file. Current convention is to start with a title tag for clarity.

```toml
title = "Custom drawpyo shapes"
```

You can then define a custom object by naming the object in square brackets and adding whichever attributes you want:

```toml
[square]
width = 80
height = 80
aspect = "fixed"
```

You can also have any shape inherit another and then either modify or extend its style:

```toml
[perfect_circle]
inherit = "square"
baseStyle = "ellipse"
```

This `perfect_circle` will now inherit the fixed aspect and size attributes from `square` but with the ellipse baseStyle.

### Style Attribute Types

The attributes in the TOML file can come from three sets:

#### Drawpyo attributes (snake_case)

These are the attributes that drawpyo uses to abstract some complicated style strings, such as `size` instead of the Draw.io parameters of `width` and `height`.

#### Predefined style attributes

Such as any of the attributes listed in the Styling section of [Objects](/usage/objects.md). These will simply be overwritten with the values in the TOML file.

#### Any new style attributes

If you want to add a rare style attribute that drawpyo hasn't defined or worked with yet, no worries! When you import the TOML library if there are new style attributes defined then they'll get added to the Object and exported into the Draw.io file.

### Using a Custom Library

To use a custom shape library it just needs to be imported then passed to the object definition function:

```python
custom_library = drawpyo.diagram.import_shape_database(
    file_name=r"path/to/toml_lib"
    )

new_obj = drawpyo.diagram.object_from_library(
    library = custom_library,
    obj_name = 'object_name_from_lib',
    page=page,
    )
```

## XML Shape Libraries (mxlibrary)

Drawpyo can import and use Draw.io's native XML shape library format (`.xml` files with `<mxlibrary>` tags). This is particularly useful for using third-party icon libraries like Azure icons, AWS icons, Google Cloud icons, and other custom shape collections available online.

### What is an mxlibrary?

An mxlibrary is Draw.io's XML-based format for storing collections of shapes. These files typically contain shapes with embedded SVG images and are commonly used for icon libraries. The format looks like:

```xml
<mxlibrary>[
  {
    "h": 50,
    "w": 50,
    "title": "Icon-Name",
    "xml": "...encoded shape data..."
  }
]</mxlibrary>
```

### Loading an mxlibrary

You can load an mxlibrary from either a local file or a URL:

```python
import drawpyo

# Load from a URL
shapes = drawpyo.load_mxlibrary(
    "https://example.com/azure-icons.xml"
)

# Load from a local file
shapes = drawpyo.load_mxlibrary(
    "/path/to/local/library.xml"
)
```

The `load_mxlibrary()` function returns a dictionary of shapes that can be used directly with `object_from_library()`.

### Registering an mxlibrary

For easier reuse, you can register an mxlibrary with a name, making it available just like the built-in libraries:

```python
import drawpyo

# Register the Azure icons library
drawpyo.register_mxlibrary(
    "azure",
    "https://raw.githubusercontent.com/dwarfered/azure-architecture-icons-for-drawio/main/azure-public-service-icons/004%20azure%20ecosystem.xml"
)

# Now use it like a built-in library
file = drawpyo.File()
page = drawpyo.Page(file=file)

vm_icon = drawpyo.diagram.object_from_library(
    library="azure",
    obj_name="01038-icon-service-Collaborative-Service",
    page=page,
    position=(100, 100)
)

file.write()
```

### Using mxlibrary Shapes

Once loaded or registered, you can use shapes from an mxlibrary in three ways:

#### 1. Register and use by name (recommended)

```python
import drawpyo

# Register once
drawpyo.register_mxlibrary(
    "custom",
    "https://example.com/custom-icons.xml"
)

# Use multiple times
file = drawpyo.File()
page = drawpyo.Page(file=file)

icon1 = drawpyo.diagram.object_from_library(
    library="custom",
    obj_name="Shape-Name-1",
    page=page,
    position=(50, 50)
)

icon2 = drawpyo.diagram.object_from_library(
    library="custom",
    obj_name="Shape-Name-2",
    page=page,
    position=(150, 50)
)
```

#### 2. Load and pass the dictionary directly

```python
import drawpyo

# Load the library
shapes = drawpyo.load_mxlibrary("https://example.com/icons.xml")

file = drawpyo.File()
page = drawpyo.Page(file=file)

# Pass the dictionary directly
icon = drawpyo.diagram.object_from_library(
    library=shapes,  # Pass the dict
    obj_name="Icon-Name",
    page=page,
    position=(100, 100)
)
```

#### 3. Use with other object parameters

Like other shapes, you can override properties when creating objects from mxlibraries:

```python
icon = drawpyo.diagram.object_from_library(
    library="azure",
    obj_name="Virtual-Machine",
    page=page,
    position=(100, 100),
    width=80,  # Override default width
    height=80,  # Override default height
)
```

### Finding Shape Names

To find the available shape names in an mxlibrary:

```python
import drawpyo

shapes = drawpyo.load_mxlibrary("https://example.com/icons.xml")

# List all available shape names
print("Available shapes:")
for shape_name in shapes.keys():
    print(f"  - {shape_name}")
```

### Error Handling

The mxlibrary functions include comprehensive error handling:

```python
import drawpyo

try:
    drawpyo.register_mxlibrary(
        "mylib",
        "https://example.com/library.xml"
    )
except FileNotFoundError:
    print("Library file not found")
except ValueError as e:
    print(f"Error loading library: {e}")
```

### Example: Complete Workflow with Azure Icons

```python
import drawpyo

# Register the Azure icons library
drawpyo.register_mxlibrary(
    "azure",
    "https://raw.githubusercontent.com/dwarfered/azure-architecture-icons-for-drawio/main/azure-public-service-icons/004%20azure%20ecosystem.xml"
)

# Create a diagram
file = drawpyo.File()
file.file_name = "azure_architecture"
file.file_path = "./output"

page = drawpyo.Page(file=file)
page.name = "Azure Architecture"

# Add Azure service icons
vm = drawpyo.diagram.object_from_library(
    library="azure",
    obj_name="01038-icon-service-Collaborative-Service",
    page=page,
    position=(100, 100)
)

storage = drawpyo.diagram.object_from_library(
    library="azure",
    obj_name="01039-icon-service-Storage-Account",
    page=page,
    position=(300, 100)
)

# Connect them with an edge
edge = drawpyo.diagram.Edge(
    page=page,
    source=vm,
    target=storage
)

# Save the diagram
file.write()
```

### Where to Find mxlibrary Files

Many organizations and communities provide mxlibrary files for Draw.io:

- **Azure Icons**: [GitHub - dwarfered/azure-architecture-icons-for-drawio](https://github.com/dwarfered/azure-architecture-icons-for-drawio)
- **AWS Icons**: Available from AWS Architecture Icons
- **Google Cloud Icons**: Available from Google Cloud Architecture Diagramming Tool
- **Custom Libraries**: Export your own from Draw.io via File → Export → Library

You can also create your own mxlibrary files using the Draw.io application by selecting shapes and exporting them as a library.
