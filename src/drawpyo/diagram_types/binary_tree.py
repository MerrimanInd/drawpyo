from __future__ import annotations

from typing import List, Optional, Dict, Any

from .tree import NodeObject, TreeDiagram
import drawpyo
import hashlib


class BinaryNodeObject(NodeObject):
    """
    NodeObject variant for binary trees exposing `left` and `right` properties
    and enforcing at most two children.
    """

    def __init__(self, tree=None, **kwargs) -> None:
        """
        Initialize a binary node with exactly 2 child slots [left, right].

        If `tree_children` is provided, it is normalized to two elements.
        """
        children: List[Optional[BinaryNodeObject]] = kwargs.get("tree_children", [])

        # Normalize provided list to exactly 2 elements
        if len(children) == 0:
            normalized = [None, None]
        elif len(children) == 1:
            normalized = [children[0], None]
        elif len(children) == 2:
            normalized = children[:]
        else:
            raise ValueError("BinaryNodeObject cannot have more than two children")

        kwargs["tree_children"] = normalized
        super().__init__(tree=tree, **kwargs)

    # ---------------------------------------------------------
    # Private methods
    # ---------------------------------------------------------

    def _ensure_two_slots(self) -> None:
        """Ensure tree_children always has exactly 2 slots."""
        if len(self.tree_children) < 2:
            missing = 2 - len(self.tree_children)
            self.tree_children.extend([None] * missing)
        elif len(self.tree_children) > 2:
            self.tree_children[:] = self.tree_children[:2]

    def _detach_from_old_parent(self, node: NodeObject) -> None:
        """Remove `node` from its old parent's children (if any)."""
        parent = getattr(node, "tree_parent", None)
        if parent is None or parent is self:
            return

        if hasattr(parent, "tree_children"):
            for i, existing in enumerate(parent.tree_children):
                if existing is node:
                    parent.tree_children[i] = None
                    break

        node._tree_parent = None

    def _clear_existing_slot(self, node: NodeObject, target_index: int) -> None:
        """
        If `node` already belongs to this parent in the *other* slot,
        clear the old slot.
        """
        for i, existing in enumerate(self.tree_children):
            if existing is node and i != target_index:
                self.tree_children[i] = None

    def _assign_child(self, index: int, node: Optional[NodeObject]) -> None:
        """
        Handles:
        - Ensuring slot count
        - Clearing old child if assigning None
        - Preventing more than 2 distinct children
        - Correctly detaching and reattaching node
        """
        self._ensure_two_slots()
        existing = self.tree_children[index]

        if node is None:
            if existing is not None:
                self.tree_children[index] = None
                existing._tree_parent = None
            return

        if not node in self.tree_children:
            other = 1 - index
            if (
                self.tree_children[index] is not None
                and self.tree_children[other] is not None
            ):
                raise ValueError("BinaryNodeObject cannot have more than two children")

        self._detach_from_old_parent(node)

        self._clear_existing_slot(node, index)

        self.tree_children[index] = node
        node._tree_parent = self

    # ---------------------------------------------------------
    # Properties and setters
    # ---------------------------------------------------------

    @property
    def left(self) -> Optional[NodeObject]:
        self._ensure_two_slots()
        return self.tree_children[0]

    @left.setter
    def left(self, node: Optional[NodeObject]) -> None:
        self._assign_child(0, node)

    @property
    def right(self) -> Optional[NodeObject]:
        self._ensure_two_slots()
        return self.tree_children[1]

    @right.setter
    def right(self, node: Optional[NodeObject]) -> None:
        self._assign_child(1, node)


class BinaryTreeDiagram(TreeDiagram):
    """Simplifies TreeDiagram for binary-tree convenience."""

    DEFAULT_LEVEL_SPACING = 80
    DEFAULT_ITEM_SPACING = 20
    DEFAULT_GROUP_SPACING = 30
    DEFAULT_LINK_STYLE = "straight"

    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("level_spacing", self.DEFAULT_LEVEL_SPACING)
        kwargs.setdefault("item_spacing", self.DEFAULT_ITEM_SPACING)
        kwargs.setdefault("group_spacing", self.DEFAULT_GROUP_SPACING)
        kwargs.setdefault("link_style", self.DEFAULT_LINK_STYLE)
        super().__init__(**kwargs)

    def _attach(
        self, parent: BinaryNodeObject, child: BinaryNodeObject, side: str
    ) -> None:
        if not isinstance(parent, BinaryNodeObject) or not isinstance(
            child, BinaryNodeObject
        ):
            raise TypeError("parent and child must be BinaryNodeObject instances")

        if parent.tree is not self:
            parent.tree = self
        child.tree = self

        setattr(parent, side, child)

    def add_left(self, parent: BinaryNodeObject, child: BinaryNodeObject) -> None:
        self._attach(parent, child, "left")

    def add_right(self, parent: BinaryNodeObject, child: BinaryNodeObject) -> None:
        self._attach(parent, child, "right")

    @classmethod
    def from_dict(
        cls,
        data: dict,
        *,
        colors: list = None,
        coloring: str = "depth",
        **kwargs,
    ) -> "BinaryTreeDiagram":
        """
        Build a BinaryTreeDiagram from nested dict/list structures.
        data: Nested dict/list structure representing the tree.
        colors: List of ColorSchemes, StandardColors, or color hex strings to use for coloring nodes. Default: None
        coloring: str - "depth" | "hash" | "type" | "directional" - Method to match colors to nodes. Default: "depth"
            1. "depth" - Color nodes based on their depth in the tree.
            2. "hash" - Color nodes based on a hash of their value.
            3. "type" - Color nodes based on their type (category, list_item, leaf).
            4. "directional" - Color nodes based on their direction (left, right).

            Note: In colors Left Nodes are coloured by 0th index and Right Nodes are coloured by 1st index in the list of colors.
        """

        if coloring not in {"depth", "hash", "type", "directional"}:
            raise ValueError(f"Invalid coloring mode: {coloring}")

        if colors is not None and not isinstance(colors, list):
            raise TypeError("colors must be a list or None")

        colors = colors or None
        TYPE_INDEX = {"category": 0, "list_item": 1, "leaf": 2}

        # -------------------------
        # Validation
        # -------------------------

        def validate(tree_node: Dict, *, is_root=False):
            if tree_node is None or isinstance(tree_node, (str, int, float)):
                return

            if isinstance(tree_node, (list, tuple)):
                if len(tree_node) > 2:
                    raise TypeError("List node can have at most two children")
                for x in tree_node:
                    validate(x)
                return

            if isinstance(tree_node, dict):
                if is_root and len(tree_node) != 1:
                    raise TypeError("Root dict must contain exactly one key")

                if not is_root and not (1 <= len(tree_node) <= 2):
                    raise TypeError("Dict node must have 1 or 2 children")

                for node, children in tree_node.items():
                    if not isinstance(node, (str, int, float)):
                        raise TypeError(f"Invalid dict key type: {type(node)}")

                    validate(children)
                return

            raise TypeError(f"Unsupported tree tree_node type: {type(tree_node)}")

        if not isinstance(data, dict):
            raise TypeError("Top-level tree must be a dict")

        # Checks if the provided dict data is valid for a binary tree construction
        validate(data, is_root=True)

        # -------------------------
        # Helpers
        # -------------------------

        diagram = cls(**kwargs)

        def choose_color(
            value: str, node_type: str, depth: int, side: Optional[object] = None
        ):
            if not colors:
                return None

            n = len(colors)

            if coloring == "depth":
                idx = depth % n
            elif coloring == "hash":
                h = int(hashlib.md5(value.encode()).hexdigest(), 16)
                idx = h % n
            elif coloring == "directional":
                # side can be 'left'/'right' or a boolean where True==left
                if n != 2:
                    raise ValueError(
                        "colors list must be of length atleast 2 for directional coloring"
                    )

                if side is None:
                    return None

                if isinstance(side, bool):
                    is_left = side
                else:
                    is_left = str(side).lower() == "left"

                idx = (0 if is_left else 1) % n

            else:  # type
                idx = TYPE_INDEX[node_type] % n

            return colors[idx]

        def create_node(value: str, parent, color):
            if color is None:
                return BinaryNodeObject(tree=diagram, value=value, tree_parent=parent)

            if isinstance(color, drawpyo.ColorScheme):
                return BinaryNodeObject(
                    tree=diagram, value=value, tree_parent=parent, color_scheme=color
                )

            return BinaryNodeObject(
                tree=diagram, value=value, tree_parent=parent, fillColor=color
            )

        # -------------------------
        # Build
        # -------------------------

        def build(parent: BinaryNodeObject, item: Any, depth: int):
            if item is None:
                return

            # Leaf
            if isinstance(item, (str, int, float)):
                value = str(item)
                # leaf nodes in this branch are always attached as left
                node = create_node(
                    value,
                    parent,
                    choose_color(value, "leaf", depth, side="left"),
                )
                diagram.add_left(parent, node)
                return

            # Dict (named children)
            if isinstance(item, dict):
                for index, (node, children) in enumerate(item.items()):
                    name = str(node)
                    side = "left" if index == 0 else "right"
                    node = create_node(
                        name,
                        parent,
                        choose_color(name, "category", depth, side=side),
                    )

                    if index == 0:
                        diagram.add_left(parent, node)
                    else:
                        diagram.add_right(parent, node)

                    build(node, children, depth + 1)
                return

            # List / Tuple (positional children)
            for index, elem in enumerate(item):
                if elem is None:
                    continue

                if isinstance(elem, (str, int, float)):
                    name = str(elem)
                    side = "left" if index == 0 else "right"
                    node = create_node(
                        name,
                        parent,
                        choose_color(name, "leaf", depth + 1, side=side),
                    )

                elif isinstance(elem, dict) and len(elem) == 1:
                    node, children = next(iter(elem.items()))
                    name = str(node)
                    side = "left" if index == 0 else "right"
                    node = create_node(
                        name,
                        parent,
                        choose_color(name, "category", depth + 1, side=side),
                    )
                    build(node, children, depth + 1)
                else:
                    raise TypeError(
                        "List elements must be primitive or single-key dict"
                    )

                if index == 0:
                    diagram.add_left(parent, node)
                else:
                    diagram.add_right(parent, node)

        # -------------------------
        # Root
        # -------------------------

        root_key, root_value = next(iter(data.items()))
        root_name = str(root_key)

        root = create_node(
            root_name,
            None,
            choose_color(root_name, "category", 0, None),
        )

        build(root, root_value, depth=1)
        diagram.auto_layout()
        return diagram
