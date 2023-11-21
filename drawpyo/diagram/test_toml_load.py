# -*- coding: utf-8 -*-
"""
Created on Sat Aug 26 14:34:26 2023

@author: xande
"""

from sys import version_info
from os import path



tml_file = r"C:\Users\xande\GitHub\drawpyo\drawpyo\formatting_database\edge_styles.toml"
# tml_file = r"C:\Users\xande\GitHub\drawpyo\drawpyo\shapes\general.toml"

dirname = path.dirname(__file__)
dirname = path.split(dirname)[0]
filename = path.join(dirname, 'shape_libraries\\general_w_inherit.toml')



if version_info.minor < 11:
    import toml
    data = toml.load(filename)

else:
    import tomllib
    with open(filename, "rb") as f:
        data = tomllib.load(f)

processed_data = {}
for obj in data.values():
    if "inherit" in obj:
        obj.update(data[obj["inherit"]])
