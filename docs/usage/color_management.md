# Color Management

Drawpyo supports three ways to handle colors:

1. **Hex strings**
2. **Standard colors** - a built-in palette of named hex colors for easier access.
3. **Color schemes** - a reusable object that groups fill, strokeand  font colors.

---

## Standard Colors

Drawpyo includes a set of predefined colors exposed through the StandardColor enum.
These match the standard Draw.io color palette and are arranged from lightest (1) to darkest (9) within each color family.

```python
from drawpyo import StandardColor

item.fill_color = StandardColor.BLUE5
item.stroke_color = StandardColor.GRAY4
```

All values inside the enum are strings (e.g., `"#007FFF"`).
When used inside a `ColorScheme`, enum values automatically resolve to their underlying hex string.

Because the enum includes many shades, it provides a convenient palette for consistent styling across diagrams.

---

# Color Schemes

A `ColorScheme` represents a small set of related colors used for an object's fill, stroke and font.
Each color value may be:

* `None`
* a hex string of the form `#RRGGBB`
* a `StandardColor` enum value

```python
from drawpyo import ColorScheme, StandardColor

scheme = ColorScheme(
    fill_color=StandardColor.BLUE5,
    stroke_color="#FF0000",
)
```

Invalid hex strings raise a `ValueError`.

---

## Setting Colors

Each component may be updated after creation:

```python
scheme.set_fill_color("#ABCDEF")
scheme.set_stroke_color(StandardColor.GRAY7)
scheme.set_gradient(None)
```

---

## Color Hierarchy

When creating an object without specifying its colors  - or when explicitly passing `None` - Drawpyo applies a default value.
Colors can come from three possible sources, and Drawpyo resolves them in the following order:

### **1. Object-specific colors**

Colors provided directly to an object take the highest priority:

* `fill_color`
* `stroke_color`
* `fontColor` (via an object’s `text_format`)

If these are set, they always override any color scheme applied to the object.

### **2. Color Scheme**

If an object has a `ColorScheme` assigned and no object-specific color overrides it,
its `fill_color`, `stroke_color` and `font_color` values are used.

### **3. Defaults**

If neither object-specific colors nor a color scheme provide a value, Drawpyo falls back to the default colors used internally (e.g., Draw.io defaults).

---

### Summary

```
Object-specific colors  >  Color scheme colors  >  Default colors
```

This hierarchy ensures that explicit styling always wins, while still allowing consistent themes via color schemes and reasonable defaults where nothing is specified.