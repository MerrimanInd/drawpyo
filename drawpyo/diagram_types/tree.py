from ..file import File
from ..page import Page
from ..diagram.objects import ObjectBase
from ..diagram.edges import EdgeBase


class LeafObject(ObjectBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tree = kwargs.get("tree", None)
        self.branches = kwargs.get("branches", [])
        self.trunk = kwargs.get("trunk", None)
        self.level = kwargs.get("level", None)

    @property
    def tree(self):
        return self._tree

    @tree.setter
    def tree(self, value):
        if value is not None:
            value.add_object(self)
        self._tree = value

    @property
    def trunk(self):
        return self._trunk

    @trunk.setter
    def trunk(self, value):
        if value is not None:
            value.branches.append(self)
        self._trunk = value

    def add_branch(self, obj):
        self.branches.append(obj)
        obj._trunk = self

    @property
    def size_of_level(self):
        if self.tree is not None:
            if self.tree.direction in ["up", "down"]:
                return self.geometry.height
            elif self.tree.direction in ["left", "right"]:
                return self.geometry.width

    @property
    def size_in_level(self):
        if self.tree is not None:
            if self.tree.direction in ["up", "down"]:
                return self.geometry.width
            elif self.tree.direction in ["left", "right"]:
                return self.geometry.height


class TreeDiagram:
    def __init__(self, **kwargs):
        # formatting
        self.level_spacing = kwargs.get("level_spacing", 60)
        self.item_spacing = kwargs.get("item_spacing", 15)
        self.group_spacing = kwargs.get("group_spacing", 30)
        self.direction = kwargs.get("direction", "down")
        self.link_style = kwargs.get("link_style", "right_angle")
        self.padding = kwargs.get("padding", 10)

        # Set up the File and Page objects
        self.file = File()
        self.file_name = kwargs.get("file_name", "Heirarchical Diagram.drawio")
        self.file_path = kwargs.get("file_path", r"C:/")
        self.page = Page(file=self.file)

        # Set up object and level lists
        self.unsorted_objects = []
        self.objects = {0: []}
        self.grouped_objects = {0: {0: []}}
        self.levels = kwargs.get("levels", {})
        self.links = []

    ###########################################################
    # properties
    ###########################################################
    # These setters and getters keep the file name and file path within the
    # File object
    @property
    def file_name(self):
        return self.file.file_name

    @file_name.setter
    def file_name(self, fn):
        self.file.file_name = fn

    @property
    def file_path(self):
        return self.file.file_path

    @file_path.setter
    def file_path(self, fn):
        self.file.file_path = fn

    # These setters enforce the options for direction and link_style.
    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, d):
        directions = ["up", "down", "left", "right"]
        if d in directions:
            self._direction = d
        else:
            raise ValueError(
                "{0} is not a valid entry for direction. Must be {1}.".format(
                    d, ", ".join(directions)
                )
            )

    @property
    def link_style(self):
        return self._link_style

    @link_style.setter
    def link_style(self, d):
        link_styles = ["right_angle", "straight", "curved"]
        if d in link_styles:
            self._link_style = d
        else:
            raise ValueError(
                "{0} is not a valid entry for link_style. Must be {1}.".format(
                    d, ", ".join(link_styles)
                )
            )

    ###########################################################
    # Formatting Properties
    ###########################################################

    @property
    def origin(self):
        origins = {
            "up": (self.page.width / 2, self.page.height - self.padding),
            "down": (self.page.width / 2, self.padding),
            "right": (self.padding, self.page.height / 2),
            "left": (self.page.width - self.padding, self.page.height / 2),
        }
        return origins[self.direction]

    def level_move(self, move):
        if self.direction in ["up", "down"]:
            return (0, move)
        elif self.direction in ["left", "right"]:
            return (move, 0)

    def move_between_levels(self, start, move):
        if self.direction == "up":
            return (start[0], start[1] - move)
        elif self.direction == "down":
            return (start[0], start[1] + move)
        elif self.direction == "left":
            return (start[0] - move, start[1])
        elif self.direction == "right":
            return (start[0] + move, start[1])
        else:
            raise ValueError("No direction defined!")

    def move_in_level(self, start, move):
        if self.direction in ["up", "down"]:
            return (start[0] + move, start[1])
        elif self.direction in ["left", "right"]:
            return (start[0], start[1] + move)
        else:
            raise ValueError("No direction defined!")

    def abs_move_between_levels(self, start, position):
        if self.direction == "up":
            return (start[0], position)
        elif self.direction == "down":
            return (start[0], position)
        elif self.direction == "left":
            return (position, start[1])
        elif self.direction == "right":
            return (position, start[1])
        else:
            raise ValueError("No direction defined!")

    def abs_move_in_level(self, start, position):
        if self.direction in ["up", "down"]:
            return (position, start[1])
        elif self.direction in ["left", "right"]:
            return (start[0], position)
        else:
            raise ValueError("No direction defined!")

    ###########################################################
    # Object Linking and Sorting
    ###########################################################

    def add_object(self, obj, **kwargs):
        obj.page = self.page
        if "trunk" in kwargs:
            obj.trunk = kwargs.get("trunk")

        if "level" in kwargs:
            level = kwargs.get("level")

            if isinstance(level, str):
                if level in self.levels:
                    level = self.levels[level]
                else:
                    raise ValueError(
                        "Level was passed in as a string but isn't present in the TreeDiagram.levels dictionary. Passed in value was {0}.".format(
                            level
                        )
                    )

            obj.level = level

            if level not in self.objects:
                self.objects[level] = []

            self.objects[level].append(obj)
        else:
            self.unsorted_objects.append(obj)

    def add_obj_to_group(self, obj, level, group):
        if level not in self.grouped_objects:
            self.grouped_objects[level] = {}
        if group not in self.grouped_objects[level]:
            self.grouped_objects[level][group] = []
        self.grouped_objects[level][group].append(obj)

    def sort_into_levels(self):
        while len(self.unsorted_objects) > 0:
            max_sort = True
            for obj in self.unsorted_objects:
                trunk_obj = obj.trunk
                if trunk_obj is None:
                    # Top level object
                    lvl = 0
                elif trunk_obj.level is not None:
                    # Has a trunk object and it's sorted
                    lvl = trunk_obj.level + 1
                else:
                    # Has a trunk object but it's not yet sorted
                    lvl = None

                if lvl is not None:
                    max_sort = False
                    obj.level = lvl
                    self.unsorted_objects.remove(obj)
                    self.add_object(obj, level=lvl)
                    # self.objects[lvl].append(obj)
            if max_sort:
                # Condition triggers the first time the program loops through
                # and isn't able to sort any of the remaining objects.
                print(
                    "Maximum sorting achieved. {0} objects are unsortable, examine unsorted_objects.".format(
                        len(self.unsorted_objects)
                    )
                )
                break

    def order_level(self, level):
        trunks = {}
        trunk_order = 0
        for obj in self.objects[level]:
            if obj.trunk not in trunks:
                trunks[obj.trunk] = trunk_order
                trunk_order = trunk_order + 1
            obj.level_order = trunks[obj.trunk]
        self.objects[level].sort(key=lambda x: x.level_order, reverse=True)

    def group_all_levels(self):
        for lvl in self.objects.keys():
            self.group_level(lvl)

    def group_level(self, level):
        # create a dict for matching trunks to groups
        trunks = {}
        group = 0
        for obj in self.objects[level]:
            if obj.trunk not in trunks:
                trunks[obj.trunk] = group
                group = group + 1

            obj.group = trunks[obj.trunk]
            self.add_obj_to_group(obj, level, obj.group)

    ###########################################################
    # Layout and Output
    ###########################################################

    def auto_layout(self):
        # Sort each layer according to parent grouping
        self.sort_into_levels()
        self.group_all_levels()

        # Place objects

        """
        Placement algorithm:
        	• Go to bottom of page
        	• Place bottom group
        	• For each layer:
        		○ Find average position of each group in last layer
        		○ Place root objects at average and one layer up
        Place final block at origin
        """

        lvl_count = len(self.grouped_objects)
        # add spaces between levels
        bottom_depth = (lvl_count - 1) * self.level_spacing

        # add size of levels
        for lvl in range(0, lvl_count, 1):
            bottom_depth = bottom_depth + self.get_height_of_level(lvl)

        # if the direction is left or up the bottom_depth needs to be reduced
        # by one since the location includes the size of a layer
        if self.direction in ["right", "down"]:
            bottom_depth = bottom_depth - self.get_height_of_level(lvl)

        curr_position = self.move_between_levels(self.origin, bottom_depth)
        self.place_grouped_level(curr_position, lvl_count - 1)

        for lvl_num in range(lvl_count - 1, 0, -1):
            # start at the bottom level and work up
            for grp in self.grouped_objects[lvl_num]:
                # Get the avg position of the group
                pos = self.get_avg_pos_of_group(lvl_num, grp)

                # Get the trunk_obj object
                trunk_obj = self.grouped_objects[lvl_num][grp][0].trunk

                # Set the position of the group's trunk_obj object
                pos = self.move_between_levels(
                    pos,
                    -(
                        self.level_spacing
                        + self.get_height_of_level(lvl_num) / 2
                        + trunk_obj.size_of_level / 2
                    ),
                )
                trunk_obj.center_position = pos
        self.draw_connections()

    def draw_connections(self):
        # Draw connections
        for lvl in self.objects.values():
            for obj in lvl:
                if obj.trunk is not None:
                    edge = EdgeBase(
                        page=self.page, source=obj.trunk, target=obj
                    )
                    if self.direction == "down":
                        trunk_style = "exitX=0.5;exitY=1;exitDx=0;exitDy=0;"
                        branch_style = (
                            "entryX=0.5;entryY=0;entryDx=0;entryDy=0;"
                        )
                    elif self.direction == "up":
                        trunk_style = "exitX=0.5;exitY=0;exitDx=0;exitDy=0;"
                        branch_style = (
                            "entryX=0.5;entryY=1;entryDx=0;entryDy=0;"
                        )
                    elif self.direction == "left":
                        trunk_style = "exitX=0;exitY=0.5;exitDx=0;exitDy=0;"
                        branch_style = (
                            "entryX=1;entryY=0.5;entryDx=0;entryDy=0;"
                        )
                    elif self.direction == "right":
                        trunk_style = "exitX=1;exitY=0.5;exitDx=0;exitDy=0;"
                        branch_style = (
                            "entryX=0;entryY=0.5;entryDx=0;entryDy=0;"
                        )

                    edge.style = edge.style + trunk_style + branch_style
                    self.links.append(edge)

    def place_grouped_level(self, origin, level):
        width = self.get_size_of_level(level)

        # Offset to half the total level width then back in to the origin of
        # the first block
        curr_pos = self.move_in_level(origin, -(width / 2))

        for grp in self.grouped_objects[level].values():
            for obj in grp:
                obj.position = curr_pos
                curr_pos = self.move_in_level(
                    curr_pos, self.item_spacing + obj.size_in_level
                )
            curr_pos = self.move_in_level(
                curr_pos, self.group_spacing - self.item_spacing
            )

    def get_avg_pos_of_group(self, level_num, group_num):
        grp = self.grouped_objects[level_num][group_num]
        grp_cnt = len(grp)
        avg_x = sum(obj.center_position[0] for obj in grp) / grp_cnt
        avg_y = sum(obj.center_position[1] for obj in grp) / grp_cnt
        return (avg_x, avg_y)

    def get_height_of_level(self, level_num):
        return max(obj.size_of_level for obj in self.objects[level_num])

    def get_size_of_level(self, level):
        # Add the width of all the spacings between the groups
        total_width = (
            len(self.grouped_objects[level]) - 1
        ) * self.group_spacing
        for grp in self.grouped_objects[level].values():
            # Add the spacing between the objects in the group
            total_width = total_width + (len(grp) - 1) * self.item_spacing
            for obj in grp:
                # Add the width of the objects themselves
                total_width = total_width + obj.size_in_level
        return total_width

    def write(self, **kwargs):
        self.file.write(**kwargs)
