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

    def __init__(self, tree=None, **kwargs) -> None:
        """Initialize a binary node with exactly 2 child slots [left, right].
        
        Each slot can be BinaryNodeObject or None. If tree_children is provided
        in kwargs, it will be normalized to a 2-element list.
        """
        # Get any provided children before calling super()
        provided_children = kwargs.get("tree_children", [])
        
        # Normalize to exactly 2 elements [left, right]
        if len(provided_children) == 0:
            kwargs["tree_children"] = [None, None]
        elif len(provided_children) == 1:
            # Single child defaults to left position
            kwargs["tree_children"] = [provided_children[0], None]
        elif len(provided_children) == 2:
            kwargs["tree_children"] = provided_children[:2]
        else:
            # More than 2 children provided - raise error
            raise ValueError("BinaryNodeObject cannot have more than two children")
        
        super().__init__(tree=tree, **kwargs)

    def _set_child_at_index(
        self, index: int, obj: Optional[NodeObject], side_name: str
    ) -> None:
        """Shared logic for setting a child at a specific index (0=left, 1=right).
        
        Args:
            index: 0 for left, 1 for right
            obj: the child node to set, or None to clear
            side_name: 'left' or 'right' for tracking last assignment
        
        Raises:
            ValueError: if attempting to add a third distinct child when both slots
                        are already occupied.
        """
        # Ensure tree_children is always 2 elements
        while len(self.tree_children) < 2:
            self.tree_children.append(None)
        
        existing = self.tree_children[index]
        
        # Remove existing child if setting to None
        if obj is None:
            if existing is not None:
                self.tree_children[index] = None
                existing._tree_parent = None
            return
        
        # Check if obj is already one of our children (moving between slots is allowed)
        is_already_our_child = obj in self.tree_children
        
        # If we're trying to add a NEW child (not moving an existing one),
        # and both slots are occupied by different nodes, raise error
        if not is_already_our_child:
            other_index = 1 - index  # 0->1, 1->0
            if (self.tree_children[index] is not None and 
                self.tree_children[other_index] is not None):
                raise ValueError("BinaryNodeObject cannot have more than two children")
        
        # Detach from previous parent if any
        if (
            getattr(obj, "tree_parent", None) is not None
            and obj.tree_parent is not self
        ):
            if hasattr(obj.tree_parent, "tree_children"):
                # Remove from old parent's children list
                try:
                    old_parent_children = obj.tree_parent.tree_children
                    if isinstance(old_parent_children, list):
                        for i, child in enumerate(old_parent_children):
                            if child is obj:
                                old_parent_children[i] = None
                                break
                except Exception:
                    pass
            obj._tree_parent = None
        
        # If obj is already one of our children, clear its old position
        for i, child in enumerate(self.tree_children):
            if child is obj and i != index:
                self.tree_children[i] = None
        
        # Set the child at the target index
        self.tree_children[index] = obj
        obj._tree_parent = self

    @property
    def left(self) -> Optional[NodeObject]:
        """Left child (index 0) or None.

        Returns:
            Optional[NodeObject]: left child or None.
        """
        # Ensure list has 2 elements
        while len(self.tree_children) < 2:
            self.tree_children.append(None)
        return self.tree_children[0]

    @left.setter
    def left(self, obj: Optional[NodeObject]) -> None:
        """Set or remove the left child.

        Detaches obj from any previous parent and sets obj._tree_parent = self.
        """
        self._set_child_at_index(0, obj, "left")

    @property
    def right(self) -> Optional[NodeObject]:
        """Right child (index 1) or None.

        Returns:
            Optional[NodeObject]: right child or None.
        """
        # Ensure list has 2 elements
        while len(self.tree_children) < 2:
            self.tree_children.append(None)
        return self.tree_children[1]

    @right.setter
    def right(self, obj: Optional[NodeObject]) -> None:
        """Set or remove the right child.

        Detaches obj from any previous parent and sets obj._tree_parent = self.
        """
        self._set_child_at_index(1, obj, "right")


class BinaryTreeDiagram(TreeDiagram):
    """A simple subclass of TreeDiagram for binary trees.

    - Uses `BinaryNodeObject` for convenience methods.
    - Provides `add_left` / `add_right` helpers and enforces two-child limit.
    - Applies light prestyling defaults.
    """

    # Spacing constants
    DEFAULT_LEVEL_SPACING = 80
    DEFAULT_ITEM_SPACING = 20
    DEFAULT_GROUP_SPACING = 30

    # Styling constants
    DEFAULT_LINK_STYLE = "straight"


    def __init__(self, **kwargs) -> None:
        """Initialize with binary-friendly spacing and styling defaults."""
        # apply some prestyling defaults for binary trees
        kwargs.setdefault("level_spacing", self.DEFAULT_LEVEL_SPACING)
        kwargs.setdefault("item_spacing", self.DEFAULT_ITEM_SPACING)
        kwargs.setdefault("group_spacing", self.DEFAULT_GROUP_SPACING)
        kwargs.setdefault("link_style", self.DEFAULT_LINK_STYLE)
        super().__init__(**kwargs)

    def add_left(self, parent: BinaryNodeObject, child: BinaryNodeObject) -> None:
        """Attach child as parent's left within this diagram.

        Ensures both nodes belong to this diagram before linking.

        Raises:
            TypeError: if arguments are not BinaryNodeObject.
            ValueError: if adding the child violates the two-child limit.
        """
        if not isinstance(parent, BinaryNodeObject) or not isinstance(
            child, BinaryNodeObject
        ):
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
        if not isinstance(parent, BinaryNodeObject) or not isinstance(
            child, BinaryNodeObject
        ):
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
