# Objects

Though some diagram types have their own object subclasses, the main class for creating objects is the BasicObject class.

## Creating a basic object

```python
base_obj = drawpyo.diagram.BasicObject(page=page)
```

The default object type is a rounded corner rectangle with white background and a black border just like in the Draw.io app.

The value attribute holds the text to display in the object.

```python
base_obj.value = "This Object's Name is Fred"
```

### Creating an object from a shape library

Just like the built-in shape libraries in the Draw.io app, Drawpyo supports generating shapes from libraries. Currently the 'general' library from the Draw.io app is defined but more will be added in the future.

> These libraries are defined in TOML files and drawpyo supports importing custom shape libraries! See [Shape Libraries][/usage/shape_libs.md] for more information.

To generate an object from a library:

```python
object = drawpyo.diagram.object_from_library(
    library="general",
    obj_name="process",
    page=page,
    )
```

This function returns a normal BasicObject but prestyled by the library. It can then be further styled or modified.

## Object Geometry

All objects contain a structure called ObjectGeometry that provides a layer of abstraction. Interacting directly with the geometry class is optional.

### Object Sizing

The three parameters that affect object placement are size and aspect. Size can be set with a tuple containing the width then height.

```python
BasicObject.size = (120, 80)
BasicObject.aspect = 'fixed'
```

The `size` attribute is an abstraction of the ObjectGeometry object, so the width and height can also be accessed directly.

```python
BasicObject.geometry.height = 80
BasicObject.geometry.width = 120
```

### Object Geometry and Placement

Repositioning objects is simple but there are a few convenience features to know about. There are two attributes available for setting the position by either the top left corner or the center:

```python
BasicObject.position = (0, 0)
BasicObject.center_position = (0, 0)
```

As with the size, the X and Y positions can be accessed directly in the geometry object.

```python
BasicObject.geometry.x = 0
BasicObject.geometry.y = 0
```

## Styling Objects

There are infinite permutations of object formatting and styling available. There are some higher order attributes that set the template for the object. What lower order styling attributes may or may not apply in combination. Then there are attributes like size and text formatting that apply in all cases. These interactions are difficult to predict in drawpyo alone so a good way to get familiar with all of the possible options and types of customizations is just to play with the Draw.io app directly to design formatting to your taste.

Almost all styling attributes are optional (and drawpyo adds the non-optional ones automatically). If an attribute is unset or set to None then it won't be included in the file output. This will set that specific styling behavior to a default mode.

### BaseStyle and Shape

The highest order styling attribute in Draw.io for objects is `shape`. This sets how the object behaves and is rendered. Different values include:

- parallelogram
- shape
- process
- hexagon
- document
- cylinder3
- internalStorage
- cube
- step
- tape
- trapezoid
- note
- card
- callout
- dataStorage

and many more.

Confusingly there is another attribute called `baseStyle` that is sometimes used in combination with `shape` and sometimes without.

BaseStyles include:

- text
- ellipse
- rhombus
- triangle
- swimlane

It can be hard to predict how these two attributes will interact. To utilize them it's recommended to start in the Draw.io app, use their shape libraries or templates to get the desired style, then look at the style string to see what `shape` and `baseStyle` were used. When creating an object from a shape library these two attributes are handled automatically.

### Basic Styling Attributes

These attributes mostly apply to most shape/baseStyle combinations and can be set on almost any object.

- rounded
- fillColor
- strokeColor
- opacity
- whiteSpace
- glass
- shadow
- comic
- linePattern

### Further Styling Attributes

As mentioned above, not all of these attributes will apply to all object shapes and types. But some commonly called include:

- darkOpacity
- darkOpacity2
- backgroundOutline
- perimeter

### Text Styling Attributes

The text set in the `value` attribute of the BasicObject class can also be styled with the expected text formatting tools.

- fontColor
- fontFamily
- fontSize
- align
- verticalAlign
- labelPosition
- labelBackgroundColor
- labelBorderColor
- textOpacity

Due to complexities with the actual combination of styling strings used by Draw.io, there are some more that are abstracted by drawpyo to make them easy to work with:

- text_direction
- bold_font
- italic_font
- underline_font

| Attribute               | Data Type                             |
| ----------------------- | ------------------------------------- |
| `fontColor`             | str (Hex Code: '#ffffff')             |
| `fontFamily`            | str (see Draw.io for available fonts) |
| `fontSize`              | int (size in pts)                     |
| `align`                 | str ('left', 'center', or 'right')    |
| `verticalAlign`         | str ('top', 'middle', 'bottom')       |
| `labelPosition`         | str ('left', 'center', or 'right')    |
| `verticalLabelPosition` | str ('top', 'middle', 'bottom')       |
| `labelBackgroundColor`  | str (Hex Code: '#ffffff')             |
| `labelBorderColor`      | str (Hex Code: '#ffffff')             |
| `textOpacity`           | int (0-100)                           |
| `text_direction`        |                                       |
| `bold_font`             | bool                                  |
| `italic_font`           | bool                                  |
| `underline_font`        | bool                                  |
