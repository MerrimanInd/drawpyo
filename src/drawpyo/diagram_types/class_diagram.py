from typing import Optional, Any

from .tree import NodeObject, TreeGroup, TreeDiagram
import inspect


class ClassDiagram(TreeDiagram):
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def create_from_module(cls, mdl, **kwargs: Any) -> None:
        pass

    def process_module(self, mdl, tree, **kwargs: Any) -> None:
        include_private = kwargs.get("include_private", False)

        # Create top object
        mdl = NodeObject(tree=tree, value=mdl.__name__)

        objects_names = dir(mdl)
        for obj_name in objects_names:
            obj = mdl.__dict__[obj_name]
            if obj_name[:2] == "__" and obj_name[-2:] == "__":
                # built_in function
                if include_private:
                    pass
            elif inspect.isclass(obj):
                # handle the MRO
                # obj.__mro__
                pass
            elif inspect.ismethod(obj):
                pass
            elif inspect.isfunction(obj):
                pass
            elif inspect.ismodule(obj):
                self.process_module(obj)
