# -*- coding: utf-8 -*-
"""
Created on Sat Aug 26 14:34:26 2023

@author: xande
"""

import tomllib
from os import path



tml_file = r"C:\Users\xande\GitHub\drawpyo\drawpyo\formatting_database\edge_styles.toml"
# tml_file = r"C:\Users\xande\GitHub\drawpyo\drawpyo\shapes\general.toml"

dirname = path.dirname(__file__)
dirname = path.split(dirname)[0]
filename = path.join(dirname, 'shape_libraries\\general.toml')

with open(filename, "rb") as f:
    data = tomllib.load(f)