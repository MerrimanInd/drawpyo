from ..file import File
from ..page import Page
from ..diagram.objects import Object, Group
from ..diagram.edges import Edge


class NodeObject(Object):
    """This class defines one of the nodes on a tree graph. It inherits from Object and performs the same in most regards. It also tracks the tree-specific parameters like the tree, children, parent, etc."""

    def __init__(self, tree=None, **kwargs):
        """The NodeObject should be instantiated with an owning tree object. A NodeObject can only have a single parent but can have any number of children.

        Args:
            tree (TreeDiagram, optional): The owning tree diagram. Defaults to None.

        Keyword Args:
            children (list, optional): A list of other NodeObjects
            parent (list, optional): The parent NodeObject
        """
        super().__init__(**kwargs)
        self.tree = tree
        self.children = kwargs.get("children", [])
        self.parent = kwargs.get("parent", None)
        self.peers = []
        # self.level = kwargs.get("level", None)
        # self.peers = kwargs.get("peers", [])

    @property
    def tree(self):
        """The TreeDiagram that owns the NodeObject

        Returns:
            TreeDiagram
        """
        return self._tree

    @tree.setter
    def tree(self, value):
        if value is not None:
            value.add_object(self)
        self._tree = value

    @property
    def parent(self):
        """The parent NodeObject

        Returns:
            NodeObject
        """
        return self._parent

    @parent.setter
    def parent(self, value):
        if value is not None:
            value.children.append(self)
        self._parent = value

    def add_child(self, obj):
        """Add a new child to the object

        Args:
            obj (NodeObject)
        """
        self.children.append(obj)
        obj._parent = self

    def add_peer(self, obj):
        if obj not in self.peers:
            self.peers.append(obj)
        if self not in obj.peers:
            obj.peers.append(self)

    @property
    def size_of_level(self):
        """The height or the width of the level, depending on tree orientation.

        Returns:
            int
        """
        if self.tree is not None:
            if self.tree.direction in ["up", "down"]:
                return self.geometry.height
            elif self.tree.direction in ["left", "right"]:
                return self.geometry.width

    @property
    def size_in_level(self):
        """The size of the object within its level, either its width or height depending on tree orientation.

        Returns:
            int
        """
        if self.tree is not None:
            if self.tree.direction in ["up", "down"]:
                return self.geometry.width
            elif self.tree.direction in ["left", "right"]:
                return self.geometry.height


class TreeGroup(Group):
    """This class defines a group within a TreeDiagram. When a set of NodeObjects share the same parent they're grouped together for auto positioning. Each level of a TreeDiagram is a set of groups."""

    def __init__(self, tree=None, parent_object=None, **kwargs):
        """The TreeGroup is instantiated with all the arguments of the Group. Additionally, the owning tree and the parent_object.

        Args:
            tree (TreeDiagram, optional): The TreeDiagram that owns the group. Defaults to None.
            parent_object (NodeObject, optional): The parent object in the group. Defaults to None.
        """
        super().__init__(**kwargs)
        self.parent_object = parent_object
        self.tree = tree

    @property
    def parent_object(self):
        """The object that defines the parent of the group.

        Returns:
            NodeObject
        """
        return self._parent_object

    @parent_object.setter
    def parent_object(self, value):
        if value is not None:
            self.add_object(value)
        self._parent_object = value

    def center_parent(self):
        """This function centers the parent_objects along the group and then offsets it by the level spacing."""
        children_grp = TreeGroup(tree=self.tree)
        for obj in self.objects:
            if obj is not self.parent_object:
                children_grp.add_object(obj)
        pos = children_grp.center_position

        level_space = (
            children_grp.size_of_level / 2
            + self.tree.level_spacing
            + self.parent_object.size_of_level / 2
        )
        pos = self.tree.move_between_levels(pos, -level_space)
        self.parent_object.center_position = pos

    # I don't love that these are copy-pasted from NodeObject but the multiple
    # inheritance was too much of a pain to have TreeGroup inherit.
    @property
    def size_of_level(self):
        """The height or the width of the level, depending on tree orientation.

        Returns:
            int
        """
        if self.tree is not None:
            if self.tree.direction in ["up", "down"]:
                return self.height
            elif self.tree.direction in ["left", "right"]:
                return self.width

    @property
    def size_in_level(self):
        """The size of the object within its level, either its width or height depending on tree orientation.

        Returns:
            int
        """
        if self.tree is not None:
            if self.tree.direction in ["up", "down"]:
                return self.width
            elif self.tree.direction in ["left", "right"]:
                return self.height


class TreeDiagram:
    """The TreeDiagram contains a File object, a Page object, and all the NodeObjects in the tree."""

    def __init__(self, **kwargs):
        """The TreeDiagram initiates its own File and Page objects. There are a number of formatting parameters that can be set to fine tune the rendering of the tree.

        Keyword Args:
            direction (str, optional): Direction that the tree grows from the root. Options are 'up', 'down', 'left', and 'right'. Defaults to 'down'.
            link_style (str, optional): Connection style of the edges. Options are 'orthogonal', 'straight', and 'curved'. Defaults to 'orthogonal'.
            level_spacing (int, optional): Spacing in pixels between levels. Defaults to 60.
            item_spacing (int, optional): Spacing in pixels between groups within a level. Defaults to 15.
            padding (int, optional): Spacing in pixels between objects within a group. Defaults to 10.
            file_name (str, optional): The name of the tree diagram.
            file_path (str, optional): The path where the tree diagram should be saved.
        """
        # formatting
        self.level_spacing = kwargs.get("level_spacing", 60)
        self.item_spacing = kwargs.get("item_spacing", 15)
        self.group_spacing = kwargs.get("group_spacing", 30)
        self.direction = kwargs.get("direction", "down")
        self.link_style = kwargs.get("link_style", "orthogonal")
        self.padding = kwargs.get("padding", 10)

        # Set up the File and Page objects
        self.file = File()
        self.file_name = kwargs.get("file_name", "Heirarchical Diagram.drawio")
        self.file_path = kwargs.get("file_path", r"C:/")
        self.page = Page(file=self.file)

        # Set up object and level lists
        self.objects = []
        self.links = []

    ###########################################################
    # properties
    ###########################################################
    # These setters and getters keep the file name and file path within the
    # File object
    @property
    def file_name(self):
        """The file name of the TreeDiagram

        Returns:
            str
        """
        return self.file.file_name

    @file_name.setter
    def file_name(self, fn):
        self.file.file_name = fn

    @property
    def file_path(self):
        """The file path where the TreeDiagram will be saved

        Returns:
            str
        """
        return self.file.file_path

    @file_path.setter
    def file_path(self, fn):
        self.file.file_path = fn

    # These setters enforce the options for direction and link_style.
    @property
    def direction(self):
        """The direction the tree diagram should grow. Options are "up", "down", "left", or "right".

        Returns:
            str
        """
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

    ###########################################################
    # Formatting Properties
    ###########################################################

    @property
    def origin(self):
        """The origin points of the TreeDiagram. This is the point where the center of the top level of the TreeDiagram starts from. By default it's set to the top center of an edge of the page. Which edge depends on the direction of the tree diagram.

        Returns:
            tuple: A tuple of ints
        """
        origins = {
            "up": (self.page.width / 2, self.page.height - self.padding),
            "down": (self.page.width / 2, self.padding),
            "right": (self.padding, self.page.height / 2),
            "left": (self.page.width - self.padding, self.page.height / 2),
        }
        return origins[self.direction]

    def level_move(self, move):
        """The functions takes in a relative distance to move within levels. It outputs a tuple with the relative move in the correct direction (horizontal or vertical) depending on the direction of the tree diagram.

        Args:
            move (int): The amount to move within levels

        Returns:
            tuple: A tuple containing a 0 and the move, in the right orientation.
        """
        if self.direction in ["up", "down"]:
            return (0, move)
        elif self.direction in ["left", "right"]:
            return (move, 0)

    def move_between_levels(self, start, move):
        """The functions takes in a starting position and a relative distance to move between levels. It outputs a tuple with the final absolute position in the correct direction (horizontal or vertical) depending on the direction of the tree diagram.

        Args:
            start (tuple): The starting position, a tuple of ints
            move (int): The direction to move between levels.

        Raises:
            ValueError: "No direction defined!"

        Returns:
            tuple: The final position, a tuple of ints
        """
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
        """The functions takes in a starting position and a relative distance to move within a level. It outputs a tuple with the final absolute position in the correct direction (horizontal or vertical) depending on the direction of the tree diagram.

        Args:
            start (tuple): The starting position, a tuple of ints
            move (int): The direction to move between levels.

        Raises:
            ValueError: "No direction defined!"

        Returns:
            tuple: The final position, a tuple of ints
        """
        if self.direction in ["up", "down"]:
            return (start[0] + move, start[1])
        elif self.direction in ["left", "right"]:
            return (start[0], start[1] + move)
        else:
            raise ValueError("No direction defined!")

    def abs_move_between_levels(self, start, position):
        """The functions takes in a starting position and an absolute position along the coordinates between levels. It outputs a tuple with the final absolute position in the correct direction (horizontal or vertical) depending on the direction of the tree diagram.

        Args:
            start (tuple): The starting position, a tuple of ints
            move (int): The direction to move between levels.

        Raises:
            ValueError: "No direction defined!"

        Returns:
            tuple: The final position, a tuple of ints
        """
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
        """The functions takes in a starting position and an absolute position along the coordinates within a level. It outputs a tuple with the final absolute position in the correct direction (horizontal or vertical) depending on the direction of the tree diagram.

        Args:
            start (tuple): The starting position, a tuple of ints
            move (int): The direction to move between levels.

        Raises:
            ValueError: "No direction defined!"

        Returns:
            tuple: The final position, a tuple of ints
        """
        if self.direction in ["up", "down"]:
            return (position, start[1])
        elif self.direction in ["left", "right"]:
            return (start[0], position)
        else:
            raise ValueError("No direction defined!")

    ###########################################################
    # Style Properties
    ###########################################################

    @property
    def link_style(self):
        """The style of the links in the TreeDiagram

        Returns:
            str
        """
        return self._link_style

    @link_style.setter
    def link_style(self, d):
        link_styles = ["orthogonal", "straight", "curved"]
        if d in link_styles:
            self._link_style = d
        else:
            raise ValueError(
                "{0} is not a valid entry for link_style. Must be {1}.".format(
                    d, ", ".join(link_styles)
                )
            )

    @property
    def link_style_dict(self):
        """Returns the correct waypoint style for the set link_style

        Returns:
            dict: A dict with 'waypoint' as a key then the set link_style
        """
        if self.link_style == "orthogonal":
            return {"waypoints": "orthogonal"}
        elif self.link_style == "straight":
            return {"waypoints": "straight"}
        elif self.link_style == "curved":
            return {"waypoints": "curved"}

    ###########################################################
    # Object Linking and Sorting
    ###########################################################

    def add_object(self, obj, **kwargs):
        if obj not in self.objects:
            obj.page = self.page
            if "parent" in kwargs:
                obj.parent = kwargs.get("parent")
            self.objects.append(obj)

    ###########################################################
    # Layout and Output
    ###########################################################

    @property
    def roots(self):
        return [x for x in self.objects if x.parent is None]

    def auto_layout(self):
        def layout_child(parent):
            grp = TreeGroup(tree=self)
            grp.parent_object = parent
            if len(parent.children) > 0:
                # has children, go through each leaf and check its children
                for leaf in parent.children:
                    self.connect(parent, leaf)
                    if len(leaf.children) > 0:
                        # If this leaf has its own children then recursive call
                        grp.add_object(layout_child(leaf))
                    else:
                        grp.add_object(leaf)

                # layout the row
                grp = layout_group(grp)
                # grp = add_parent(grp, parent)
                grp.center_parent()
            return grp

        def layout_group(grp, pos=self.origin):
            pos = self.origin

            for leaf in grp.objects:
                if leaf is not grp.parent_object:
                    leaf.position = pos
                    pos = self.move_in_level(
                        pos, leaf.size_in_level + self.item_spacing
                    )
            return grp

        # def add_parent(grp, parent):
        #     pos = grp.center_position
        #     level_space = (
        #         grp.size_of_level / 2
        #         + self.level_spacing
        #         + parent.size_of_level / 2
        #     )
        #     pos = self.move_between_levels(pos, -level_space)
        #     parent.center_position = pos
        #     # add the parent_object
        #     grp.parent_object = parent
        #     return grp

        top_group = TreeGroup(tree=self)

        for root in self.roots:
            top_group.add_object(layout_child(root))

        if len(top_group.objects) > 0:
            # Position top group
            top_group = layout_group(top_group)
            # Center the top group
            pos = self.origin
            pos = self.move_between_levels(pos, top_group.size_of_level / 2)
            top_group.center_position = pos

        # lastly add peer links
        self.connect_peers()

        return top_group

    def connect_peers(self):
        peer_style = {
            "endArrow": "none",
            "dashed": 1,
            "html": 1,
            "rounded": 0,
            "exitX": 1,
            "exitY": 0.5,
            "exitDx": 0,
            "exitDy": 0,
            "entryX": 0,
            "entryY": 0.5,
            "entryDx": 0,
            "entryDx": 0,
            "edgeStyle": "orthogonalEdgeStyle",
        }
        for obj in self.objects:
            for peer in obj.peers:
                link_exists = False
                for link in self.links:
                    if link.source == obj and link.target == peer:
                        link_exists = True
                    elif link.source == peer and link.target == obj:
                        link_exists = True
                if not link_exists:
                    edge = Edge(page=self.page, source=obj, target=peer)
                    edge.apply_attribute_dict(peer_style)
                    self.links.append(edge)

    def connect(self, source, target):
        edge = Edge(page=self.page, source=source, target=target)
        edge.apply_attribute_dict(self.link_style_dict)
        if self.direction == "down":
            # parent style
            edge.exitX = 0.5
            edge.exitY = 1
            # child style
            edge.entryX = 0.5
            edge.entryY = 0
        elif self.direction == "up":
            # parent style
            edge.exitX = 0.5
            edge.exitY = 0
            # child style
            edge.entryX = 0.5
            edge.entryY = 1
        elif self.direction == "left":
            # parent style
            edge.exitX = 0
            edge.exitY = 0.5
            # child style
            edge.entryX = 1
            edge.entryY = 0.5
        elif self.direction == "right":
            # parent style
            edge.exitX = 1
            edge.exitY = 0.5
            # child style
            edge.entryX = 0
            edge.entryY = 0.5
        self.links.append(edge)

    def draw_connections(self):
        # Draw connections
        for lvl in self.objects.values():
            for obj in lvl:
                if obj.parent is not None:
                    self.connect(source=obj.parent, target=obj)

    def write(self, **kwargs):
        self.file.write(**kwargs)
