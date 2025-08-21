#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""usage: build_ani.py FASTA FASTA [FASTA ...]

Create an ANI distance matrix from input FASTA files and print it to stdout in
csv format. Set CPUS environment variable for parallelization.

example: CPUS=10 build_ani.py *.fasta > ani_matrix.csv"""

import functools
import itertools
import multiprocessing
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

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


def ani(pair: tuple[Path, Path], fastani: str = "fastANI") -> tuple[str, str, float]:
    """Compute ANI from a pair of files."""

    stem1, stem2 = [path.stem for path in pair]
    cmd = [fastani, "-q", pair[0], "-r", pair[1], "-o", "/dev/stdout"]

    return stem1, stem2, 100 - float(
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE)
        .stdout.decode().split("\t")[2]
    )


def main() -> int:
    """Driver code."""

    cpus = int(os.environ.get("CPUS", "1"))

    # Check executable dependencies
    fastani = check_exec("fastANI")

    if len(sys.argv) < 3:
        print(__doc__, file=sys.stderr)
        return 1

    files = [Path(file) for file in sys.argv[1:]]
    stems = [file.stem for file in files]

    # Compute pairwise ANI between every pair of genomes
    func = functools.partial(ani, fastani=fastani)
    pairs = itertools.permutations(files, 2)

    with multiprocessing.Pool(cpus) as pool:
        df = pd.DataFrame(pool.map(func, pairs))

    # Reshape to distance matrix and compute mean of ANI values
    df = pd.pivot_table(df, index=0, columns=1, values=2).fillna(0)
    df = (df + df.T) / 2
    df = df.loc[stems, stems]
    df.index.name = "genome"
    df.to_csv(sys.stdout)

    return 0


if __name__ == "__main__":
    sys.argv[0] = re.sub(r"(-script\.pyw|\.exe)?$", "", sys.argv[0])
    sys.exit(main())
