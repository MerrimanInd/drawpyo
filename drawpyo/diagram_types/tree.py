from ..file import File
from ..page import Page
from ..diagram.objects import BasicObject, Group
from ..diagram.edges import BasicEdge


class LeafObject(BasicObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tree = kwargs.get("tree", None)
        self.branches = kwargs.get("branches", [])
        self.trunk = kwargs.get("trunk", None)
        self.level = kwargs.get("level", None)
        self.peers = kwargs.get("peers", [])

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
        
    def add_peer(self, obj):
        if obj not in self.peers:
            self.peers.append(obj)
        if self not in obj.peers:
            obj.peers.append(self)

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


class TreeGroup(Group):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.trunk_object = kwargs.get("trunk_object", None)
        self.tree = kwargs.get("tree", None)

    @property
    def trunk_object(self):
        return self._trunk_object

    @trunk_object.setter
    def trunk_object(self, value):
        if value is not None:
            self.add_object(value)
            self._trunk_object = value


    # I don't love that these are copy-pasted from LeafObject but the multiple
    # inheritance was too much of a pain to have TreeGroup inherit.
    @property
    def size_of_level(self):
        if self.tree is not None:
            if self.tree.direction in ["up", "down"]:
                return self.height
            elif self.tree.direction in ["left", "right"]:
                return self.width

    @property
    def size_in_level(self):
        if self.tree is not None:
            if self.tree.direction in ["up", "down"]:
                return self.width
            elif self.tree.direction in ["left", "right"]:
                return self.height


class TreeDiagram:
    def __init__(self, **kwargs):
        # formatting
        self.level_spacing = kwargs.get("level_spacing", 60)
        self.item_spacing = kwargs.get("item_spacing", 15)
        self.group_spacing = kwargs.get("group_spacing", 30)
        self.direction = kwargs.get("direction", "down")
        self.link_style = kwargs.get("link_style", "ortho")
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
    # Style Properties
    ###########################################################

    @property
    def link_style(self):
        return self._link_style

    @link_style.setter
    def link_style(self, d):
        link_styles = ["ortho", "straight", "curved"]
        if d in link_styles:
            self._link_style = d
        else:
            raise ValueError(
                "{0} is not a valid entry for link_style. Must be {1}.".format(
                    d, ", ".join(link_styles)
                )
            )

    @property
    def link_style_string(self):
        if self.link_style == "ortho":
            return "rounded=0;orthogonalLoop=1;jettySize=auto;edgeStyle=orthogonalEdgeStyle;"
        elif self.link_style == "straight":
            return "rounded=0;orthogonalLoop=1;jettySize=auto;"
        elif self.link_style == "curved":
            return "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;curved=1;"
        
        

    ###########################################################
    # Object Linking and Sorting
    ###########################################################

    def add_object(self, obj, **kwargs):
        if obj not in self.objects:
            obj.page = self.page
            if "trunk" in kwargs:
                obj.trunk = kwargs.get("trunk")
            self.objects.append(obj)

    ###########################################################
    # Layout and Output
    ###########################################################

    @property
    def roots(self):
        return [x for x in self.page.objects[2:] if x.trunk is None]

    def auto_layout(self):
        def layout_branch(trunk):
            grp = TreeGroup(tree=self)
            if len(trunk.branches) > 0:
                # has branches, go through each leaf and check its branches
                for leaf in trunk.branches:
                    self.connect(trunk, leaf)
                    if len(leaf.branches) > 0:
                        # If this leaf has its own branches then recursive call
                        grp.add_object(layout_branch(leaf))
                    else:
                        grp.add_object(leaf)

                # layout the row
                # top align
                if len(grp.objects) > 0:
                    grp = layout_group(grp)
                    grp = add_trunk(grp, trunk)
                    
            return grp
        
        def layout_group(grp, pos=self.origin):
            pos = self.origin

            for leaf in grp.objects:
                leaf.position = pos
                pos = self.move_in_level(
                    pos, leaf.size_in_level + self.item_spacing
                )
            return grp
        
        def add_trunk(grp, trunk):
            pos = grp.center_position
            level_space = (
                grp.size_of_level / 2
                + self.level_spacing
                + trunk.size_of_level / 2
            )
            pos = self.move_between_levels(pos, -level_space)
            trunk.center_position = pos
            # add the trunk_object
            grp.trunk_object = trunk
            return grp
        
        top_group = TreeGroup(tree=self)
        
        for root in self.roots:
            top_group.add_object(layout_branch(root))
        
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
        peer_style = "endArrow=none;dashed=1;html=1;rounded=0;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;edgeStyle=orthogonalEdgeStyle;"
        for obj in self.objects:
            for peer in obj.peers:
                link_exists = False
                for link in self.links:
                    if link.source == obj and link.target == peer:
                        link_exists = True
                    elif link.source == peer and link.target == obj:
                        link_exists = True
                if not link_exists:
                    edge = BasicEdge(page=self.page, source=obj, target=peer)
                    edge.extra_styles = peer_style
                    self.links.append(edge)

    def connect(self, source, target):
        edge = BasicEdge(page=self.page, source=source, target=target, style=self.link_style_string)
        if self.direction == "down":
            trunk_style = "exitX=0.5;exitY=1;exitDx=0;exitDy=0;"
            branch_style = "entryX=0.5;entryY=0;entryDx=0;entryDy=0;"
        elif self.direction == "up":
            trunk_style = "exitX=0.5;exitY=0;exitDx=0;exitDy=0;"
            branch_style = "entryX=0.5;entryY=1;entryDx=0;entryDy=0;"
        elif self.direction == "left":
            trunk_style = "exitX=0;exitY=0.5;exitDx=0;exitDy=0;"
            branch_style = "entryX=1;entryY=0.5;entryDx=0;entryDy=0;"
        elif self.direction == "right":
            trunk_style = "exitX=1;exitY=0.5;exitDx=0;exitDy=0;"
            branch_style = "entryX=0;entryY=0.5;entryDx=0;entryDy=0;"
        edge.extra_styles = edge.style + trunk_style + branch_style
        self.links.append(edge)

    def draw_connections(self):
        # Draw connections
        for lvl in self.objects.values():
            for obj in lvl:
                if obj.trunk is not None:
                    self.connect(source=obj.trunk, target=obj)

    def write(self, **kwargs):
        self.file.write(**kwargs)
