#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""usage: build_pangenome.py DIR SUFFIX OUTPREFIX

Recursively search for faa files in DIR containing SUFFIX and build a pangenome
saved to OUTPREFIX. Two files are produced: OUTPREFIX.tsv containing a presence
absence matrix, and OUTPREFIX.json listing gene names referred by each gene
family in OUTPREFIX.tsv. Use JOBS environment variable for parallelization.

example: build_pangenome.py proteins/ .proteins.fa results/pangenome"""

import atexit
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pandas as pd


def remove_suffix(string: str, suffix: str) -> str:
    """Return a str with the given suffix string removed if present.

    If the string ends with the suffix string and that suffix is not empty,
    return string[:-len(suffix)]. Otherwise, return a copy of the original
    string."""

    if string.endswith(suffix):
        return string[:-len(suffix)]
    return string


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
    jobs = int(os.environ.get("JOBS", "1"))

    if len(sys.argv) != 4:
        print(__doc__, file=sys.stderr)
        return 1

    indir = Path(sys.argv[1]).resolve()
    suffix = sys.argv[2]
    outprefix = Path(sys.argv[3]).resolve()
    if not outprefix.parent.exists():
        print(f"error: {outprefix.parent} does not exist", file=sys.stderr)
        return 1

    # Setup tmp directory
    tmp = Path(tempfile.mkdtemp(prefix=".tmp", dir=".")).resolve()
    atexit.register(shutil.rmtree, tmp)
    os.chdir(tmp)

    # Recursively search for files with provided suffix and create symlinks
    files: list[str] = []
    for src in indir.rglob(f"*{suffix}"):
        dst = f"{remove_suffix(src.name, suffix)}.faa"
        os.symlink(str(src), dst)
        files.append(dst)

    # Run proteinortho
    cmd = [
        proteinortho, "-project=pangenome", f"-cpus={jobs}", "-clean",
        "-singles"
    ]
    subprocess.run(cmd + files, check=True, stdout=sys.stderr)

    # Open proteinortho output
    df = pd.read_csv("pangenome.proteinortho.tsv", sep="\t")

    # Filter out non-singleton families with very low connectivity
    df = df[(df["Alg.-Conn."] >= 0.01) | (df["Alg.-Conn."] == 0)]
    df.reset_index(drop=True, inplace=True)

    # Output wrangling
    df = df[df.columns[3:]]
    df.columns = df.columns.str[:-4]
    df.index = "g" + df.index.astype(str)
    df: pd.DataFrame = df.applymap(
        lambda x: [] if x == "*" else x.split(",")
    ) # type: ignore

    # Create json output
    mapping = {
        fam: row[row.map(bool)].to_dict() for fam, row in df.iterrows()
    }
    with open(f"{outprefix}.json", "w", encoding="utf8") as handle:
        json.dump(mapping, handle, indent=2)

    # Create csv output
    df: pd.DataFrame = df.applymap(bool).astype(int).T.sort_index() # type: ignore
    df.index.name = "accession"
    df.to_csv(f"{outprefix}.csv")

    return 0


if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
