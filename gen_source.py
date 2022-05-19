#!/usr/bin/env python3

import toml
from typing import List
from pprint import pformat, pprint
import itertools
import numpy as np


def get_veclevel(stype, iset):
    valsizes = {'float': 4*8, 'double': 8*8}
    regsizes = { 'avx2': 256, 'avx512': 512}

    veclevel = 1 if iset == 'x86_64' else regsizes[iset] // valsizes[stype]

    return veclevel


class Function:
    """hi."""

    def __init__(self, calltemplate, implements, stype, veclevel, domain):
        """hi."""
        self.calltemplate: str = calltemplate
        self.implements: str = implements
        self.stype: str = stype
        self.veclevel = veclevel
        self.domain: List[float] = config.get('domain', [0.0, 1.0])


    def __repr__(self):
        """Prints this object."""
        return pformat(vars(self))

    def gen_map_elem(self):
        """Generates map, lambda expression pairs in C++ to call this function"""
        if self.veclevel == 1:
            template = """{{"{0}", scalar_func_map<{1}>([]({1} x) -> {1} {{ return {3}; }})}}"""
        else:
            template = """{{"{0}", vec_func_map<{2}, {1}>([]({2} x) -> {2} {{ return {3}; }})}}"""

        vectype = "Vec{}{}".format(self.veclevel, self.stype[0])

        map_elem = template.format(self.implements, self.stype, vectype, self.calltemplate)
        return map_elem


config = toml.load("funcs.toml")
domains = config.pop('domains')

funcs = []
for lname, lconfig in config.items():
    types = lconfig.pop('types')
    instructions = lconfig.pop('instructions')

    for fname, calltemplate in lconfig['calltemplates'].items():
        for stype, iset in itertools.product(types, instructions):
            veclevel = get_veclevel(stype, iset)
            mapname = "funs_{}x{}".format(stype[0], veclevel)
            func = Function(calltemplate, fname, stype, veclevel, domains.get(fname, [0.0, 1.0]))
            funcs.append(func)


for func in funcs:
    print(func.gen_map_elem())
