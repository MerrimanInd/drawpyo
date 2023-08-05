from ..file import File
from ..page import Page
from ..diagram.objects import ObjectBase


class LeafObject(ObjectBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.branches = kwargs.get("branches", [])
        self.trunk = kwargs.get("trunk", None)
        self.level = kwargs.get("level", None)

    @property
    def trunk(self):
        return self._trunk
    @trunk.setter
    def trunk(self, value):
        if value is not None:
            value.branches.append(self)
        self._trunk = value

    # def add_trunk(self, obj):
    #     self.trunk = obj
    #     obj.add_branch(self)

    # def add_branch(self, obj):
    #     self.branches.append(obj)
    #     obj.trunk = self

class TreeDiagram:
    def __init__(self, **kwargs):

        # formatting
        self.level_spacing = kwargs.get("level_spacing", 250)
        self.item_spacing = kwargs.get("item_spacing", 15)
        self.group_spacing = kwargs.get("group_spacing", 30)
        self.direction = kwargs.get("direction", "down")
        self.link_style = kwargs.get("link_style", "right_angle")

        self.file_name = kwargs.get(
            "file_name", "Heirarchical Diagram.drawio"
        )
        self.file_path = kwargs.get(
            "file_path", r"C:/"
        )

        self.file = File(file_name=self.file_name, file_path=self.file_path)
        self.page = Page(file=self.file)

        self.unsorted_objects = []
        self.objects = {0: []}

    # TODO add setters and getters for file_name and file_path

    def add_object(self, obj, **kwargs):

        obj.page = self.page
        if "trunk" in kwargs:
            obj.trunk = kwargs.get("trunk")


        if "level" in kwargs:
            level = kwargs.get("level")
            obj.level = level

            if level not in self.objects:
                self.objects[level] = []

            self.objects[level].append(obj)
        else:
            self.unsorted_objects.append(obj)

    def level_sort(self):
        pass

    def auto_layout(self):
        pass

    def write(self, **kwargs):
        self.file.write(**kwargs)