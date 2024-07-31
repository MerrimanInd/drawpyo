from .objects import Object, object_from_library

# These classes extend the basic diagram classes (Object or Edge) with a little bit of custom functionality for ergonomics or ease of use.


class List(Object):
    def __init__(self, title="List", list_items=[], **kwargs):
        """The List object wraps the basic Object type but allows easier managing of a list object and its members. All of the arguments and keyword arguments for Object are available here as well.

        Args:
            title (str, optional): The name in the heading of the list. Defaults to "List".
            list_items (list of strings, optional): A Python list of strings denoting the items. Defaults to empty.
        """
        super().__init__(value=title, **kwargs)
        self.format_as_library_object(library="general", obj_name="list")
        self.autosizing = kwargs.get("autosizing", True)
        self.width = kwargs.get("width", 120)
        self.list_items = list_items

    @property
    def list_items(self):
        """A Python list of strings of the objects in the list.

        Returns:
            list of strings: The list items
        """
        return [child.value for child in self.children]
    
    @list_items.setter
    def list_items(self, value):
        if not isinstance(value, list):
            raise TypeError("list_items must be a list!")
        self.children = []
        for item in value:
            self.add_item(item)
    
    def add_item(self, item_text):
        """This function creates a new Draw.io text item and adds it to the end of the list.

        Args:
            item_text (string): The name of the item to add.
        """
        new_item = object_from_library(
            library="general", obj_name="list_item", page=self.page
        )
        new_item.value = item_text
        new_item.parent = self
        new_item.width = self.width
        new_item.geometry.y = len(self.list_items) * new_item.height
        if self.autosizing:
            self.autosize()

    def remove_item(self, item_text):
        """This function removes any list items matching the text passed into the function.

        Args:
            item_text (string): The text of the list item to remove.
        """
        for child in self.children:
            if child.value == item_text:
                self.remove_object(child)
                self.page.remove_object(child)
                del child
        if self.autosizing:
            self.autosize()

    def autosize(self):
        """This function resizes the parent List object to match the length of the list of items. It also restacks the list items to fill any gaps from deleted items.
        """
        y_pos = self.startSize
        for child in self.children:
            child.geometry.y = y_pos
            y_pos = y_pos + child.height
        self.height = self.startSize + sum(child.height for child in self.children)
        self.width = min(child.width for child in self.children)

    @property
    def width(self):
        """The width of the object. The difference between List's width and Object's width is that when the List.width is set all of the child objects will be set to the same width.

        Returns:
            _type_: _description_
        """
        return self.geometry.width
    
    @width.setter
    def width(self, value):
        for child in self.children:
            child.width = value
        self.geometry.width = value
        self.update_parent()
        
