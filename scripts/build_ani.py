#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""usage: build_ani.py FASTA FASTA [FASTA ...]

Create an ANI distance matrix from input FASTA files and print it to stdout in
csv format. Set JOBS environment variable for parallelization.

example: JOBS=10 build_ani.py *.fasta > ani_matrix.csv"""

import itertools
import multiprocessing
import os
import re
import sys
from pathlib import Path
from typing import Tuple, List

import screed
import sourmash
import pandas as pd


def pairwise_ani(files: Tuple[Path, Path]) -> Tuple[str, str, float]:
    """Compute ANI between a pair of genomes."""

    minhashes: List[sourmash.MinHash] = []

    for file in files:
        minhash = sourmash.MinHash(n=0, ksize=31, scaled=1000)
        with screed.open(file) as handle:
            for record in handle:
                minhash.add_sequence(record["sequence"], force=True)
        minhashes.append(minhash)

    ani = minhashes[0].jaccard_ani(minhashes[1]).ani
    if ani is None:
        ani = 0.0

    return files[0].stem, files[1].stem, ani


def main() -> int:
    """Driver code."""

    jobs = int(os.environ.get("JOBS", "1"))

    if len(sys.argv) < 3:
        print(__doc__, file=sys.stderr)
        return 1

    files = sorted([Path(file) for file in sys.argv[1:]])

    # Compute pairwise ANI between every pair of genomes
    pairs = itertools.permutations(files, 2)
    with multiprocessing.Pool(jobs) as pool:
        df = pd.DataFrame(pool.map(pairwise_ani, pairs))

    # Reshape to distance matrix and save to stdout
    df = 1 - df.pivot(index=0, columns=1, values=2).fillna(1.0)
    df.index.name = "accession"
    df.to_csv(sys.stdout)

    return 0


if __name__ == "__main__":
    sys.argv[0] = re.sub(r"(-script\.pyw|\.exe)?$", "", sys.argv[0])
    sys.exit(main())
