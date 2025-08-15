#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""usage: phylogenetic_tree.py FASTA

Create a phylogenetic tree from sequences in FASTA file and print it to stdout
in SVG format.

example: phylogenetic_tree.py sequences.fasta > tree.svg"""

import atexit
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


import phytreeviz
from Bio import SeqIO
from Bio.Phylo import Newick, NewickIO


def check_exec(*executables: str):
    """Find and return an executable from input, showing error if none is
    found."""

    choice = None
    for executable in executables:
        if shutil.which(executable) is not None:
            choice = executable
            break
    if choice is None:
        print(
            f"error: could not find an executable for '{executables[0]}'",
            file=sys.stderr
        )
        sys.exit(1)
    else:
        return choice


def main() -> int:
    """Driver code."""

    # Check executable dependencies
    muscle = check_exec("muscle3", "muscle")
    iqtree = check_exec("iqtree2", "iqtree")
    gblocks = check_exec("Gblocks")

    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 1

    file = Path(sys.argv[1])
    tmp = Path(tempfile.mkdtemp())
    atexit.register(shutil.rmtree, tmp)

    # Get outgroup from first record in FASTA
    with open(file) as handle:
        outgroup = next(SeqIO.parse(handle, "fasta")).id

    # Get a mapping of identifiers to full names
    with open(file) as handle:
        names = {
            rec.id: rec.description for rec in SeqIO.parse(handle, "fasta")
        }

    # Align sequences
    subprocess.run(
        [muscle, "-in", file, "-out", tmp/"aln.fa"],
        check=True,
        stdout=sys.stderr
    )

    # Perform alignment trimming, ignore check as exit code of 1 is common
    subprocess.run([gblocks, tmp/"aln.fa", "-t", "d"], stdout=sys.stderr)

    # Build tree
    subprocess.run(
        [
            iqtree, "-s", tmp/"aln.fa-gb", "-m", "TEST",
            "-B", "10000", "-o", outgroup
        ],
        check=True,
        stdout=sys.stderr
    )

    # Load tree for plotting
    with open(tmp/"aln.fa-gb.treefile") as handle:
        tree = next(NewickIO.parse(handle))
    
    # Update names with full names
    for clade in tree.get_terminals():
        clade: Newick.Clade
        clade.name = names[clade.name]

    # Create tree visualization
    tv = phytreeviz.TreeViz(tree, height=0.4, width=6)
    tv.show_confidence(size=12, ymargin_ratio=0.1)
    tv.show_scale_bar(text_size=12)
    fig = tv.plotfig()
    fig.savefig(sys.stdout, format="svg", transparent=True)

    return 0


if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
