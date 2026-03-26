#!/usr/bin/env python
"""Simple T9 demo."""

import pynini
from pynini.examples import t9
from pynini.lib import rewrite

SOURCE = "char.txt"
LM = "char.lm"

def lexicon() -> set[str]:
    result = set()
    with open(SOURCE, "r") as source:
        for line in source:
            result.update(line.split())
    return result


my_t9 = t9.T9(lexicon())

lattice = my_t9.decode("737837804726833")

candidates = rewrite.lattice_to_strings(lattice)
print(f"# of candidates: {len(candidates):,}")
print(candidates)

lm = pynini.Fst.read(LM)

lattice @= lm  # This is equivalent to: lattice = lattice @ lm.
print(f"Best candidate: {rewrite.lattice_to_top_string(lattice)}")
