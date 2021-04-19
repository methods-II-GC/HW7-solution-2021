#!/usr/bin/env python
"""Anagram decoder."""

import argparse
import collections

from typing import DefaultDict, List

import pynini


KeyTable = DefaultDict[str, List[int]]


def get_key(s: str) -> str:
    """Computes the "key" for a given token."""
    return "".join(sorted(s))


def make_key_table(sym: pynini.SymbolTable) -> KeyTable:
    """Creates the key table.

    The key table is a dictionary mapping keys to the index of words which
    have that key.
    """
    table: KeyTable = collections.defaultdict(list)
    for (index, token) in sym:
        key = get_key(token)
        table[key].append(index)
    return table


def make_lattice(tokens: List[str], key_table: KeyTable) -> pynini.Fst:
    """Creates a lattice from a list of tokens.

    The lattice is an unweighted FSA.
    """
    lattice = pynini.Fst()
    # A "string FSA" needs n + 1 states.
    lattice.add_states(len(tokens) + 1)
    lattice.set_start(0)
    lattice.set_final(len(tokens))
    for (src, token) in enumerate(tokens):
        key = get_key(token)
        # Each element in `indices` is the index of an in-vocabulary word that
        # represents a possible unscrambling of `token`.
        indices = key_table[key]
        for index in indices:
            # This adds an unweighted arc labeled `index` from the current
            # state `src` to the next state `src + 1`.
            lattice.add_arc(src, pynini.Arc(index, index, 0, src + 1))
    assert lattice.verify(), "ill-formed lattice"
    return lattice


def decode_lattice(
    lattice: pynini.Fst, lm: pynini.Fst, sym: pynini.SymbolTable
) -> str:
    """Decodes the lattice."""
    lattice = pynini.compose(lattice, lm)
    assert lattice.start() != pynini.NO_STATE_ID, "composition failure"
    # Pynini can join the string for us.
    return pynini.shortestpath(lattice).rmepsilon().string(sym)


def main(args: argparse.Namespace) -> None:
    lm = pynini.Fst.read(args.lm)
    sym = lm.input_symbols()
    assert sym, "no input symbol table found"
    key_table = make_key_table(sym)
    with open(args.input, "r") as source, open(args.output, "w") as sink:
        for line in source:
            tokens = line.rstrip().split()
            lattice = make_lattice(tokens, key_table)
            print(decode_lattice(lattice, lm, sym), file=sink)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lm", required=True, help="path to LM FST")
    parser.add_argument("input", help="path to input scrambled text")
    parser.add_argument("output", help="path for output unscrambled text")
    main(parser.parse_args())
