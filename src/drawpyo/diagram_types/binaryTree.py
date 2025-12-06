from __future__ import annotations

from typing import List, Optional, Tuple, Dict, Any

from ..file import File
from ..page import Page
from ..diagram.objects import Object, Group
from ..diagram.edges import Edge

from .tree import NodeObject, TreeDiagram


class BinaryNodeObject(NodeObject):
    """NodeObject variant for binary trees exposing `left` and `right` properties
    and enforcing at most two children.
    """

    @property
    def left(self) -> Optional[NodeObject]:
        """Left child (index 0) or None.

        Returns:
            Optional[NodeObject]: left child or None.
        """
        if len(self.tree_children) >= 1:
            return self.tree_children[0]
        return None

    @left.setter
    def left(self, obj: Optional[NodeObject]) -> None:
        """Set or remove the left child.

        Side effects:
            - Detaches obj from any previous parent and assigns this node as its parent.
            - Inserts obj at index 0 of tree_children.
        Raises:
            ValueError: if the two-child limit would be exceeded.
        """
        # remove existing left if setting to None
        existing = self.left
        if obj is None:
            if existing is not None:
                try:
                    self.tree_children.remove(existing)
                except ValueError:
                    pass
                existing._tree_parent = None
            return

        # detach from previous parent if any
        if getattr(obj, "tree_parent", None) is not None and obj.tree_parent is not self:
            try:
                obj.tree_parent.tree_children.remove(obj)
            except Exception:
                pass
            obj._tree_parent = None

        # ensure we don't exceed two children
        if len(self.tree_children) >= 2 and obj not in self.tree_children:
            raise ValueError("BinaryNodeObject cannot have more than two children")

        # place as left (index 0)
        if existing is obj:
            return

        # if already present elsewhere (as right), move it
        if obj in self.tree_children:
            self.tree_children.remove(obj)

        if len(self.tree_children) == 0:
            self.tree_children.insert(0, obj)
        else:
            # if there's one child, insert at position 0
            self.tree_children.insert(0, obj)

        obj._tree_parent = self

    @property
    def right(self) -> Optional[NodeObject]:
        """Right child (index 1) or None.

        Returns:
            Optional[NodeObject]: right child or None.
        """
        if len(self.tree_children) >= 2:
            return self.tree_children[1]
        elif len(self.tree_children) == 1:
            return None
        return None

    @right.setter
    def right(self, obj: Optional[NodeObject]) -> None:
        """Set or remove the right child.

        Side effects:
            - Detaches obj from any previous parent and assigns this node as its parent.
            - Ensures obj occupies index 1 of tree_children.
        Raises:
            ValueError: if the two-child limit would be exceeded.
        """
        existing = self.right
        if obj is None:
            if existing is not None:
                try:
                    self.tree_children.remove(existing)
                except ValueError:
                    pass
                existing._tree_parent = None
            return

        # detach from previous parent if any
        if getattr(obj, "tree_parent", None) is not None and obj.tree_parent is not self:
            try:
                obj.tree_parent.tree_children.remove(obj)
            except Exception:
                pass
            obj._tree_parent = None

        # ensure we don't exceed two children
        if len(self.tree_children) >= 2 and obj not in self.tree_children:
            raise ValueError("BinaryNodeObject cannot have more than two children")

        # if already present as left, move to right
        if obj in self.tree_children:
            try:
                self.tree_children.remove(obj)
            except ValueError:
                pass

        # ensure list has space for right at index 1
        if len(self.tree_children) == 0:
            # insert a placeholder for left (None by omission) then append
            self.tree_children.append(obj)
        elif len(self.tree_children) == 1:
            self.tree_children.append(obj)
        else:
            # replace existing right
            self.tree_children[1] = obj

        obj._tree_parent = self

    


class BinaryTreeDiagram(TreeDiagram):
    """A simple subclass of TreeDiagram for binary trees.

    - Uses `BinaryNodeObject` for convenience methods.
    - Provides `add_left` / `add_right` helpers and enforces two-child limit.
    - Applies light prestyling defaults.
    """

    def __init__(self, **kwargs) -> None:
        """Initialize with binary-friendly spacing and styling defaults."""
        # apply some prestyling defaults for binary trees
        kwargs.setdefault("level_spacing", 80)
        kwargs.setdefault("item_spacing", 20)
        kwargs.setdefault("group_spacing", 30)
        kwargs.setdefault("link_style", "straight")
        super().__init__(**kwargs)

    def add_left(self, parent: BinaryNodeObject, child: BinaryNodeObject) -> None:
        """Attach child as parent's left within this diagram.

        Ensures both nodes belong to this diagram before linking.

        Raises:
            TypeError: if arguments are not BinaryNodeObject.
            ValueError: if adding the child violates the two-child limit.
        """
        if not isinstance(parent, BinaryNodeObject) or not isinstance(child, BinaryNodeObject):
            raise TypeError("parent and child must be BinaryNodeObject instances")
        # ensure parent is part of this tree
        if parent.tree is not self:
            parent.tree = self
        # attach child to this tree and set as left
        child.tree = self
        parent.left = child

    def add_right(self, parent: BinaryNodeObject, child: BinaryNodeObject) -> None:
        """Attach child as parent's right within this diagram.

        Ensures both nodes belong to this diagram before linking.

        Raises:
            TypeError: if arguments are not BinaryNodeObject.
            ValueError: if adding the child violates the two-child limit.
        """
        if not isinstance(parent, BinaryNodeObject) or not isinstance(child, BinaryNodeObject):
            raise TypeError("parent and child must be BinaryNodeObject instances")
        if parent.tree is not self:
            parent.tree = self
        child.tree = self
        parent.right = child

    # def add_object(self, obj: NodeObject, **kwargs: Any) -> None:  # type: ignore[override]
    #     """Add a node to this diagram (accepts BinaryNodeObject or NodeObject)."""
    #     # ensure BinaryNodeObject is used when desired, but accept NodeObject too
    #     if isinstance(obj, BinaryNodeObject):
    #         super().add_object(obj, **kwargs)
    #     else:
    #         super().add_object(obj, **kwargs)
