# Parent and Child Objects

In Draw.io, any object can have a parent. This is used within the app for containers and lists but actually any object can have subobjects. Within the XML this is achieved just be setting the `parent` attribute from `1` (the page) to any other object's ID. This changes the X and Y coordinates of the child object to be relative to the parent's X and Y coordinates.

Drawpyo has convenient support for subobjects with a handful of attributes and parameters.

## Linking Parent and Child Objects

A parent object can be assigned to any subobject either during instantiation or after the fact by using the `parent` property. Every object has this property as well as a `children` property that's a list of other objects.

Creating the parent object:

```python
parent_container = drawpyo.diagram.object_from_library(
    library="general", obj_name="labeled_horizontal_container", page=page
)
```

Adding child objects:

```python
block_1 = drawpyo.diagram.object_from_library(
    library="general", obj_name="rectangle", page=page
)
block_1.value = "Block 1"
block_1.parent = parent_container

block_2 = drawpyo.diagram.Object(
    position_rel_to_parent=(300, 300), parent=parent_container, value="Block 2", page=page
)
```

There are also methods for adding and removing objects:

```python
    parent_container.add_object(block_1)
    parent_container.remove_object(block_2)
```

This will create or remove the link on both ends (set the parent attribute of the child object as well as add the child to the parents. These functions are called by the setters of the `parent` property, this is just an alternate syntax.

## Positioning

Within the Draw.io application, child objects X and Y coordinates are relative to the parent object. This isn't always useful so drawpyo offers two different position attributes. Both are tuples of ints: (X, Y). They both modify or return the underlying Geometry object so they can be used interchangeably and are not duplicate variables.

The normal `position` attribute continues to be relative to the page regardless of whether there's a parent object set.

There is also a `position_rel_to_parent` attribute that will return the position with respect to the position of the parent.

## Autosizing

It's useful to have a parent object expand or contract to fit its objects. This behavior is disabled by default but can be enabled by setting the `autosize_to_children` boolean parameter to True. There is also a corresponding parameter called `autosize_margin` that sets the margin to maintain around the child objects in pixels. When this is set anytime that a child object is added, resized, or repositioned the parent will expand to fit the contents plus the margins. By default the parent will never contract unless `autocontract` is set to True as well.

> Note that the margin is inclusive of a container's title block.

The autofit behavior can also be called manually using the `resize_to_children()` function on an object. This will respect the autofit_margin and autocontract behavior.

## Combining Relative Positioning and Autosizing

Combining the autosizing behavior with relative positioning can cause unexpected behavior. Since the parent object will resize every time a child object is added or moved within it the successive objects added will now be relative to a new updated parent object position. This will make your code order-dependent.

To avoid this, either disable `autosize_to_children` or use absolute positioning for child objects.
