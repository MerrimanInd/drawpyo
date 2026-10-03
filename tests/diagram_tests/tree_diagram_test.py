import pytest

from drawpyo.diagram_types.tree import NodeObject, TreeDiagram, TreeGroup


class CustomTreeGroup(TreeGroup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.centered_parent = False

    def center_parent(self):
        self.centered_parent = True
        super().center_parent()


def _tree_with_parent_and_child(**kwargs):
    tree = TreeDiagram(**kwargs)
    parent = NodeObject(tree=tree, value="parent")
    child = NodeObject(tree=tree, value="child")
    parent.add_child(child)
    return tree


def test_auto_layout_uses_tree_group_by_default():
    tree = _tree_with_parent_and_child()

    top_group = tree.auto_layout()

    assert isinstance(top_group, TreeGroup)
    assert type(top_group) is TreeGroup


def test_auto_layout_uses_factory_for_every_group():
    groups = []

    def group_factory(*, tree):
        group = CustomTreeGroup(tree=tree)
        groups.append(group)
        return group

    tree = _tree_with_parent_and_child(group_factory=group_factory)
    top_group = tree.auto_layout()

    assert top_group is groups[0]
    assert len(groups) == 3
    assert len({id(group) for group in groups}) == len(groups)
    assert all(isinstance(group, CustomTreeGroup) for group in groups)
    assert all(group.tree is tree for group in groups)
    assert sum(group.centered_parent for group in groups) == 1


def test_tree_diagram_rejects_non_callable_group_factory():
    with pytest.raises(TypeError, match="group_factory must be callable"):
        TreeDiagram(group_factory=None)
