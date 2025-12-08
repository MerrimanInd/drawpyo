from __future__ import annotations

from typing import List, Optional, Tuple, Dict, Any

import hashlib
from ..file import File
from ..page import Page
from ..diagram.objects import Object, Group
from ..diagram.edges import Edge
import drawpyo


class NodeObject(Object):
    """This class defines one of the nodes on a tree graph. It inherits from Object and performs the same in most regards. It also tracks the tree-specific parameters like the tree, children, parent, etc."""

    def __init__(self, tree=None, **kwargs) -> None:
        """The NodeObject should be instantiated with an owning tree object. A NodeObject can only have a single parent but can have any number of children.
        Args:
            tree (TreeDiagram, optional): The owning tree diagram. Defaults to None.

        Keyword Args:
            tree_children (list, optional): A list of other NodeObjects
            parent (list, optional): The parent NodeObject
        """
        super().__init__(**kwargs)
        self.tree: Optional[TreeDiagram] = tree
        self.tree_children: List[NodeObject] = kwargs.get("tree_children", [])
        self.tree_parent: Optional[NodeObject] = kwargs.get("tree_parent", None)
        self.peers: List[NodeObject] = []
        # self.level = kwargs.get("level", None)
        # self.peers = kwargs.get("peers", [])

    @property
    def tree(self) -> TreeDiagram:
        """The TreeDiagram that owns the NodeObject

        Returns:
            TreeDiagram
        """
        return self._tree

    @tree.setter
    def tree(self, value: Optional[TreeDiagram]) -> None:
        if value is not None:
            value.add_object(self)
        self._tree = value

    @property
    def tree_parent(self) -> Optional[NodeObject]:
        """The parent NodeObject in the tree

        Returns:
            NodeObject
        """
        return self._tree_parent

    @tree_parent.setter
    def tree_parent(self, value: Optional[NodeObject]) -> None:
        if value is not None:
            value.tree_children.append(self)
        self._tree_parent = value

    def add_child(self, obj: NodeObject) -> None:
        """Add a new child to the object

        Args:
            obj (NodeObject)
        """
        self.tree_children.append(obj)
        obj._tree_parent = self

    def add_peer(self, obj: NodeObject) -> None:
        if obj not in self.peers:
            self.peers.append(obj)
        if self not in obj.peers:
            obj.peers.append(self)

    @property
    def size_of_level(self) -> Optional[int]:
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
    def size_in_level(self) -> Optional[int]:
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

    def __init__(self, tree=None, parent_object=None, **kwargs) -> None:
        """The TreeGroup is instantiated with all the arguments of the Group. Additionally, the owning tree and the parent_object.

        Args:
            tree (TreeDiagram, optional): The TreeDiagram that owns the group. Defaults to None.
            parent_object (NodeObject, optional): The parent object in the group. Defaults to None.
        """
        super().__init__(**kwargs)
        self.tree: Optional[TreeDiagram] = tree
        self.parent_object: Optional[NodeObject] = parent_object

    @property
    def parent_object(self) -> Optional[NodeObject]:
        """The object that defines the parent of the group.

        Returns:
            NodeObject
        """
        return self._parent_object

    @parent_object.setter
    def parent_object(self, value: Optional[NodeObject]) -> None:
        if value is not None:
            self.add_object(value)
        self._parent_object = value

    def center_parent(self) -> None:
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
    def size_of_level(self) -> Optional[int]:
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
    def size_in_level(self) -> Optional[int]:
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

    def __init__(self, **kwargs) -> None:
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
        self.level_spacing: int = kwargs.get("level_spacing", 60)
        self.item_spacing: int = kwargs.get("item_spacing", 15)
        self.group_spacing: int = kwargs.get("group_spacing", 30)
        self.direction: str = kwargs.get("direction", "down")
        self.link_style: str = kwargs.get("link_style", "orthogonal")
        self.padding: int = kwargs.get("padding", 10)

        # Set up the File and Page objects
        self.file: File = File()
        self.file_name: str = kwargs.get("file_name", "Heirarchical Diagram.drawio")
        self.file_path: str = kwargs.get("file_path", r"C:/")
        self.page: Page = Page(file=self.file)

        # Set up object and level lists
        self.objects: List[NodeObject] = []
        self.links: List[Edge] = []

    ###########################################################
    # Properties
    ###########################################################
    # These setters and getters keep the file name and file path within the
    # File object
    @property
    def file_name(self) -> str:
        """The file name of the TreeDiagram

        Returns:
            str
        """
        return self.file.file_name

    @file_name.setter
    def file_name(self, fn: str) -> None:
        self.file.file_name = fn

    @property
    def file_path(self) -> str:
        """The file path where the TreeDiagram will be saved

        Returns:
            str
        """
        return self.file.file_path

    @file_path.setter
    def file_path(self, fn: str) -> None:
        self.file.file_path = fn

    # These setters enforce the options for direction and link_style.
    @property
    def direction(self) -> str:
        """The direction the tree diagram should grow. Options are "up", "down", "left", or "right".

        Returns:
            str
        """
        return self._direction

    @direction.setter
    def direction(self, d: str) -> None:
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
    def origin(self) -> Tuple[float, float]:
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

    def level_move(self, move: int) -> Tuple[int, int]:
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

    def move_between_levels(self, start: Tuple[int, int], move: int) -> Tuple[int, int]:
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

    def move_in_level(self, start: Tuple[int, int], move: int) -> Tuple[int, int]:
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

    def abs_move_between_levels(
        self, start: Tuple[int, int], position: Tuple[int, int]
    ) -> Tuple[int, int]:
        """The functions takes in a starting position and an absolute position along the coordinates between levels. It outputs a tuple with the final absolute position in the correct direction (horizontal or vertical) depending on the direction of the tree diagram.

        Args:
            start (tuple): The starting position, a tuple of ints
            position (tuple): The absolute position to move between levels, a tuple of ints

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

    def abs_move_in_level(
        self, start: Tuple[int, int], position: Tuple[int, int]
    ) -> Tuple[int, int]:
        """The functions takes in a starting position and an absolute position along the coordinates within a level. It outputs a tuple with the final absolute position in the correct direction (horizontal or vertical) depending on the direction of the tree diagram.

        Args:
            start (tuple): The starting position, a tuple of ints
            position (tuple): The absolute position to move within a levels, a tuple of ints

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
    def link_style(self) -> str:
        """The style of the links in the TreeDiagram

        Returns:
            str
        """
        return self._link_style

    @link_style.setter
    def link_style(self, d: str) -> None:
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
    def link_style_dict(self) -> Dict[str, str]:
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

    def add_object(self, obj: NodeObject, **kwargs: Any) -> None:
        if obj not in self.objects:
            obj.page = self.page
            if "tree_parent" in kwargs:
                obj.tree_parent = kwargs.get("tree_parent")
            self.objects.append(obj)

    ###########################################################
    # Creating from dict
    ###########################################################

    @classmethod
    def from_dict(
        cls,
        data: dict,
        *,
        colors: list = None,
        coloring: str = "depth",
        **diagram_kwargs,
    ) -> "TreeDiagram":
        """
        Build a TreeDiagram from nested dict/list structures.
        data: Nested dict/list structure representing the tree.
        colors: List of ColorSchemes, StandardColors, or color hex strings to use for coloring nodes. Default: None
        coloring: str - "depth" | "hash" | "type" - Method to match colors to nodes. Default: "depth"
            1. "depth" - Color nodes based on their depth in the tree.
            2. "hash" - Color nodes based on a hash of their value.
            3. "type" - Color nodes based on their type (category, list_item, leaf).
        """

        diagram = cls(**diagram_kwargs)

        TYPE_INDEX = {"category": 0, "list_item": 1, "leaf": 2}

        if coloring not in ("depth", "hash", "type"):
            raise ValueError(f"Invalid coloring mode: {coloring}")

        if colors is not None and not isinstance(colors, list):
            raise TypeError("colors must be a list or None")
        if colors == []:
            colors = None

        def choose_color(value: str, node_type: str, depth: int):
            """Return a color from the palette based on mode."""
            if not colors:
                return None

            n = len(colors)

            if coloring == "depth":
                index = depth % n
            elif coloring == "hash":
                # Stable hash using md5
                h = int(hashlib.md5(value.encode("utf-8")).hexdigest(), 16)
                index = h % n
            elif coloring == "type":
                index = TYPE_INDEX[node_type] % n

            return colors[index]

        def create_node(tree, value, parent, color):
            """Create NodeObject with proper color argument."""
            if color is None:
                return NodeObject(tree=tree, value=value, tree_parent=parent)

            if isinstance(color, drawpyo.ColorScheme):
                return NodeObject(
                    tree=tree, value=value, tree_parent=parent, color_scheme=color
                )
            elif isinstance(color, (drawpyo.StandardColor, str)):
                return NodeObject(
                    tree=tree, value=value, tree_parent=parent, fillColor=color
                )
            else:
                raise TypeError(f"Unsupported color type: {type(color)}")

        def build(parent: Optional[NodeObject], item, depth: int):
            """Recursively build tree nodes."""

            # LEAF NODE
            if isinstance(item, (str, int, float)):
                value = str(item)
                color = choose_color(value, "leaf", depth)
                create_node(diagram, value, parent, color)
                return

            # CATEGORY NODE (dict)
            if isinstance(item, dict):
                for key, value in item.items():
                    if not isinstance(key, (str, int, float)):
                        raise TypeError(f"Invalid dict key type: {type(key)}")

                    key_str = str(key)
                    color = choose_color(key_str, "category", depth)
                    node = create_node(diagram, key_str, parent, color)
                    build(node, value, depth + 1)
                return

            # LIST / TUPLE NODES
            if isinstance(item, (list, tuple)):
                for element in item:
                    # list itself does not create a node, elements are siblings
                    build(parent, element, depth)
                return

            raise TypeError(f"Unsupported type in tree data: {type(item)}")

        if not isinstance(data, dict):
            raise TypeError("Top-level tree must be a dict")

        build(None, data, depth=0)

        diagram.auto_layout()
        return diagram

    ###########################################################
    # Layout and Output
    ###########################################################

    @property
    def roots(self) -> List[NodeObject]:
        return [x for x in self.objects if x.tree_parent is None]

    def auto_layout(self) -> TreeGroup:
        def layout_child(tree_parent: Optional[NodeObject]) -> TreeGroup:
            grp = TreeGroup(tree=self)
            grp.parent_object = tree_parent
            # Filter out None children (for BinaryNodeObject compatibility)
            actual_children = [c for c in tree_parent.tree_children if c is not None]
            if len(actual_children) > 0:
                # has children, go through each child and check its children
                for child in actual_children:
                    self.connect(tree_parent, child)
                    child_actual_children = [
                        c for c in child.tree_children if c is not None
                    ]
                    if len(child_actual_children) > 0:
                        # If this child has its own children then recursive call
                        grp.add_object(layout_child(child))
                    else:
                        grp.add_object(child)

                # layout the row
                grp = layout_group(grp)
                # grp = add_parent(grp, parent)
                grp.center_parent()
            return grp

        def layout_group(grp: TreeGroup) -> TreeGroup:
            pos = self.origin

            for obj in grp.objects:
                if obj is not grp.parent_object:
                    obj.position = pos
                    pos = self.move_in_level(pos, obj.size_in_level + self.item_spacing)
            return grp

        # def add_parent(grp, parent):
        #     pos = grp.center_position
        #     level_space = (
        #         grp.size_of_level / 2
        #         + self.level_spacing
        #         + tree_parent.size_of_level / 2
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

    def connect_peers(self) -> None:
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

    def connect(self, source: NodeObject, target: NodeObject) -> None:
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

    def draw_connections(self) -> None:
        # Draw connections
        for lvl in self.objects.values():
            for obj in lvl:
                if obj.tree_parent is not None:
                    self.connect(source=obj.tree_parent, target=obj)

    def write(self, **kwargs) -> None:
        self.file.write(**kwargs)
