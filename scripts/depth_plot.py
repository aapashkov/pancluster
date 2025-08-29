#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""usage: depth_plot.py COORD CONTIG REFERENCE READ [READ1] [READ2]

Plot depth of a CONTIG from a REFERENCE genome by mapping READs to it and print
it to stdout in svg format. By default, READ are Nanopore reads, but if
READ1 and/or READ2 are provided, READ is considered Nanopore while READ1 and/or
READ2 is considered Illumina paired-end reads. If setting COORD to a number,
a dashed vertical line will be drawn on that position, if set to NaN, it will
be ignored.

example: depth_plot.py scaffold_1 IraGTOF11.fna f11_nanopore.fq.gz > depth.svg"""

import atexit
import io
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


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


def get_depth(
    contig: str,
    ref: str,
    reads: List[str],
    minimap2: str = "minimap2",
    samtools: str = "samtools",
):
    """Compute depth of reads mapped to reference."""

    # Setup tmp directory
    tmp = Path(tempfile.mkdtemp(prefix=".tmp", dir="."))
    atexit.register(shutil.rmtree, tmp)

    # List of commands to run
    preset = "sr" if len(reads) > 1 else "map-ont"
    cmds = [
        [minimap2, "-ax", preset, ref] + reads,
        [samtools, "view", "-bS", "-"],
        [samtools, "sort", "-T", tmp/"samtools", "-"],
        [samtools, "depth", "-a", "-"]
    ]

    # Create a pipeline
    procs: List[subprocess.Popen] = []
    for cmd in cmds:
        if procs:
            proc = subprocess.Popen(
                cmd, stdin=procs[-1].stdout, stdout=subprocess.PIPE
            )
        else:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)

        if procs:
            if procs[-1].stdout is not None:
                procs[-1].stdout.close()

        procs.append(proc)

    output: bytes = procs[-1].communicate()[0]
    depth = pd.read_csv(io.BytesIO(output), sep="\t", header=None)
    return depth[depth[0] == contig][2].to_numpy()


def bin_array(array: np.ndarray, m: int):
    """Reduce an array into m bins by summing consecutive elements."""

    edges = np.linspace(0, len(array), m + 1, dtype=int)
    return np.add.reduceat(array, edges[:-1]), edges


def main() -> int:
    """Driver code."""

    minimap2 = check_exec("minimap2")
    samtools = check_exec("samtools")

    if len(sys.argv) < 5 or len(sys.argv) > 7:
        print(__doc__, file=sys.stderr)
        return 1

    coord = float(sys.argv[1])
    contig = sys.argv[2]
    ref = sys.argv[3]
    reads = sys.argv[4:]
    depth = get_depth(contig, ref, [reads[0]], minimap2, samtools)
    n_bars = 1_000

    if len(reads) > 1:
        depth += get_depth(contig, ref, reads[1:], minimap2, samtools)

    bins, edges = bin_array(depth, n_bars)

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.bar(
        range(n_bars), bins, width=1.0, lw=0, align="edge",
        color="silver"
    )
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_yscale("log")
    ax.set_xlabel(contig)
    ax.set_ylabel("profundidad")
    ax.set_xlim(0, n_bars)
    xticks = ax.get_xticks().astype(int)
    ax.set_xticks(xticks, [f"{num:.1f}Mbp" for num in edges[xticks] / 1e6])

    if not np.isnan(coord):
        mapped_coord = coord * n_bars / len(depth)
        ax.axvline(mapped_coord, ls="--", color="red", lw=1)

    fig.tight_layout()
    fig.savefig(sys.stdout, format="svg", transparent=True)

    return 0


if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
