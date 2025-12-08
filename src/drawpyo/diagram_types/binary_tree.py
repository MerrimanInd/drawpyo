from __future__ import annotations

from typing import List, Optional, Tuple, Dict, Any

from .tree import NodeObject, TreeDiagram


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
