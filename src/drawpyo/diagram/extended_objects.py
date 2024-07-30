from .objects import Object, object_from_library

# These classes extend the basic diagram classes (Object or Edge) with a little bit of custom functionality for ergonomics or ease of use.


class List(Object):
    def __init__(self, title="List", **kwargs):
        super().__init__(value=title, **kwargs)
        self.format_as_library_object(library="general", obj_name="list")
        self.autosizing = kwargs.get("autosizing", True)
        self.width = kwargs.get("width", 120)

    @property
    def list_items(self):
        return self.children

    def add_item(self, item_text):
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
        for child in self.children:
            if child.value == item_text:
                self.remove_object(child)
        if self.autosizing:
            self.autosize()

    def autosize(self):
        self.height = self.startSize + sum(child.height for child in self.children)
        self.width = min(child.width for child in self.children)
