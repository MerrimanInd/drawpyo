# Basic Functionality

Drawpyo's basic functionality provides the same features as using the Draw.io app. You can create files with one or more pages, add objects to them, and position those objects. You can style objects from built-in shape libraries, manually, or from style strings. Those objects can be shapes, containers, or edges to connect them. Finally you can save your diagrams where they can be opened with the Draw.io app.

## Files

### Make a new file

A File object represents a Draw.io file. If no file_path is set the default path will be 'user/Drawpyo Charts' where 'user' will be an OS-specific user home folder.

```python
diagram = drawpyo.File()
file.file_path = r"C:\drawpyo"
file.file_name = "Test Generated Edges.drawio"
```

### Write a file

Files can be written simply with the write() function. This function takes a few parameters to make it more flexible:
| Parameter | Setting |
| - | - |
| `file_path` | This will overwrite the previously set file_path. |
| `file_name` | This will overwrite the previously set file_name. Like file_path, useful in creating multiple copies of a diagram with slight variations |
| `overwrite` | This boolean parameter controls whether an existing diagram should be overwritten or not. |

## Pages

### Add a page

The Page object represents the different diagram pages that you can create in Draw.io. A Page can be created without linking it to a File but it won't be writable without a File object.

```python
# Add a page
page = drawpyo.Page(file=file)
```

### Page Parameters

There are a number of customizable parameter for pages:

| argument    | description                                                |
| ----------- | ---------------------------------------------------------- |
| width       | Width of the document in pixels                            |
| height      | Height of the document in pixels                           |
| size_preset | Optional predefined page size. Overrides width and height. |
| grid        | Enable grid (0 or 1)                                       |
| grid_size   | Side of grid squares in pixels                             |
| guides      | Enable guides (0 or 1)                                     |
| tooltips    | Enable tooltips (0 or 1)                                   |
| scale       | Scale of the drawing                                       |
