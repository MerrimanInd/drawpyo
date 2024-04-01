# Formatting Text

Everywhere that text appears in Draw.io has the same basic text formatting options. TO support this in drawpyo there's a custom class, `TextFormat`, that handles all of these options for code reusability. This also means that `TextFormat` objects can be created and copied into new objects or edges to make reformatting text convenient.

Any object with formattable text will have a .text_format attribute that holds a `TextFormat` class.

## Type Face Attributes

| Attribute     | Data Type | Description                                                  |
| ------------- | --------- | ------------------------------------------------------------ |
| `fontFamily`  | str       | The typeface to use. See Draw.io for a list of font choices. |
| `fontSize`    | int       | The size of the font in points                               |
| `fontColor`   | str       | The color of the typeface                                    |
| `bold`        | bool      | Bold font                                                    |
| `italic`      | bool      | Italic font                                                  |
| `underline`   | bool      | Underlined font                                              |
| `textShadow`  | bool      | Whether to place a shadow underneath the text                |
| `textOpacity` | int       | The transparency level of the text. 0-100                    |

## Text Alignment and Spacing Attributes

The text is rendered inside a box and various layout and alignment choices can be made to control where and how it's positioned.

| Attribute       | Data Type | Description                                                                   |
| --------------- | --------- | ----------------------------------------------------------------------------- |
| `spacing`       | int       | The global spacing to add around the text and the outside of the bounding box |
| `spacingTop`    | int       | The top spacing to add around the text                                        |
| `spacingBottom` | int       | The bottom spacing to add around the text                                     |
| `spacingLeft`   | int       | The left spacing to add around the text                                       |
| `spacingRight`  | int       | The right spacing to add around the text                                      |
| `direction`     | str       | The direction to orient the text. Can be 'horizontal' or 'vertical'           |
| `align`         | str       | The horizontal alignment of the text. Can be 'left', 'center', or 'right'     |
| `verticalAlign` | str       | The vertical alignment of the text. Can be 'top', 'middle', or 'bottom'       |

Spacing Attributes

## Label Box Attributes

Some aspects of the text bounding box itself can also be formatted.

| Attribute              | Data Type | Description                                                         |
| ---------------------- | --------- | ------------------------------------------------------------------- |
| `labelBorderColor`     | str       | The color of the border around the bounding box                     |
| `labelBackgroundColor` | str       | The color of the fill of the bounding box                           |
| `labelPosition`        | str       | The position of the bounding box as it relates to the owning object |
