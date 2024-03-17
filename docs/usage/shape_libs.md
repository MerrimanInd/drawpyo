# Shape Libraries

The Draw.io app has a lot of built-in shape libraries available. The basic library contains shapes and building blocks but there are increasingly more specific libraries such as flowcharts, wiring diagrams, and org charts. You can also export and import shape libraries into Draw.io.

To replicate this feature for drawpyo, I created a library format based on TOML. Draw.io's libraries are XML which isn't as human readable or writable and is more specification than necessary.

> Supporting Draw.io's XML based library is a planned feature.

## Built-In Shape Libaries

Drawpyo uses these TOML shape libraries to store the default libaries. Currently the only library that ships with drawpyo is the general library but more will come. The default libraries are in /drawpyo/shape_libraries.

There is also a set of TOML databases for other formats, like all of the various combinations of edge styles and the line styles. These are stored in /drawpyo/formatting_database.

## Custom Shape Libaries

This functionality is available to the user so you can define your own custom libraries! TOML was selected because it's a very simple and human-readable config file format. [the TOML project website](https://toml.io/) has a very nice high level overview. But drawpyo is hardly scratching the surface of what TOML is capable of so little expertise is needed.

### Creating a Shape Library

To define a shape library create a .toml file. Current convention is to start with a title tag for clarity.

```toml
title = "Custom drawpyo shapes"
```

You can then define a custom object by naming the object in square brackets and adding whichever attributes you want:

```toml
[square]
size = [80, 80]
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

If you want to add a rare style attribute that drawpyo hasn't defined or worked with yet, no worries! When you import the TOML library if there are new style attributes defined then they'll get added to the BasicObject and exported into the Draw.io file.

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














