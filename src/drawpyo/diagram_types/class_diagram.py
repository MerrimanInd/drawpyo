from .tree import NodeObject, TreeGroup, TreeDiagram
import inspect


class ClassDiagram(TreeDiagram):
    def __init__(self):
        super().__init__()

    @classmethod
    def create_from_module(cls, module, **kwargs):
        pass

    def process_module(module, tree, **kwargs):
        include_private = kwargs.get("include_private", False)

        # Create top object
        module = NodeObject(tree=tree, value=module.__name__)

        objects_names = dir(module)
        for obj_name in objects_names:
            obj = module.__dict__[obj_name]
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
                process_module(obj)
