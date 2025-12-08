import pytest

from drawpyo.diagram_types.binary_tree import BinaryNodeObject, BinaryTreeDiagram


class TestBinaryNodeBasic:
    """Basic BinaryNodeObject property behaviour."""

    def test_left_set_and_remove(self):
        """Setting left assigns child at index 0 and removing clears parent."""
        parent = BinaryNodeObject(value="P")
        child = BinaryNodeObject(value="C")

        parent.left = child
        assert parent.left is child
        assert child._tree_parent is parent
        assert parent.tree_children[0] is child

        # remove left
        parent.left = None
        assert parent.left is None
        assert child._tree_parent is None
        assert child not in parent.tree_children

    def test_right_getter_with_single_child(self):
        """If only one child exists (at left), right property returns None."""
        parent = BinaryNodeObject(value="P")
        left = BinaryNodeObject(value="L")

        parent.left = left
        assert parent.left is left
        assert parent.right is None

    def test_set_same_child_idempotent(self):
        """Setting the same child twice does not duplicate entries."""
        parent = BinaryNodeObject(value="P")
        child = BinaryNodeObject(value="C")

        parent.left = child
        parent.left = child
        assert parent.tree_children.count(child) == 1


class TestBinaryNodeReparenting:
    """Tests for detaching from old parent when reparenting a node."""

    def test_move_child_between_parents_using_properties(self):
        """Assigning a child to a new parent removes it from the old parent's children."""
        p1 = BinaryNodeObject(value="P1")
        p2 = BinaryNodeObject(value="P2")
        child = BinaryNodeObject(value="C")

        p1.left = child
        assert child._tree_parent is p1
        assert child in p1.tree_children

        p2.right = child
        assert child._tree_parent is p2
        assert child in p2.tree_children
        assert child not in p1.tree_children

    def test_move_child_between_parents_using_diagram_helpers(self):
        """add_left/add_right should set child's tree and detach from old parent."""
        bt = BinaryTreeDiagram()
        p1 = BinaryNodeObject(value="P1")
        p2 = BinaryNodeObject(value="P2")
        child = BinaryNodeObject(value="C")

        bt.add_left(p1, child)
        assert child._tree_parent is p1
        assert child.tree is bt

        bt.add_right(p2, child)
        assert child._tree_parent is p2
        assert child.tree is bt
        assert child not in p1.tree_children


class TestBinaryTreeDiagramHelpers:
    """Tests for BinaryTreeDiagram.add_left / add_right and related errors."""

    def test_add_left_and_add_right_assign_tree(self):
        """Helpers should attach nodes to the diagram and set parent links."""
        bt = BinaryTreeDiagram()
        parent = BinaryNodeObject(value="Parent")
        l = BinaryNodeObject(value="L")
        r = BinaryNodeObject(value="R")

        bt.add_left(parent, l)
        bt.add_right(parent, r)

        assert l._tree_parent is parent
        assert r._tree_parent is parent
        assert l.tree is bt
        assert r.tree is bt
        # left at index 0, right at index 1
        assert parent.tree_children[0] is l
        assert parent.tree_children[1] is r

    def test_add_with_incorrect_types_raises(self):
        """Passing non-BinaryNodeObject should raise TypeError."""
        bt = BinaryTreeDiagram()
        with pytest.raises(
            TypeError, match="parent and child must be BinaryNodeObject"
        ):
            bt.add_left(object(), BinaryNodeObject())
        with pytest.raises(
            TypeError, match="parent and child must be BinaryNodeObject"
        ):
            bt.add_right(BinaryNodeObject(), object())

    def test_exceed_two_children_raises_when_adding_third_left(self):
        """Adding a third (distinct) left child should raise and not attach it."""
        bt = BinaryTreeDiagram()
        parent = BinaryNodeObject(value="P")
        c1 = BinaryNodeObject(value="C1")
        c2 = BinaryNodeObject(value="C2")
        c3 = BinaryNodeObject(value="C3")

        bt.add_left(parent, c1)
        bt.add_right(parent, c2)
        with pytest.raises(
            ValueError, match="BinaryNodeObject cannot have more than two children"
        ):
            bt.add_left(parent, c3)
        assert c3._tree_parent is None
        assert c3 not in parent.tree_children

    def test_exceed_two_children_raises_when_adding_third_right(self):
        """Adding a third (distinct) right child should raise and not attach it."""
        bt = BinaryTreeDiagram()
        parent = BinaryNodeObject(value="P")
        c1 = BinaryNodeObject(value="C1")
        c2 = BinaryNodeObject(value="C2")
        c3 = BinaryNodeObject(value="C3")

        bt.add_left(parent, c1)
        bt.add_right(parent, c2)
        with pytest.raises(
            ValueError, match="BinaryNodeObject cannot have more than two children"
        ):
            bt.add_right(parent, c3)
        assert c3._tree_parent is None
        assert c3 not in parent.tree_children

    def test_replace_right_then_left_positions(self):
        """Moving an existing child from right to left reorders tree_children."""
        parent = BinaryNodeObject(value="P")
        a = BinaryNodeObject(value="A")
        b = BinaryNodeObject(value="B")

        parent.right = a
        parent.right = b  # replace right
        assert parent.right is b
        # place a back as left
        parent.left = a
        assert parent.left is a
        # ensure ordering: left index 0 is a, right index 1 is b
        assert parent.tree_children[0] is a
        assert parent.tree_children[1] is b


class TestEdgeCasesAndConsistency:
    """Extra edge and consistency checks."""

    def test_setting_none_on_left_removes_child(self):
        """Setting left to None removes child and clears parent pointer."""
        parent = BinaryNodeObject(value="P")
        child = BinaryNodeObject(value="C")
        parent.left = child
        assert child._tree_parent is parent

        parent.left = None
        assert child._tree_parent is None
        assert child not in parent.tree_children

    def test_setting_none_on_right_removes_child(self):
        """Setting right to None removes child and clears parent pointer."""
        parent = BinaryNodeObject(value="P")
        child = BinaryNodeObject(value="C")
        parent.right = child
        assert child._tree_parent is parent

        parent.right = None
        assert child._tree_parent is None
        assert child not in parent.tree_children

    def test_adding_same_child_as_left_then_right_moves_it(self):
        """If child was left then set as right, right should return it and left be None."""
        parent = BinaryNodeObject(value="P")
        child = BinaryNodeObject(value="C")
        parent.left = child
        parent.right = child

        assert parent.right is child
        assert parent.left is None
        # no duplicates
        assert parent.tree_children.count(child) == 1

    def test_adding_same_child_as_right_then_left_moves_it(self):
        """If child was right then set as left, left should return it and right be None."""
        parent = BinaryNodeObject(value="P")
        child = BinaryNodeObject(value="C")
        parent.right = child
        parent.left = child

        assert parent.left is child
        assert parent.right is None
        # no duplicates
        assert parent.tree_children.count(child) == 1

    def test_no_duplicate_when_setting_right_after_left(self):
        """Setting same object left then right should not leave duplicate entries."""
        parent = BinaryNodeObject(value="P")
        child = BinaryNodeObject(value="C")
        parent.left = child
        parent.right = child
        assert parent.tree_children.count(child) == 1
        assert child._tree_parent is parent
