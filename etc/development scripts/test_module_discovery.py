import drawpyo
# from os import path
import os

# file = drawpyo.File()
# file.file_path = path.join(path.expanduser("~"), "Test Drawpyo Charts")
# file.file_name = "Test Generated Class Diagram.drawio"
# page = drawpyo.Page(file=file)

def standard_lib_names_gen(include_underscored=False):
    standard_lib_dir = os.path.dirname(os.__file__)
    for filename in os.listdir(standard_lib_dir):
        if not include_underscored and filename.startswith('_'):
            continue
        filepath = os.path.join(standard_lib_dir, filename)
        name, ext = os.path.splitext(filename)
        if filename.endswith('.py') and os.path.isfile(filepath):
            if str.isidentifier(name):
                yield name
        elif os.path.isdir(filepath) and '__init__.py' in os.listdir(filepath):
            yield name

def standard_lib_names(include_underscored=False):
    return list(standard_lib_names_gen(include_underscored))

import inspect
import sys

def process_module(module, **kwargs):
    prefix = kwargs.get("print_prefix", "")
    builtins = standard_lib_names()
    
    objects_names = dir(module)
    for obj_name in objects_names:
        if obj_name[:2] == "__" and obj_name[-2:] == "__":
            continue
        
        obj_type = "unknown"
        obj = module.__dict__[obj_name]
        if inspect.isclass(obj):
            # handle the MRO
            # obj.__mro__
            print(f"{prefix}Found class {obj_name}")
            process_module(obj, print_prefix=prefix+"  ")
            pass
        elif inspect.ismethod(obj):
            print(f"{prefix}Found method {obj_name}")
            pass
        elif inspect.isfunction(obj):
            print(f"{prefix}Found function {obj_name}")
            pass
        elif inspect.ismodule(obj) and obj_name not in sys.stdlib_module_names and obj_name != 'path':
            print(f"{prefix}Found module {obj_name}")
            process_module(obj, print_prefix=prefix+"  ")
        else:
            # Have to handle all built-in types
            pass
        pass

process_module(drawpyo)