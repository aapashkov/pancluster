#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""usage: run_pancluster.py BIGSCAPE FAMILY

Run a pancluster analysis for a given BGC FAMILY from a BIGSCAPE results
directory and save it as CSV to stdout. This script will always use the most
recent network found in the BIGSCAPE directory.

example: run_pancluster.py gcfs/ 60 > 60.csv"""

import atexit
import os
import re
import shutil
import subprocess
import sys
import tempfile
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


def main() -> int:
    """Driver code."""

    proteinortho = check_exec("proteinortho")

    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 1

    bigscape = Path(sys.argv[1]).resolve()
    family = sys.argv[2]

    # Setup tmp directory
    tmp = Path(tempfile.mkdtemp(prefix=".tmp", dir=".")).resolve()
    atexit.register(shutil.rmtree, tmp)
    os.chdir(tmp)

    # Get BGCs that belong to input family from the most recent network
    clustering_file = (
        sorted((bigscape / "network_files").glob("*"))[-1] / "mix" /
        "mix_clustering_c0.30.tsv"
    )
    bgcs: list[str] = []
    clustering = pd.read_csv(clustering_file, sep="\t", dtype=str)

    for _, row in clustering.iterrows():
        bgc = row["#BGC Name"]
        if row["Family Number"] != family:
            continue
        if bgc.startswith("BGC0"): # Ignore MIBiG
            continue

        shutil.copyfile(
            str(bigscape / "cache" / "fasta" / f"{bgc}.fasta"), f"{bgc}.faa"
        )
        bgcs.append(f"{bgc}.faa")

    # If only one BGC is found, create a pancluster of only one entry
    if len(bgcs) == 1:
        name = bgcs[0][:-4]
        data = {}

        with open(bgcs[0], encoding="utf8") as handle:
            for line in handle:
                if line.startswith(">"):
                    data[f"c{family}_g{len(data)}"] = {name: 1}

        result = pd.DataFrame(data)
        result.index.name = "bgc"
        result.to_csv(sys.stdout)

        return 0

    # Run Proteinortho
    cmd = [proteinortho, f"-project={family}", "-cpus=1", "-clean", "-singles"]
    subprocess.run(cmd + bgcs, check=True, stdout=sys.stderr)

    # Create output file
    result = pd.read_csv(f"{family}.proteinortho.tsv", sep="\t")
    result = result[result.columns[3:]].transpose()
    result.index = result.index.str[:-4]
    result.index.name = "bgc"
    result.columns = f"c{family}_g" + result.columns.astype(str)
    # A cell with * means absence, else count number of genes
    result = result.applymap(
        lambda cell: 0 if cell == "*" else len(cell.split(","))
    ) # type: ignore

    result.to_csv(sys.stdout)

    return 0


if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
